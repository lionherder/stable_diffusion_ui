import os

from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import select
from dreamflask.dream_utils import convert_bytes
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.models.sd_model import *

GENERATED = 'generated'
WORKBENCH = 'workbench'
THUMBNAIL = 'thumbnail'
PLAYGROUND = 'playground'

class image_info():

	def __init__(self, image_info, owner_id, engine):
		self._image_info = image_info
		self._owner_id = owner_id
		self._committed = False # Has this been committed to the DB
		self._engine = engine
		self._filename = image_info.get('filename', '')
		self._hash = image_info.get('hash', '')

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init()

	@classmethod
	def from_hash(cls, hash, owner_id, engine):
		# Check the DB for the file using hash and collect data
		with Session(engine) as session:
			file_info_resp = session.execute(select(FileInfo).where(FileInfo.id==hash)).fetchone()
			if (file_info_resp and len(file_info_resp) == 1):
				return cls(file_info_resp[0].as_dict(), owner_id, engine)
		return None

	@classmethod
	def from_filename(cls, filename, owner_id, engine):
		# Check the DB for the file using filename
		with Session(engine) as session:
			file_info_resp = session.execute(select(FileInfo).where(FileInfo.filename==filename)).fetchone()
			if (file_info_resp and len(file_info_resp) == 1):
				return cls(file_info_resp[0].as_dict(), owner_id, engine)

			# Check the disk for on last chance
			if (os.path.exists(filename)):
				return cls({ 'filename' : filename, 'committed' : False }, owner_id, engine)
		return None

	def from_fileinfo(cls, fileinfo, engine):
		# Check the DB for the file using filename
		return cls(fileinfo.as_dict())

	def init(self):
		filename = self._image_info.get('filename', self._filename)

		self._image_info = {}
		# Check the DB for the file using filename or hash
		#self.info(f"init: {self._filename}")
		with Session(self._engine) as session:
			# Check if the filename is in the database
			if (len(filename) > 0):
				file_info_resp = session.execute(select(FileInfo).where(FileInfo.filename==filename)).fetchone()
				if (file_info_resp and len(file_info_resp) > 0):
					self._image_info = file_info_resp[0].as_dict()
					self._committed = True # It has already been committed
					#self.info(f"  - image hash: {self._image_info.get('id')}")
				else:
					# If not in db, check the disk and load if we can
					self._image_info = self.gather_info()

		return self._image_info

	def refresh_info(self):
		self.info(f"  - refreshing: {self.filename} [{self.hash}]")
		self._image_info = self.gather_info()

	def get_file_info_fields(self):
		new_file_fields = [ 'title', 'filename', 'filetype', 'c_time', 'a_time', 'm_time', 'size',
							 'show_meta', 'show_owner', 'width', 'height', 'meta', 'thumbnail', 'owner_id' ]
		return { k : self._image_info[k] for k in new_file_fields }

	# Push info to disk
	def update_file_info(self):
		self.info(f"  - updating file: {self.filename}")

		new_file_args = self.get_file_info_fields()
		with Session(self._engine) as session:
			#self.info(f"new_file_args: {self._image_info}")
			session.query(FileInfo).\
				filter(FileInfo.id==self.id).\
				update(new_file_args)
			session.commit()
			self._committed = True

	def insert_file_info(self):
		self.info(f"  - inserting file: {self.filename}")

		new_file_args = self.get_file_info_fields()
		with Session(self._engine) as session:
			#self.info(f"new_file_args: {self._image_info}")
			new_file_info = FileInfo(**new_file_args)
			session.add(new_file_info)
			session.commit()
			
			self._committed = True
			self._image_info = new_file_info.as_dict()

	def gather_info(self):
		img_info = {}
		self.info(f"Gathering info: [{self._filename}]")

		if (not os.path.exists(self._filename)):
			self.info("  - file doesn't exist")
			return {}

		# If we have a db entry, use that info
		if (self.committed):
			self.info("  - loading info from database")
			with Session(self._engine) as session:
				file_info_resp = session.execute(select(FileInfo).where(FileInfo.filename==self._filename)).fetchone()
				if (file_info_resp and len(file_info_resp) > 0):
					img_info = file_info_resp[0].as_dict()
					self._committed = True # Setting it anyways
		else:
			# Gather up some file stats
			self.info("  - gathering info")
			stats = os.stat(self._filename)
			img = Image.open(self._filename)

			img_info = {
				'title' : '',
				'filename' : self._image_info.get('filename', self._filename),
				'hash' : self._image_info.get('id', self._hash),
				'id' : self._hash,
				'c_time' : stats.st_ctime,
				'a_time' : stats.st_atime,
				'm_time' : stats.st_mtime,
				'size' : stats.st_size,
				'show_meta' : 'False',
				'show_owner' : 'False',
				'owner_id' : self._owner_id,
				'thumbnail' : '',
				'width' : img.width,
				'height' : img.height,
				'meta' : ''
			}
			img_info['basename'] = os.path.basename(self._image_info.get('filename', ''))

			if self._filename.find('img-samples') > -1:
				img_info['filetype'] = GENERATED
			elif self._filename.find('img-workbench') > -1:
				img_info['filetype']  = WORKBENCH
			elif self._filename.find('img-thumbnails') > -1:
				img_info['filetype']  = THUMBNAIL
			elif self._filename.find('img-playground') > -1:
				img_info['filetype']  = PLAYGROUND

			if (self.filetype == THUMBNAIL):
				img_info['meta'] = THUMBNAIL
			elif (len(img.info.keys()) < 1):
				img_info['meta'] = "No Data"
			else:
				img_info['meta'] = ''.join([ f'{img.info[i]} ' for i in img.info ])

		#self.info(f"  - img_info: {img_info}")
		return img_info

	def exists(self):
		return os.path.exists(self.filename)
	
	def exists_in_db(self):
		with Session(self._engine) as session:
			exists_resp = session.execute(select(FileInfo).where(FileInfo.filename==self._filename))
			return len(exists_resp) > 0
	
	def has_thumbnail(self):
		return len(self.thumbnail) > 0

	def is_thumbnail(self):
		return self.filetype == THUMBNAIL

	def set_thumbnail(self, thumbnail):
		self._image_info['thumbnail'] = thumbnail

	def __str__(self):
		return "ImageInfo: {" + ''.join([ f" '{k}' : '{v}'," for k,v in self._image_info.items() ])[:-1] + "}"

	def as_dict(self):
		return self._image_info

	def as_file_info_fields(self):
		return self.get_file_info_fields()

	def get_title_text(self, viewer_id=None):
		title = f'Title: {os.path.basename(self.filename)} [{convert_bytes(self.size)}]'

		if (self.show_owner) or (self.owner_id == viewer_id):
			title += f'''
Owner: {self.owner_id}'''

		if (self.show_meta) or (self.owner_id == viewer_id):
			title += f'''
Parameters: {self.metadata}
'''
		return title

	@property
	def ctime(self):
		return self._image_info.get('c_time', -1)
	
	@property
	def atime(self):
		return self._image_info.get('a_time', -1)

	@property
	def mtime(self):
		return self._image_info.get('m_time', -1)

	@property
	def size(self):
		return self._image_info.get('size', -1)

	@property
	def hash(self):
		return self._image_info.get('id', -1)

	@property
	def id(self):
		return self._image_info.get('id', -1)

	@property
	def thumbnail(self):
		return self._image_info.get('thumbnail', '')

	@property
	def metadata(self):
		return self._image_info.get('meta', '')

	@property
	def width(self):
		return self._image_info.get('width', '-1')

	@property
	def height(self):
		return self._image_info.get('height', '-1')

	@property
	def owner_id(self):
		return self._image_info.get('owner_id', '-1')

	@property
	def basename(self):
		return self._image_info.get('basename', '')

	@property
	def filetype(self):
		return self._image_info.get('filetype', '')

	@property
	def title(self):
		return self._image_info.get('title', '')

	@property
	def show_owner(self):
		#self.info(f"show_owner: {self._image_info['show_owner'] == 'True'}")
		return bool(self._image_info.get('show_owner', 'False')) == 'True'

	@property
	def show_meta(self):
		#self.info(f"show_meta: {self._image_info.get('show_meta') == 'True'}")
		return bool(self._image_info.get('show_meta', 'False')) == 'True'

	@property
	def committed(self):
		return self._committed

	@property
	def filename(self):
		return self._filename

	@property
	def image_info(self):
		return self._image_info
