from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.controllers.page_item import *

class page_manager():

	def __init__(self, user_id, engine):
		self._user_id = user_id
		self._engine = engine
		self._pages = {}

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init()

	def init(self):
		for page_name in PAGE_LIST:
			self.info(f"Init: {page_name}")
			self._pages[page_name] = self.add_page(page_name)

	def add_page(self, page_name):
		return page_item(self._user_id, page_name, self._engine)

	def update_page_item(self, page_name, page_info, with_form=False):
		if (page_info == None or not page_name or len(page_name) < 1):
			return
		page_item = self.get_page_item(page_name)
		if not page_item:
			return

		page_item.update_page_item(page_info, with_form=with_form)
	
	def get_page_item(self, page_name):
		return self._pages[page_name]

	def get_landing_page_item(self):
		return self.get_page_item(LANDING)

	def get_generate_page_item(self):
		return self.get_page_item(GENERATE)

	def get_upscale_page_item(self):
		return self.get_page_item(UPSCALE)
		
	def get_upload_page_item(self):
		return self.get_page_item(UPLOAD)

	def get_cleanup_page_item(self):
		return self.get_page_item(CLEANUP)

	def get_themes_page_item(self):
		return self.get_page_item(THEMES)

	def get_montage_page_item(self):
		return self.get_page_item(MONTAGE)

	def get_playground_page_item(self):
		return self.get_page_item(PLAYGROUND)

	def get_profile_page_item(self):
		return self.get_page_item(PROFILE)

	def get_image_page_item(self):
		return self.get_page_item(IMAGES)

	def get_edit_image_page_item(self):
		return self.get_page_item(EDITIMAGE)
