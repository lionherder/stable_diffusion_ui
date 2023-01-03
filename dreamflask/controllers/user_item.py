from sqlalchemy.orm import Session
from sqlalchemy import select

from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.controllers.file_manager import file_manager
from dreamflask.controllers.page_manager import page_manager
from dreamflask.models.sd_model import UserInfo

class user_item():
	
	def __init__(self, user_id, engine, create=True):
		self._user_id = user_id
		self._engine = engine
		self._user_info = {}
		self._committed = False

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

		self.update_properties()

		return user_info

	def get_user_info_fields(self):
		# [ 'user_id', 'display_name', 'bio' ]
		col_names = UserInfo().__table__.columns
		#self.info(f"col_names: {col_names}")
		new_user_info = {}

		# Create default user info
		if (not self._user_info):
			new_user_info = {
				'user_id' : self._user_id,
				'display_name' : 'Edit Profile',
				'bio' : '' }
		else:
			new_user_info = { k : self._user_info[k] for k in col_names if k in self._user_info }

		self.info(f"new_user_info: {new_user_info}")
		return new_user_info

	def insert_user_info(self, user_info=None):
		self.info(f"  - inserting user: {self._user_id}")

		new_user_args = self.get_user_info_fields()
		with Session(self._engine) as session:
			new_user_info =  UserInfo(**new_user_args)
			session.add(new_user_info)
			session.commit()
			self._committed = True
			self._user_info = new_user_info.as_dict()

		self.update_properties()
		return self._user_info

	# Push info to disk
	def update_user_info(self, user_info=None):
		#self.info(f"  - updating user: {self._user_id}")
		update_user_args = user_info or self.get_user_info_fields()
		#self.info(f"  - user_info: {user_info}")

		with Session(self._engine) as session:
			#self.info(f"new_file_args: {self._image_info}")
			session.query(UserInfo).\
				filter(UserInfo.user_id==self._user_id).\
				update(update_user_args)
			session.commit()
			self._committed = True

		self._user_info = update_user_args
		self.update_properties()

		return self._user_info

	def update_properties(self, user_info=None):
		# Create/Update our attributes/properties
		for col_name in UserInfo.__table__.columns:
			col_base = str(col_name).split('.')[-1]
			# self.info(f"Adding property: {col_base} = '{self._user_info[col_base]}'")
			if (user_info):
				self.__dict__[col_base] = user_info[col_base]
			else:
				self.__dict__[col_base] = self._user_info[col_base]

	def refresh(self):
		with Session(self._engine) as session:
			user_info = session.execute(select(UserInfo).where(UserInfo.user_id==str(self._user_id))).fetchone()
			if (not user_info or len(user_info) < 1):
				self.info(f"  - Not in DB.  What?  [{self._user_id}")
			else:
				self.info(f"User exists: {self._user_id} -> {user_info}")
				self._user_info = user_info[0].as_dict()
		self.update_properties()

	@property
	def committed(self):
		return self._committed

if __name__ == '__main__':
	from dreamflask.controllers.sessions_manager import *
	from dreamflask.controllers.user_item import *

	sm = sessions_manager('sessions_dev.db')
	ui = user_item('lyon-furry', sm._engine)