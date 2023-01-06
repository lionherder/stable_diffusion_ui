import os

from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from dreamflask.dream_utils import convert_bytes
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.models.sd_model import *

GENERATED = 'generated'
WORKBENCH = 'workbench'
THUMBNAIL = 'thumbnail'
PLAYGROUND = 'playground'

class image_item():

	def __init__(self, image_info, owner_id, engine):
		self._image_info = image_info
		self._owner_id = owner_id
		self._committed = False # Has this been committed to the DB
		self._engine = engine
		self._filename = image_info.get('filename', '')
		self._owner_info = None

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
					self._owner_info = file_info_resp[0].owner
					if (self._owner_info):
						self._image_info['display_name'] = self.owner_info.display_name
					else:
						self._image_info['display_name'] = "Not Sure"
					self._committed = True # It has already been committed
					#self.info(f"  - image hash: {self._image_info.get('id')}")
				else:
					# If not in db, check the disk and load if we can
					self._image_info = self.gather_info()

		return self._image_info

	def refresh(self):
		self.info(f"  - refreshing: {self.filename} [{self.id}]")
		self.gather_info()

	def get_file_info_fields(self):
		new_file_fields = [ 'title', 'filename', 'filetype', 'c_time', 'a_time', 'm_time', 'size',
							 'show_meta', 'show_owner', 'is_visible', 'width', 'height', 'meta', 'thumbnail', 'owner_id' ]
		return { k : self._image_info[k] for k in new_file_fields }

	# Push info to disk
	def update_file_info(self, img_info={}):
		self.info(f"  - updating file: {self.filename}")

		update_file_args = self.get_file_info_fields()
		update_file_args.update(img_info)

		with Session(self._engine) as session:
			self.info(f"  - update_file_args: {self._image_info}")
			session.query(FileInfo).\
				filter(FileInfo.id==self.id).\
				update(update_file_args)
			session.commit()
			self._committed = True
		self.refresh()

	def insert_file_info(self):
		self.info(f"  - inserting file: {self.filename}")

		new_file_args = self.get_file_info_fields()
		with Session(self._engine) as session:
			self.info(f"new_file_args: {new_file_args}")
			new_file_info = FileInfo(**new_file_args)
			session.add(new_file_info)
			session.commit()
			self._committed = True
			self.info(f"new_file_info: {new_file_info}")
			self._image_info = new_file_info.as_dict()
			self.info(f"New image hash: {self.id}")
		self.refresh()

	def gather_info(self):
		image_info = {}
		self.info(f"  - gathering info: [{self._filename}]")

		if (not os.path.exists(self._filename)):
			self.info("  - file doesn't exist")
			return {}

		# If we have a db entry, use that info
		if (self.committed):
			self.info("  - loading info from database")
			with Session(self._engine) as session:
				file_info_resp = session.execute(select(FileInfo).where(FileInfo.filename==self._filename)).fetchone()
				if (file_info_resp and len(file_info_resp) > 0):
					#self.info(f"file_info_resp: {file_info_resp[0].as_dict()}")
					image_info = file_info_resp[0].as_dict()
					self._owner_info = file_info_resp[0].owner
					if (self._owner_info):
						image_info['display_name'] = self._owner_info.as_dict()
					else:
						image_info['display_name'] = "Edit Profile"
					self._committed = True # Setting it anyways
		else:
			# Gather up some file stats
			self.info("  - gathering info")
			stats = os.stat(self._filename)
			img = Image.open(self._filename)

			image_info = {
				'title' : '',
				'filename' : self._image_info.get('filename', self._filename),
				'id' : self._image_info.get('id', -1),
				'c_time' : stats.st_ctime,
				'a_time' : stats.st_atime,
				'm_time' : stats.st_mtime,
				'size' : stats.st_size,
				'show_meta' : 'False',
				'show_owner' : 'False',
				'is_visible' : 'True',
				'owner_id' : self._owner_id,
				'thumbnail' : '',
				'width' : img.width,
				'height' : img.height,
				'meta' : self._image_info.get('meta', '')
			}
			image_info['basename'] = os.path.basename(self._image_info.get('filename', ''))

			if self._filename.find('img-samples') > -1:
				image_info['filetype'] = GENERATED
			elif self._filename.find('img-workbench') > -1:
				image_info['filetype']  = WORKBENCH
			elif self._filename.find('img-thumbnails') > -1:
				image_info['filetype']  = THUMBNAIL
			elif self._filename.find('img-playground') > -1:
				image_info['filetype']  = PLAYGROUND

		self._image_info = image_info
		#self.info(f"  - image_info: {image_info}")
		return self._image_info

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

	def as_file_info_fields(self):
		return self.get_file_info_fields()

	#
	# Get title text
	#
	def get_title_text(self, viewer_id=None):
		title = ""

		if (self.title and len(self.title) > 0):
			title += f'''Title: {self.title}
'''

		if (self.owner_id == viewer_id):
			title += f'''[ {os.path.basename(self.filename)} - {self.id}]
'''

		if (self.show_owner) or (self.owner_id == viewer_id):
			title += f'''Owner: {self.display_name}
'''

		if (self.show_meta) or (self.owner_id == viewer_id):
			title += f'''{self.meta}
'''
		title +=f'Size: {convert_bytes(self.size)} [ {self.width}x{self.height} ]'
		return title

	def __str__(self):
		return "ImageInfo: {" + ''.join([ f" '{k}' : '{v}'," for k,v in self._image_info.items() ])[:-1] + "}"

	def as_dict(self):
		return self._image_info

	def set(self, k, v):
		self.info(f"  - setting [{self.id}] '{k}' = '{v}'")
		self._image_info[k] = v
		return self._image_info[k]

	def get(self, k, d=None):
		if (d == None):
			return self._image_info[k]
		else:
			return self._image_info.get(k, d)

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
	def id(self):
		return self._image_info.get('id', -1)

	@property
	def thumbnail(self):
		return self._image_info.get('thumbnail', '')

	@property
	def meta(self):
		return self._image_info.get('meta', '')

	@property
	def width(self):
		return self._image_info.get('width', '-1')

	@property
	def height(self):
		return self._image_info.get('height', '-1')

	@property
	def owner_id(self):
		return self._owner_id

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
		return self._image_info.get('show_owner', 'False') == 'True'

	@property
	def show_meta(self):
		#self.info(f"show_meta: {self._image_info.get('show_meta') == 'True'}")
		return self._image_info.get('show_meta', 'False') == 'True'

	@property
	def is_visible(self):
		#self.info(f"is_visible: {self._image_info.get('is_visible') == 'True'}")
		return self._image_info.get('is_visible', 'True') == 'True'

	@property
	def committed(self):
		return self._committed

	@property
	def filename(self):
		return self._filename

	@property
	def display_name(self):
		return self._image_info.get('display_name', '')

	@property
	def image_info(self):
		return self._image_info

	@property
	def owner_info(self):
		return self._owner_info
