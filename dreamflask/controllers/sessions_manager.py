import glob
import os

from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.models.sd_model import *
from dreamflask.controllers.image_item import image_item
from dreamflask.controllers.user_manager import user_manager
from dreamflask.controllers.page_manager import PAGE_LIST
from dreamflask.dream_consts import *
from dreamflask.dream_utils import *

class sessions_manager():

	def __init__(self, db_name):
		self._db_name = db_name
		self._globals = {}
		self._engine = None
		self._session = None
		self._users = {}
		self._public_key = None
		self._private_key = None

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init()

	# Reset recreates the DB from the drive
	def init(self):
		# Create the db if needed
		self.info(f"Initializing DB [{self._db_name}]")
		self._engine = create_engine(f"sqlite:///{self._db_name}", echo=False, future=True)
		Base.metadata.create_all(self._engine)
		self._session = Session(self._engine)

		if not os.path.exists(PUBLIC_KEY) or not os.path.exists(PRIVATE_KEY):
			generate_rsa_keys()

		self._public_key = RSA.import_key(open(PUBLIC_KEY).read())
		self._private_key = RSA.import_key(open(PRIVATE_KEY).read())

		self.refresh(clean=True)

	# Light weight refresh
	def refresh(self, clean=False):
		self.info(f"Refreshing users.  Be patient.")
		# Get userlist from generated folder
		user_id_list_disk = glob.glob(f"{GENERATED_FOLDER}/*")
		user_id_list_db = self.get_user_ids()

		# Check the _users in DB
		if clean:
			self._users = {}
		else:
			self.info(f"user_id_list_db: {user_id_list_db}")
			for user_id in list(user_id_list_db):
				if not user_id in user_id_list_disk:
					self.info(f"  - Stale user_id: {user_id}")
					self.remove_user(user_id)
					del(self._users[user_id])

		# Re/load the database
		for user_id_path in user_id_list_disk:
			user_id = os.path.basename(user_id_path)
			user_session = self.get_user_by_id(user_id)

			self.info(f"  - init user id: {user_id}")
			# Refresh if we have, add if we don't
			if user_session:
				user_session.refresh()
			else:
				self.add_user(user_id)

	def exec_in_session(self, statement):
		with Session(self._engine) as session:
			return session.execute(statement).fetchall()

	def user_exists(self, user_id):
		with Session(self._engine) as session:
			return len(session.exect(select(UserInfo).where(UserInfo.user_id==user_id).fetchall())) != 0

	def add_user(self, user_id):
		# Check if the display_name is present
		with Session(self._engine) as session:
			self.info(f"Adding session: {user_id}")
			new_user_manager = user_manager(user_id, self._engine, create=True)
			self._users[user_id] = new_user_manager
		return self._users[user_id]

	# TODO: Remove user and all image files
	def remove_user(self, user_id):
		self.info(f"Removing user: '{user_id}'")
		with Session(self.engine) as session:
			user_info = self.get_user_by_id(user_id)
			if user_info:
				# Remove all images from the disk and DB
				self.info("  - removing image files and entries")
				all_file_infos = user_info.image_manager.get_all_file_infos()
				for file_info in all_file_infos:
					user_info.image_manager.remove_file(file_info.id)

				self.info("  - removing page entries")
				for page_name in PAGE_LIST:
					user_info.page_manager.remove_page(page_name)

				self.info("  - removing user entry")
				session.execute(delete(UserInfo).\
					where(UserInfo.user_id == user_id))
				session.commit()
				del(self._users[user_id])

				# Remove user directories
				self.info("  - removing folders")
				for folder in FOLDERS_LIST:
					try:
						os.rmdir(f"{folder}/{user_id}")
					except Exception as e:
						self.info(f"    + not present: '{folder}/{user_id}'")

	def get_users(self):
		return self._users
	
	def get_user_ids(self):
		return self._users.keys()

	def get_user_by_id(self, user_id):
		if (user_id == None or len(user_id) < 1):
			return None

		return self._users.get(user_id)

	def get_globals(self):
		return self._globals

	def get_models(self):
		return self._globals.get('models', [])
	
	def set_models(self, models):
		self._globals['models'] = models
		return self._globals['models']

	def get_samplers(self):
		return self._globals.get('samplers', [])

	def set_samplers(self, samplers):
		self._globals['samplers'] = samplers
		return self._globals['samplers']

	def get_upscalers(self):
		return self._globals.get('upscalers', [])

	def set_upscalers(self, upscalers):
		self._globals['upscalers'] = upscalers
		return self._globals['upscalers']

	def get_file_info_by_filename(self, filename):
		with Session(self._engine) as session:
			file_info = session.execute(select(FileInfo).where(FileInfo.filename==filename)).fetchone()
			if (file_info and len(file_info) > 0):
				return file_info[0]

	def get_file_info_by_hash(self, hash):
		with Session(self._engine) as session:
			file_info = session.execute(select(FileInfo).where(FileInfo.id==hash)).fetchone()
			if (file_info and len(file_info) > 0):
				return file_info[0]

	def get_image_item_by_hash(self, img_hash):
		file_info = self.get_file_info_by_hash(img_hash)
		if (file_info):
			return image_item.from_hash(img_hash, file_info.owner_id, self._engine)

	def get_image_item_by_filename(self, filename):
		file_info = self.get_file_info_by_hash(filename)
		if (file_info):
			return image_item.from_hash(file_info.id, file_info.owner_id, self._engine)

	def get_hash_by_filename(self, filename):
		with Session(self._engine) as session:
			file_info = session.execute(select(FileInfo).where(FileInfo.filename==filename)).fetchone()
			if (file_info and len(file_info) > 0):
				return file_info[0].id

	def get_filename_by_hash(self, hash):
		with Session(self._engine) as session:
			file_info = session.execute(select(FileInfo).where(FileInfo.id==hash)).fetchone()
			if (file_info and len(file_info) > 0):
				return file_info[0].filename
		return None

	def get_all_playground_file_infos(self):
		pg_images = []
		for user_id in self.get_user_ids():
			user_info = self.get_user_by_id(user_id)
			pg_images.extend(user_info.image_manager.get_playground_file_infos())
		return pg_images

	@property
	def engine(self):
		return self._engine








