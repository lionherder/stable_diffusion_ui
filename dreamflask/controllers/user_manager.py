from sqlalchemy.orm import Session
from sqlalchemy import select

from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.controllers.file_manager import file_manager
from dreamflask.controllers.page_manager import page_manager
from dreamflask.models.sd_model import UserInfo

class user_manager():
	
	def __init__(self, user_id, engine, create=True):
		self._user_id = user_id
		self._engine = engine
		self._user_info = {}
		self._committed = False
		self._file_manager = file_manager(user_id, engine)
		self._page_manager = page_manager(user_id, engine)

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init(create=create)

	# Populate
	def init(self, create=True):
		self.info(f"Init user: {self._user_id}")
		if ((self._user_id == None) or (len(self._user_id) < 1)):
			return None

		# Create or update user
		with Session(self._engine) as session:
			user_info = session.execute(select(UserInfo).where(UserInfo.user_id==str(self._user_id))).fetchone()
			if (not user_info or len(user_info) < 1):
				if create:
					self.info(f"Creating new user: {self._user_id}")
					self._user_info = self.insert_user_info()
				else:
					self._user_info = self.get_user_info_fields()
					self._committed = False
			else:
				self.info(f"User exists: {self._user_id} -> {user_info[0]}")
				self._user_info = user_info[0].as_dict()
				self._committed = True

		# Recheck the files and page info
		#self._file_manager.refresh()
		#self._page_manager.refresh()

		return user_info

	def get_user_info_fields(self):
		new_user_fields = [ 'user_id', 'display_name', 'bio' ]
		new_user_info = {}
		if (not self._user_info):
			new_user_info = {
				'user_id' : self._user_id,
				'display_name' : 'Not Sure',
				'bio' : '' }
		else:
			new_user_info = { k : self._user_info[k] for k in new_user_fields if k in self._user_info }

		return new_user_info

	def insert_user_info(self):
		self.info(f"  - inserting user: {self.user_id}")

		new_user_args = self.get_user_info_fields()
		with Session(self._engine) as session:
			new_user_info =  UserInfo(**new_user_args)
			session.add(new_user_info)
			session.commit()
			self._committed = True
			self._user_info = new_user_info.as_dict()

		return self._user_info

	# Push info to disk
	def update_user_info(self):
		self.info(f"  - updating user: {self._user_id}")

		update_user_args = self.get_user_info_fields()
		with Session(self._engine) as session:
			#self.info(f"new_file_args: {self._image_info}")
			session.query(UserInfo).\
				filter(UserInfo.user_id==self._user_id).\
				update(update_user_args)
			session.commit()
			self._committed = True

		return self._user_info

	def refresh(self):
		self._file_manager.refresh()
		# TODO: page_manager refresh
		with Session(self._engine) as session:
			user_info = session.execute(select(UserInfo).where(UserInfo.user_id==str(self._user_id))).fetchone()
			if (not user_info or len(user_info) < 1):
				self.info(f"  - Not in DB.  What?  [{self._user_id}")
			else:
				self.info(f"User exists: {self._user_id} -> {user_info}")
				self._user_info = user_info[0].as_dict()

	@property
	def user_info(self):
		return self._user_info

	@property
	def bio(self):
		return self.user_info.bio

	@property
	def display_name(self):
		return self.user_info.get('display_name', 'Not Sure')

	@property
	def user_id(self):
		return self._user_id

	@property
	def file_manager(self):
		return self._file_manager

	@property
	def page_manager(self):
		return self._page_manager
