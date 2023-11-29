import os
import subprocess
import requests

# Set this to True to log all the code and globals being executed
LOG_ALL_CODE = False
ALWAYS_BE_UNSAFE = False

LOGGING_API_EP = 'https://api.deltafunctions.io/v1/internal/runtime_kit/{deployment_id}/safe_exec'
class SafeExecException(Exception):
	pass

def safe_exec_log_error_to_api(pid, error_message):
	error_data = {'pid': pid, 'error_message': error_message}
	try:
		response = requests.post(LOGGING_API_EP, json=error_data)
		if response.ok:
			print("Error logged to API successfully")
		else:
			print(f"Failed to log error to API. Status code : {response.status_code}")
			print("API Response : ", response)
	except Exception as ex:
		print("Exception while logging error to API : ", str(ex))


def safe_excec(exe_file, globals_dict, files=None, python_path=None, limit_overrides_context=None, slug=None, extra_files=None):
	try:
		# capture both the stdout and stderr
		result = subprocess.run(exe_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

		if result.returncode == 0:
			print("Command executed successfully")
		else:
			safe_exec_log_error_to_api(f"Error occured:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
	except Exception as ex:
		print(f"Exception : {ex}")

def checkpoint_process(pid, dump_file):
	try:
		result = subprocess.run(f'sudo criu {dump_file} -t {pid} --shell-job', shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

		if result.returncode == 0:
			print(f"Process with PID {pid} Saved Successfully")
		else:
			print(f"Process Checkpointing Failed with return code : {result.returncode}")
			print(result.stderr)
	except subprocess.CalledProcessError as e:
		print(f"Command failed with return code : {e.returncode}")
		print(e.stderr)
	except Exception as ex:
		print(f"Exception : {ex}")

def restore_process_ckpt(pid, dump_file):
	try:
		result = subprocess.run(f'sudo criu restore -d -t {pid} --shell-job --tcp-established --pre-dump-dir {dump_file}', shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

		if result.returncode == 0:
			print(f'Process witj PID {pid} Restored Successfully')
		else:
			print(f"Process Restore Failed with return code : {result.returncode}")
			print(result.stderr)
	except subprocess.CalledProcessError as e:
		print(f"Command failed with return code : {e.returncode}")
		print(e.stderr)
	except Exception as ex:
		print(f"Exception : {ex}")

