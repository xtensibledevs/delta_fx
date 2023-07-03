

# Set this to True to log all the code and globals being executed
LOG_ALL_CODE = False
ALWAYS_BE_UNSAFE = False

class SafeExecException(Exception):
	pass


def safe_excec(code, globals_dict, files=None, python_path=None, limit_overrides_context=None, slug=None, extra_files=None):
	''' Execute code as `exec` does, but safely 
		
		`code` : String od python code. 
		`globals_dict` : globals during execution
		`files` : list of file paths, files or directories. To be 
		copied into the temp directory for execution.
	'''

	the_code = []
	files = list(files or ())
	extra_files = extra_files or ()
	python_path = python_path or ()

	extra_names = {name for name, contents in extra_files}

	the_code.append(textwrap.dedent(
		"""
		import sys
		import six
		try:
			import simplejson as json
		except ImportError:
			import json
		"""
		"""
		class DevNull(object):
			def write(self, *args, **kwargs):
				pass

			def flush(self, *args, **kwargs):
				pass
		sys.stdout = DevNull()

		"""
		"""
		code, g_dict = json.load(sys.stdin)
		"""
	))