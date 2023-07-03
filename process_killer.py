
import time
import subprocess as sp
import os

from logger import getLogger
from xcloud.utils import CloudLogger

logger = getLogger(__name__)
cloudlogger = CloudLogger(SERVICE_BLACKSMITH_DROPPER, __name__)

class ProcessKillerThread(threading.Thread):
	''' A thread looking out to kill expired processes after a given time limit
	'''
	def __init__(self, subproc, limit):
		super().__init__()
		self.subproc = subproc
		self.limit = limit

	def run(self):
		start = time.time()
		while (time.time() - start) < self.limit:
			time.sleep(.25)
			if self.subproc.poll() is not None:
				return

		if self.subproc.poll() is None:
			#  subproc.kill can't be used because we launched the subproc with 
			# sudo
			pgid = os.getpgid(self.subproc.pid)
			logger.warning("Killing process %r (group %r), ran too long: %.1fs", self.subproc.pid, pgid, time.time() - start)
			cloudlogger.warning("Killing process %r (group %r), ran too long: %.1fs", self.subproc.pid, pgid, time.time() - start)
			sp.call(["sudo", "pkill", "-9", "-g", str(pgid)])
