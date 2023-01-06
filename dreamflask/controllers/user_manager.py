import os

from sqlalchemy.orm import Session
from sqlalchemy import select

from dreamflask.dream_consts import *
from dreamflask.dream_utils import *
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.controllers.image_manager import image_manager
from dreamflask.controllers.page_manager import page_manager
from dreamflask.controllers.user_item import user_item

class user_manager():
	
	def __init__(self, user_id, engine, create=True):
		self._user_id = user_id
		self._engine = engine
		self._committed = False
		self._user_item = user_item(user_id, engine, create=True)
		self._image_manager = image_manager(user_id, engine)
		self._page_manager = page_manager(user_id, engine)

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init()

	# Populate
	def init(self):
		self.info(f"Init: {self._user_id}")

		for folder in FOLDERS_LIST:
			folder_path = f'{folder}/{clean_name(self.user_id)}'
			os.makedirs(folder_path, exist_ok=True)
	
		return self._user_item

	# Push user info to disk
	def update_user_info(self, user_info=None):
		self._user_item.update_user_info(user_info=user_info)
		return self._user_item

	def refresh(self):
		self._image_manager.refresh()
		self._user_item.refresh()

	@property
	def bio(self):
		return self._user_item.bio

	@property
	def display_name(self):
		return self._user_item.display_name

	@property
	def user_id(self):
		return self._user_item.user_id

	@property
	def user_item(self):
		return self._user_item

	@property
	def image_manager(self):
		return self._image_manager

	@property
	def page_manager(self):
		return self._page_manager
