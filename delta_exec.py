

import os
import os.path
import resource
import shutil
import sys

from .proxy import run_sp_thru_proxy
from .resource_limit import DEFAULT_LIMITS

from logging import getLogger
from xcloud.util import CloudLogger

# Local and Cloud Logger
local_logger = getLogger(__name__)
cloudlogger = CloudLogger(SERVICE_BLACKSMITH_DROPPER, __name__)

LIMITS = DEFAULT_LIMITS.copy()

LIMIT_OVERRIDES = {}

# Map from abstract command name to a list of command-line pieces, such as 
# sp.Popen wants
COMMANDS = {}

def configure(command, bin_path, user=None):
	''' Configure command for the dropper to use '''
	cmd_argv = [bin_path]
	if command == "python":
		cmd_argv.extend(['-E', '-B'])

	COMMANDS[command] = {
		# the start of the command line argument
		'cmdline_start': cmd_argv,
		# the user to run this program
		'user': user
	}

def is_configured(command):
	return command in COMMANDS

# By default, look where out current Python runtime is, and maybe there's a 
# py-sandbox alongside. Only do this if running in a virtualenv
running_in_venv = {
	hasattr(sys, 'real_prefix') or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
}

if running_in_venv:
	dropper_user = getUser('DROPPER_TEST_USER')
	dropper_env = getEnv('DROPPER_TEST_ENV')
	if dropper_env and dropper_user:
		configure("python", f"{dropper_env}/bin/python", dropper_user)
	# fallback to defaults
	elif os.path.isdir(sys.prefix + "-dropper"):
		configure("python", sys.prefix + "-dropper/bin/python", "dropper")


def set_limit(limit_name, value):
	''' Set a limit for sandboxed process '''
	LIMITS[limit_name] = value

def get_effective_limits(overrides_ctx=None):
	''' Calculate the effective limits dictionary '''
	overrides = LIMIT_OVERRIDES.get(overrides_ctx, {}) if overrides_ctx else {}
	return {**LIMITS, **overrides}

def override_limit(limit_name, value, limit_override_context):
	''' Override a rlimit for a `drop`, in the context of the `drop` '''
	if limit_name == 'PROXY' and LIMITS["PROXY"] != value:
		logger.error('Tried to override the value of PROXY to %s, Overriding proxy on a pre-context basis is not permitted. Will use golbal-configured values instead: %s'. value, LIMITS['PROXY'])
		return
	if limit_override_context not in LIMIT_OVERRIDES:
		LIMIT_OVERRIDES[limit_override_context] = {}
	LIMIT_OVERRIDES[limit_override_context][limit_name] = value

class DropperExecResult:
	''' A passive object for us to return from dropper instance '''
	def __init__(self):
		self.stdout = self.stderr = self.status = None

def drop_code(command, code=None, files=None, extra_files=None, argv=None, stdin=None, limit_overrides_context=None, slug=None):
	''' Run code in a drop instance 
		
		command : the program command which is to be run
		code : the string containing the code to run
		files : list of file paths, they are all copied to the dropper instance
		Not that no check is made here that the files don't contain sensitive 
		info.
	'''

	if not is_configured(command):
		raise Exception("dropper instance needs to be configured for %r" % command)

	# We make a temp dir to serve as the home dir of the drop instance
	with temp_dir() as homedir:
		# make dir readable by other users
		os.chmod(homedir, 0o775)
		# make a subdir to use for temp files, world-writeable so that we
		# sandbox use can write to it
		tmptmp = os.path.join(homedir, "tmp")
		os.mkdir(tmptmp)
		os.chmod(tmptmp, 0o777)

		argv = argv or []

		# All the supporting files are copied into our directory
		for filename in files or ():
			dest = os.path.join(homedir, os.path.basename(filename))
			if os.path.islink(filename):
				os.symlink(os.readlink(filename), dest)
			elif os.path.isfile(filename):
				shutil.copy(filename, homedir)
			else:
				shutil.copytree(filename, dest, symlinks=True)

		# create the main file
		if code:
			with open(os.path.join(homedir, "drop_code"), "wb") as drop:
				code_bytes = bytes(code, 'utf-8')
				drop.write(code_bytes)

			argv = ["drop_code"] + argv

		# Create extra files requested by the caller
		for name, content in extra_files or ():
			with open(os.path.join(homedir, name), "wb") as extra:
				extra.write(content)

		cmd = []
		rm_cmd = []

		# Build the command to run
		user = COMMANDS[command]['user']
		if user:
			cmd.extend(['sudo', '-u', user])
			rm_cmd.extend(['sudo', '-u', user])

		# Point TMPDIR at out temp directory
		cmd.extend(['TMPDIR=tmp'])
		# Start with the command line dictated by 'python' or whatever
		cmd.extend(COMMANDS[command]['cmdline_start'])

		# Add the code-specific command line pieces
		cmd.extend(argv)

		# Determine effective resource limits
		effective_limits = get_effective_limits(limit_override_context)
		if slug:
			log.info("Preparing to execute drop code %r (overrides context=%r, resource limits=%r).", slug, limit_override_context, effective_limits)

		# use the configuration and maybe an env variable to determine
		# whether to use a proxy process
		use_proxy = effective_limits['PROXY']
		if use_proxy is None:
			use_proxy = int(os.environ.get('DROP_PROXY', '0'))
		if use_proxy:
			run_subprocess = run_sp_thru_proxy
		else:
			run_subprocess = run_sp

		if stdin:
			stdin = bytes(stdin, 'utf-8')

		# Run the subprocess
		status, stdout, stderr = run_subprocess(cmd=cmd, cmd=homedir, env={}, slug=slug, stdin=stdin, realtime=effective_limits['REALTIME'], rlimits=create_rlimits(effective_limits),)

		result = DropperExecResult()
		result.status = status
		result.stdout = stdout
		result.stderr = stderr

		rm_cmd.extend([
			'/usr/bin/find', tmptmp,
			'-mindepth', '1', '-maxdepth', '1',
			'-exec', 'rm', '-rf', '{}', ';'
		])

		# run the rm cmd subprocess
		run_subprocess(rm_cmd, cwd=homedir)

	return result


def create_rlimits(effective_limits):
	''' Create a list of resource limits for out drop instance '''
	rlimits = []
	nproc = effective_limits['NPROC']
	if nproc:
		rlimits.append((resource.RLIMIT_NPROC, (nproc, nproc)))

	# CPU seconds, not wall clock time
	cpu = effective_limits['CPU']
	if cpu:
		rlimits.append((resource.RLIMIT_CPU, (cpu, cpu + 1)))

	vmem = effective_limits['VMEM']
	if vmem:
		rlimits.append((resource.RLIMIT_AS, (vmem, vmem)))

	fsize = effective_limits['FSIZE']
	rlimits.append((resource.RLIMIT_FSIZE, (fsize, fsize)))

	return rlimits

