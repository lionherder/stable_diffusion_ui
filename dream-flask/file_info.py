import os
import uuid

class file_info():
	
	def __init__(self,
				filename,
				filetype,
				session_id,
				hash=None,
				c_time=None,
				a_time=None,
				m_time=None,
				size=None,
				metadata={}):
		self._filename = filename
		self._filetype = filetype
		self._session_id = session_id
		self._ctime = c_time 
		self._atime = a_time
		self._mtime = m_time
		self._size = size
		self._metadata = metadata
		self._hash = hash
		self._basename = os.path.basename(filename)
		self._thumbnail = ""
		self.update_fileinfo()

	def update_fileinfo(self, rehash=False):
		# Check if file still exists	
		if (not os.path.exists(self._filename)):
			print(f'File does not exist: {self._filename}')
			return None

		# Give us a hash if we don't have one
		if not self._hash or rehash:
			self._hash = str(uuid.uuid4())

		stats = os.stat(self.filename)
		self._size = self._size if self._size else stats.st_size
		self._ctime = self._ctime if self._ctime else stats.st_ctime
		self._atime = self._atime if self._atime else stats.st_atime
		self._mtime = self._mtime if self._mtime else stats.st_mtime

		return self

	def exists(self):
		return os.path.exists(self._filename)
	
	def has_thumbnail(self):
		return len(self._thumbnail) > 0

	def is_thumbnail(self):
		return self._filetype == 'thumbnail'

	def as_dict(self):
		return { 
			"_ctime" : self._ctime,
			"_atime" : self._atime,
			"_mtime" : self._mtime,
			"_size" : self._size,
			"_hash" : self._hash,
			"_filename" : self._filename,
			"_thumbnail" : self._thumbnail,
			"_file_type" : self._filetype
		}

	def __repr__(self):
		return str(self.as_dict())
	
	def __str__(self):
		return str(self.as_dict())

	@property
	def ctime(self):
		return self._ctime
	
	@property
	def atime(self):
		return self._atime

	@property
	def mtime(self):
		return self._mtime

	@property
	def size(self):
		return self._size

	@property
	def hash(self):
		return self._hash

	@property
	def filename(self):
		return self._filename

	@property
	def basename(self):
		return self._basename

	@property
	def thumbnail(self):
		return self._thumbnail

	@property
	def metadata(self):
		return self._metadata

	@property
	def type(self):
		return self._filetype

if __name__ == '__main__':
	fh = file_info('../screenshot.png')