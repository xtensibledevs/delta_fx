

# Set this to True to log all the code and globals being executed
LOG_ALL_CODE = False
ALWAYS_BE_UNSAFE = False

class SafeExecException(Exception):
	pass


def safe_excec(code, globals_dict, files=None, python_path=None, limit_overrides_context=None, slug=None, extra_files=None):
	pass