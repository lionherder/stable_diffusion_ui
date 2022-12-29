from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.controllers.file_manager import file_manager
from dreamflask.controllers.page_manager import page_manager
from dreamflask.models.sd_model import UserInfo
from sqlalchemy.orm import Session
from sqlalchemy import select

class user_manager():
	
	def __init__(self, user_id, engine):
		self._user_id = user_id  # test_sample
		self._engine = engine
		self._display_name = None # Test Sample
		self._bio = None
		self._user_info = None
		self._file_manager = file_manager(user_id, engine)
		self._page_manager = page_manager(user_id, engine)

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

	# Populate
	def init(self):
		self.info(f"user_id : {self._user_id}")
		if ((self._user_id == None) or (len(self._user_id) < 1)):
			return

		# Create or update user
		with Session(self._engine) as session:
			user_info = session.execute(select(UserInfo).where(UserInfo.user_id==str(self._user_id))).fetchone()
			if (not user_info or len(user_info) < 1):
				self.info(f"Creating new user: {self._user_id}")
				self._user_info = UserInfo(user_id=self._user_id, display_name=self._user_id)
				session.add(self._user_info)
				session.commit()
			else:
				self.info(f"User exists: {self._user_id} -> {user_info[0]}")
				self._user_info = user_info[0]
				self._display_name = self._user_info.display_name

		# Recheck the files and page info
		self._file_manager.init()
		self._page_manager.init()

		return user_info

	def get_user_id(self):
		return self._user_id

	@property
	def user_info(self):
		return self._user_info

	@property
	def bio(self):
		return self._bio

	@property
	def display_name(self):
		return self._display_name

	@property
	def user_id(self):
		return self._user_id

	@property
	def file_manager(self):
		return self._file_manager

	@property
	def page_manager(self):
		return self._page_manager
