
import ast
from logging import getLogger
import os
import os.path
import subprocess
import sys
import time

import six

from .subproc import run_subprocess
from xcloud.utils import CloudLogger

# Cloud logger, local logger
cloudlogger = CloudLogger(SERVICE_BLACKSMITH_DROPPER, __name__)
logger = getLogger("dropper")

def serialize_out(val):
	return repr(val)

def serialize_in(val):
	return serialize_out(val).encode('utf-8')

def deserialize_in(ustr):
	return ast.literal_eval(ustr)

def deserialize_out(bstr):
	return deserialize_in(bstr.decode('utf-8'))


# Client code, runs in the parent Drop instance process

def run_sp_thru_proxy(*args, **kwargs):
	last_exception = None
	for _tries in range(3):
		try:
			proxy = get_proxy()

			# Write the args and kwargs to the proxy process
			proxy_stdin = serialize_in((args, kwargs))
			proxy.stdin.write(proxy_stdin + b'\n')
			proxy.stdin.flush()

			# read the result from the proxy. This blocks until the process is
			# done
			proxy_stdout = proxy.stdout.readline()
			if not proxy_stdout:
				raise Exception("Proxy process died unexpectedly!")
			status, stdout, stderr, log_calls = deserialize_out(proxy_stdout.rstrip())

			# Write all the log messages to the log, and return
			for level, msg, args in log_calls:
				logger.log(level, msg, *args)
			return status, stdout, stderr

		except Exception:
			logger.exception("Proxy process failed")
			time.sleep(.001)
			last_exception = sys.exc_info()
			continue

	if last_exception:
		six.reraise(*last_exception)

PROXY_PROCESS = None

def get_proxy():
	global PROXY_PROCESS

	if PROXY_PROCESS is not None:
		status = PROXY_PROCESS.poll()
		if status is not None:
			logger.info("Dropper proxy process (PID %d) ended with status code %d", PROXY_PROCESS.pid, status)
			PROXY_PROCESS = None

		if PROXY_PROCESS is None:
			root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
			proxy_main_py = os.path.join(root, "proxy_main.py")

			log_level = logger.getEffectiveLevel()
			cmd = [sys.executable, '-u', proxy_main_py, str(log_level)]

			PROXY_PROCESS = sp.Popen(args=cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
			logger.info("Started Dropper proxy process (PID %d)", PROXY_PROCESS.pid)
			return PROXY_PROCESS