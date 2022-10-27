import glob
import uuid
import os
from dreamconsts import *

def get_generated_images(session_id):
	return sorted(glob.glob(f"{GENERATED_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

def get_uploaded_images(session_id):
	return sorted(glob.glob(f"{UPLOADS_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

def get_upscaled_images(session_id):
	return sorted(glob.glob(f"{UPSCALE_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

def get_models_list():
	return glob.glob(f"{MODELS_FOLDER}/*")

def get_hashes(file_hashes, image_type):
	return sorted( [ k for k in file_hashes.keys() if file_hashes[k]['type'] == image_type], key = lambda k: file_hashes[k]['ctime'], reverse=True )

def get_uploaded_hashes(session_info):
	pass

def make_fileinfo(filename, type):
	if (not os.path.exists(filename)):
		return {}

	return {
		'filename' : filename,
		'type' : type,
		'ctime' : os.path.getctime(filename),
		#'atime' : os.path.getatime(filename),
		#'mtime' : os.path.getmtime(filename),
		#'size' : os.path.getsize(filename)
	}

def fetch_and_resize(path, image):
	pass

def get_filehashes_for_session(session_info):
	session_id = session_info['session_id']
	file_hashes = session_info['file_hashes']
	new_hashes = {}

	filenames_to_hashes = { v['filename'] : k for k, v in file_hashes.items() }

	for filename in get_generated_images(session_id):
		if (filename not in filenames_to_hashes):
			print(f"New File: {filename}")
			new_uuid = str(uuid.uuid4())
			new_hashes[new_uuid] = make_fileinfo(filename, 'generated')
		else:
			old_uuid = filenames_to_hashes[filename]
			new_hashes[old_uuid] = file_hashes[old_uuid]

	for filename in get_uploaded_images(session_id):
		if (filename not in filenames_to_hashes):
			print(f"New File: {filename}")
			new_uuid = str(uuid.uuid4())
			new_hashes[new_uuid] = make_fileinfo(filename, 'uploaded')
		else:
			old_uuid = filenames_to_hashes[filename]
			new_hashes[old_uuid] = file_hashes[old_uuid]
	return new_hashes

'''
'sessions' -> {
	'session_id_1' -> {
		'file_hashes' -> {
			'uuid' -> {
				'filename' : filename,
				'ctime' : os.path.getctime(filename),
				'atime' : os.path.getatime(filename),
				'mtime' : os.path.getmtime(filename),
				'size' : os.path.getsize(filename)
			}, ...
		}
	},
	'session_id_2' -> { ... },
	'session_id_3' -> { ... },
}
'''