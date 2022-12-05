import glob
import os
from PIL import Image
from dream_consts import GENERATED_FOLDER, PLAYGROUND_FOLDER, THUMBNAILS_FOLDER, WORKBENCH_FOLDER
from file_info import file_info

class file_manager():

	def __init__(self, session_id):
		self._fileinfos = []
		self._fileinfos_byhash = {}
		self._fileinfos_byfilename = {}
		self._session_id = session_id

	def update_fileinfos(self, clean=False, refresh=False):
		# Clean out everything and rehash
		print(f"Updaing all file information for {self._session_id}")
		if (clean):
			self._fileinfos = []
			self._fileinfos_byhash = {}
			self._fileinfos_byfilename = {}

		# Check for new files and add them
		if (refresh or clean):
			# Get generated images
			for filepath in self.get_generated_images(self._session_id):
				if filepath in self._fileinfos_byfilename:
					#print(f"Generated image exists.  Skipping: f'{filepath}'")
					continue
				self.add_file(filepath, 'generated')

			# Get workbench images
			for filepath in self.get_workbench_images(self._session_id):
				if filepath in self._fileinfos_byfilename:
					#print(f"Workbench image exists.  Skipping: f'{filepath}'")
					continue
				self.add_file(filepath, 'workbench')

			# Get thumbnail images
			for filepath in self.get_thumbnail_images(self._session_id):
				if filepath in self._fileinfos_byfilename:
					#print(f"Thumbnail image exists.  Skipping: f'{filepath}'")
					continue
				self.add_file(filepath, 'thumbnail')

			# Get thumbnail images
			for filepath in self.get_playground_images(self._session_id):
				if filepath in self._fileinfos_byfilename:
					#print(f"Thumbnail image exists.  Skipping: f'{filepath}'")
					continue
				self.add_file(filepath, 'playground')

			# Process thumbnails.  Go through images and verify they have a thumbnail
			# Create one if they don't and link images to their thumbnails by hash
			self._fileinfos = [ fileinfo for fileinfo in self._fileinfos if fileinfo.exists() ]
			self._fileinfos_byfilename = { fileinfo.filename : fileinfo for fileinfo in self._fileinfos }
			self._fileinfos_byhash = { fileinfo.hash : fileinfo for fileinfo in self._fileinfos }
			for fileinfo in self._fileinfos:
				# Skip thumbnails
				if (fileinfo.is_thumbnail()):
					continue
				# Check if a thumbnail is valid otherwise re/create it
				if (fileinfo.has_thumbnail()):
					if fileinfo.thumbnail in self._fileinfos_byhash:
						continue

				#print(f"Image didn't have a valid thumbnail: {fileinfo.filename}")
				# Each image should have a thumbnail created by default
				th_filename = f'{THUMBNAILS_FOLDER}/{self._session_id}/th-{fileinfo.type[:2]}-{os.path.basename(fileinfo.filename)}'
				if th_filename in self._fileinfos_byfilename:
					#print(f"  * Linking from thumbnail in filelist: {th_filename}")
					fileinfo._thumbnail = self._fileinfos_byfilename[th_filename].hash
					continue
				else:
					#print(f"  * Thumbnail not in filelist: {th_filename}", end='\n  * ')
					pass
				# We have to create the thumbnail and add it
				self.generate_thumbnail(fileinfo)
				#print(f"  * Done")

		# Preprocess fileinfos to make searching faster
		self._fileinfos = [ fileinfo for fileinfo in self._fileinfos if fileinfo.exists() ]
		self._fileinfos_byhash = { fileinfo.hash : fileinfo for fileinfo in self._fileinfos }
		self._fileinfos_byfilename = { fileinfo.filename : fileinfo for fileinfo in self._fileinfos }

	def generate_thumbnail(self, fileinfo):
		if (fileinfo.is_thumbnail()):
			return
		
		os.makedirs(f'{THUMBNAILS_FOLDER}/{self._session_id}', exist_ok=True)
		th_basename = os.path.basename(fileinfo.filename)
		th_filename = f'{THUMBNAILS_FOLDER}/{self._session_id}/th-{fileinfo.type[:2]}-{th_basename}'
		#print(f"Generating Thumbnail: '{th_filename}'")
		img = Image.open(fileinfo.filename)
		img.thumbnail((128, 128))
		img.save(th_filename)

		th_fileinfo = file_info(th_filename, 'thumbnail', self._session_id)
		fileinfo._thumbnail = th_fileinfo.hash
		self.add_fileinfo(th_fileinfo)
		return th_fileinfo

	def clean_thumbnail_dir(self, wipe=False):
		if wipe:
			#print("Wiping the thumnbails cache")
			filenames = glob.glob(f'{THUMBNAILS_FOLDER}/{self._session_id}/*.png')
			try:
				[ os.remove(filename) for filename in filenames ]
			except Exception as e:
				print(e)
		else:
			#print("Cleaning up thumbnails dir")
			th_fileinfos = self.get_thumbnail_fileinfos()
			for th_fileinfo in th_fileinfos:
				# Chop off the 'th-' to get the original name
				orig_basename = (th_fileinfo.filename.split('/')[-1])[3:]
				if self.has_filename(f'{GENERATED_FOLDER}/{self._session_id}/{orig_basename}'):
					continue
				if self.has_filename(f'{WORKBENCH_FOLDER}/{self._session_id}/{orig_basename}'):
					continue
				#print(f"Removing stale thumbnail file: {th_fileinfo.filename}")
				try:
					os.remove(th_fileinfo.filename)
				except Exception as e:
					print(e)

	def has_filename(self, filename):
		return self._fileinfos_byfilename.get(filename, False)
	
	def has_hash(self, file_hash):
		return self._fileinfos_byhash.get(file_hash, False)

	def get_generated_images(self, session_id):
		return sorted(glob.glob(f"{GENERATED_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

	def get_workbench_images(self, session_id):
		return sorted(glob.glob(f"{WORKBENCH_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

	def get_thumbnail_images(self, session_id):
		return sorted(glob.glob(f"{THUMBNAILS_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

	def get_playground_images(self, session_id):
		return sorted(glob.glob(f"{PLAYGROUND_FOLDER}/{session_id}/*"), key=os.path.getctime, reverse=True)

	def get_fileinfos_type(self, filetype):
		return sorted([ fileinfo for fileinfo in self._fileinfos if fileinfo.type == filetype ], key=lambda x: f'{x.ctime}-{x.filename}', reverse=True) 

	def get_fileinfos(self):
		return self._fileinfos

	def get_generated_fileinfos(self):
		return self.get_fileinfos_type('generated')
	
	def get_workbench_fileinfos(self):
		return self.get_fileinfos_type('workbench')

	def get_thumbnail_fileinfos(self):
		return self.get_fileinfos_type('thumbnail')

	def get_playground_fileinfos(self):
		return self.get_fileinfos_type('playground')

	def get_file_by_hash(self, filehash):
		#print(f"get_file_by_hash: {filehash} {self.get_fileinfos()}")
		return self._fileinfos_byhash.get(filehash)
	
	def get_file_by_filename(self, filename):
		return self._fileinfos_byfilename.get(filename)

	def add_file(self, filename, filetype, thumbnail=False):
		fileinfo = file_info(filename, filetype, self._session_id)
		if (thumbnail):
			self.generate_thumbnail(fileinfo)
		return self.add_fileinfo(fileinfo)

	def add_fileinfo(self, fileinfo):
		#print(f"Adding fileinfo: {fileinfo}")
		if self.has_filename(fileinfo.filename):
			print("Skipping duplicate filename")
			return None
		# WTF doesn't this work?!
		#self._fileinfos.insert(0, fileinfo)
		self._fileinfos = [fileinfo, *self._fileinfos]
		return fileinfo
	
	def remove_file(self, file_hash):
		try:
			file_info = self.get_file_by_hash(file_hash)
			th_file_info = self.get_file_by_hash(file_info.thumbnail)
			print(f'[{self._session_id}] Removing: {file_info.filename} and {th_file_info.filename}')
			os.remove(file_info.filename)
			os.remove(th_file_info.filename)
		except Exception as e:
			print(f'Error removing file: {e}')	
