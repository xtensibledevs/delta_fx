# The Resource limits for drop, to be enforced

import resource

class CORELimit:
	# the max size of the core file that the process can create
	def __init__(self, value):
		self.name = 'CORE'
		self.value = value

class CPULimit:
	# if this exceeds, SIGXCPU is sent to the process
	def __init__(self, value):
		self.name = 'CPU'
		self.value = value

class FSIZELimit:
	# max size of a file the process can create
	def __init__(self, value):
		self.name = 'FSIZE'
		self.value = value

class DATALimit:
	# process heap size limit
	def __init__(self, value):
		self.name = 'DATA'
		self.value = value

class STACKLimit:
	# process stack size limit
	def __init__(self, value):
		self.name = 'STACK'
		self.value = value

class RSSRLimit:
	# max resident set size limit

	def __init__(self, value):
		self.name = 'RSS'
		self.value = value

class NRPOCLimit:
	# max no of subprocesses limit

	def __init__(self, value):
		self.name = 'NRPOC'
		self.value = value

class NOFILELimit:
	# no of open file descriptors limit
	def __init__(self, value):
		self.name = 'NOFILE'
		self.value = value

class OFILELimit:
	# max address space which may be locked in memory
	def __init__(self, value):
		self.name = 'OFILE'
		self.value = value

class MEMLOCKLimit:
	# max address space which may be locked in memory
	def __init__(self, value):
		self.name = 'MEMLOCK'
		self.value = value

class VMEMLimit:
	# max address space which the process may occupy
	def __init__(self, value):
		self.name = 'VMEM'
		self.value = value

class MSGQUEUELimit:
	# max no of bytes that can be allocated for POSIX messages queues
	def __init__(self, value):
		self.name = 'MSGQUEUE'
		self.value = value

class ASLimit:
	# The ceiling for the process's nice level
	def __init__(self, value):
		self.name = 'AS'
		self.value = value

class NICELimit:
	# the ceiling of the real-time priority
	def __init__(self, value):
		self.name = 'NICE'
		self.value = value

class RTPRIOLimit:
	# the time-limit in microsecs that a process can spend under realtime scheduling
	def __init__(self, value):
		self.name = 'RTPRIO'
		self.value = value

class RTTIMELimit:
	def __init__(self, value):
		self.name = 'RTTIME'
		self.value = value

class SIGPENDINGLimit:
	sock_buf_rlim = None
	def __init__(self, value):
		self.name = 'SIGPENDING'
		self.value = value

class SBSIZELimit:
	def __init__(self, value):
		self.name = 'SBSIZE'
		self.value = value

class SWAPLimit:
	def __init__(self, value):
		self.name = 'SWAP'
		self.value = value

class NPTSLimit:
	def __init__(self, value):
		self.name = 'NPTS'
		self.value = value

class KQUEUESLimit:
	def __init__(self, value):
		self.name = 'KQUEUES'
		self.value = value

class PROXYLimit:
	def __init__(self, value):
		self.name = 'PROXY'
		self.value = value


DEFAULT_LIMITS = [
	CPULimit(1),
	RTTIMELimit(1),
	VMEMLimit(0),
	FSIZELimit(0),
	NRPOCLimit(15),
	PROXYLimit(None),
]