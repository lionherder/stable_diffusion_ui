from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.controllers.page_item import *

from sqlalchemy import delete

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
			self.add_page(page_name)

	def add_page(self, page_name):
		if (page_name in self._pages):
			return
		self._pages[page_name] = page_item(self._user_id, page_name, self._engine)

	def remove_page(self, page_name):
		with Session(self._engine) as session:
			session.execute(delete(PageInfo).\
				where(PageInfo.owner_id == self._user_id).\
				where(PageInfo.page_name == page_name))
			session.commit()
		del(self._pages[page_name])

	# Update state of page_item.  No db write
	def update_page_state(self, page_name, page_info, with_form=False, commit=False):
		if (page_info == None or not page_name or len(page_name) < 1):
			return

		page_item = self.get_page_item(page_name)
		if (not page_item):
			self.info("  - page doesn't exist")
			return

		page_item.update_page_state(page_info, with_form=with_form, commit=commit)

	# Update the db entry
	def update_page_item(self, page_name):
		if (page_name == None) or (len(page_name) < 1):
			return

		page_item = self.get_page_item(page_name)
		if (not page_item):
			self.info("  - page doesn't exist")
			return

		page_item.update_page_item()

	def insert_page_item(self, page_name):
		if (not page_name or len(page_name) < 1):
			return

		page_item = self.get_page_item(page_name)
		if (page_item):
			self.info("  - page already exists")
			return

		page_item.insert_page_item()


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
