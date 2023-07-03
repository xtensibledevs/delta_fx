
import functools
import os
import resource
import subprocess as sp
import threading
import time

from logging import getLogger
from xcloud.utils import CloudLogger

from .resource_limit.rlimits_utils import set_process_limits, get_process_limits

# Local and cloud logger
logger = getLogger(__name__)
cloudlogger = CloudLogger(SERVICE_BLACKSMITH_DROPPER, __name__)

def run_subprocess(cmd, stdin=None, cwd=None, env=None, rlimits=None, realtime=None, slug=None):
	''' A helper to run limited subprocess 
		`cmd`, `cwd` and `env` are the one that `subprocess.Popen` expects
		`stdin` - is the data to write to the stdin of the subprocess
		`rlimits` - set of tuples, the arguments to pass to `resource.setrlimit`
		to set limits on the process
		`realtime` - is the number of seconds to limit the exec of the process
		`slug` - is the short identifier for use in log messages
	'''

	subproc = sp.Popen(cmd, cwd=cwd, env=env, preexec_fn=functools.partial(set_process_limits, rlimits or ()), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

	if slug:
		logger.info("Executed process %s in %s, with PID %s", slug, cwd, subproc.pid)
	if realtime:
		killer = ProcessKillerThread(subproc, limit=realtime)
		killer.start()

	stdout, stderr = subproc.communicate(stdin)
	return subproc.returncode, stdout, stderr
