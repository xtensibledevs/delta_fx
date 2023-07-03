# RLimits for processes, used to create a drop instance

import os
import resource

def set_process_limits(rlimits):
	''' Set the limits on the process, to be used first in a child process '''
	os.setsid()
	for limit in rlimits:
		try:
			resources.setrlimit(limit.name, limit.value)
		except Exception as exc:
			cloudlogger.error("{}-{}-{}".format(limit.name, limit.value, exc))
			logger.error("{}-{}-{}".format(limit.name, limit.value, exc))

def get_process_limits(resources):
	''' Get the limits of an running child process '''
	rlimits = {}
	for res in resources:
		rlimits[res] = resources.getrlimit(res)
	return rlimits

