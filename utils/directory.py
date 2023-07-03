
import contextlib
import os
import shutil
import tempfile

@contextlib.contextmanager
def temp_dir():
	''' A content manager to make a use a temp directory 
		The directory will be removed when done
	'''
	temp_dir = tempfile.mkdtemp(prefix="blksmth-codrr-")
	try:
		yield temp_dir
	finally:
		shutil.rmtree(temp_dir)

@contextlib.contextmanager
def ch_dir(new_dir):
	''' A context manager to change the directory, and then change it back '''
	old_dir = os.getcwd()
	os.chdir(new_dir)
	try:
		yield new_dir
	finally:
		os.chdir(old_dir)