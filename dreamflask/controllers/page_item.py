import time
import json

from sqlalchemy.orm import Session
from sqlalchemy import select
from dreamflask.dream_utils import convert_bytes
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.models.sd_model import PageInfo

# Was going to do an enum but it was overkill.  These look just fine.
LANDING = 'landing_page'
GENERATE = 'generate_page'
UPSCALE = 'upscale_page'
UPLOAD = 'upload_page'
CLEANUP = 'cleanup_page'
THEMES = 'themes_page'
MONTAGE = 'montage_page'
PLAYGROUND = 'playground_page'
PROFILE = 'profile_page'
EDITIMAGE = 'image_page'

PAGE_LIST = [ LANDING, GENERATE, UPSCALE, UPLOAD, CLEANUP, THEMES, MONTAGE, PLAYGROUND, PROFILE, EDITIMAGE ]

class page_item():

	def __init__(self, user_id, page_name, engine):
		self._user_id = user_id
		self._page_name = page_name
		self._engine = engine
		self._committed = False
		self._page_item = None
		self._page_state = {}

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init()

	def init(self):
		#self.info(f"Init: {page}")
		self.update_page_item({})

	def update_page_item(self, page_info, with_form=False):
		if (not self._page_name or len(self._page_name) < 1):
			return None
		if (page_info == None):
			return None

		new_page_info = {}
		self.info(f"Updating page info for: '{self._page_name}' -> [{page_info}]")
		if self.page_name == LANDING:
			new_page_info = self.update_landing_page_state(page_info, with_form)
		elif self.page_name == GENERATE:
			new_page_info = self.update_generate_page_state(page_info, with_form)
		elif self.page_name == UPSCALE:
			new_page_info = self.update_upscale_page_state(page_info, with_form)
		elif self.page_name == UPLOAD:
			new_page_info = self.update_upload_page_state(page_info, with_form)
		elif self.page_name == CLEANUP:
			new_page_info = self.update_cleanup_page_state(page_info, with_form)
		elif self.page_name == THEMES:
			new_page_info = self.update_themes_page_state(page_info, with_form)
		elif self.page_name == MONTAGE:
			new_page_info = self.update_montage_page_state(page_info, with_form)
		elif self.page_name == PLAYGROUND:
			new_page_info = self.update_playground_page_state(page_info, with_form)
		elif self.page_name == PROFILE:
			new_page_info = self.update_profile_page_state(page_info, with_form)
		elif self.page_name == EDITIMAGE:
			new_page_info = self.update_image_page_state(page_info, with_form)
		else:
			self.info(f"error: unhandled page name {self.page_name}")
			new_page_info = None
			return None

		self._page_item = page_info
		self._page_state = new_page_info

		return self._page_item

	def insert_page_item(self):
		self.info(f"  - inserting page: {self.filename}")

		new_page_args = self.get_file_info_fields()
		with Session(self._engine) as session:
			self.info(f"new_page_args: {self._image_info}")
			new_page_info = PageInfo(**new_page_args)
			session.add(new_page_info)
			session.commit()
			self._committed = True

			self._page_item = new_page_info.as_dict()
			self._page_state = json.loads(self._page_item['page_info'])

	def refresh(self):
		if not self.committed:
			self._page_item = {
					'id' : '-1',
					'page_name' : self._page_name,
					'page_info' : {},
					'u_time' : time.time(),
					'status_msg' : 'Okie Dokie!'
				}
			return self.page_state

		with Session(self._engine) as session:
			page_info = session.execute(select(PageInfo).\
				where(PageInfo.owner_id == self._user_id).\
				where(PageInfo.page_name == self._page_name)).fetchone()
			if (page_info):
				self._page_item = page_info.as_dict()
				self._page_state = json.loads(page_info.page_info)
			else:
				self._page_item = {
					'id' : '-1',
					'page_name' : self._page_name,
					'page_info' : {},
					'u_time' : time.time(),
					'status_msg' : 'Okie Dokie!'
				}
				self._committed = False


		return self.page_state

	def get_page_state(self):
		return self._page_state

	def update_landing_page_state(self, page_state, with_form=False):
		self.info(f"Update landing page: {page_state}")
		return {
			'page_name' : LANDING,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
		}

	def update_generate_page_state(self, page_state, with_form=True):
		return {
			'page_name' : GENERATE,
			'session_id' : page_state.get('session_id', ''),
			'sampler' : page_state.get('sampler', 'Euler a'),
			'prompt' : page_state.get('prompt', ''),
			'neg_prompt' : page_state.get('neg_prompt', ''),
			'button' : page_state.get('button', ''),
			'init_image' : page_state.get('init_image', 'none'),
			'model' : page_state.get('model', 'sd-v2_768.ckpt [2c02b20a]'),
			'width' : page_state.get('width', '768'),
			'height' : page_state.get('height', '768'),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'steps' : page_state.get('steps', '25'),
			'skips' : page_state.get('skips', '0'),
			'batch_size' : page_state.get('batch_size', '5'),
			'batches' : page_state.get('batches', '1'),
			'seed' : page_state.get('seed', '-1'),
			'scale' : page_state.get('scale', '2'),
			'strength' : page_state.get('strength', '0.5'),
			'cfg_scale' : page_state.get('cfg_scale', '7.5'),
			'ddim_eta' : page_state.get('ddim_eta', '0.0'),
			'samplers' : page_state.get('samplers', []),
			'models' : page_state.get('models', []),
		}
		
	def update_upscale_page_state(self, page_state, with_form=False):
		return {
			'page_name' : UPSCALE,
			'session_id' : page_state.get('session_id', ''),
			'upscale_image' : page_state.get('upscale_image', 'none'),
			'button' : page_state.get('button', ''),
			'width' : page_state.get('width', '512'),
			'height' : page_state.get('height', '512'),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'scale' : page_state.get('scale', '2'),
			'upscaler' : page_state.get('upscaler', 'ESRGAN_4x'),
		}

	def update_upload_page_state(self, page_state, with_form=False):
		return {
			'page_name' : UPLOAD,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
		}

	def update_cleanup_page_state(self, page_state, with_form=False):
		return {
			'page_name' : CLEANUP,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'files' : page_state.getlist('files') if with_form else page_state.get('files', [])
		}

	def update_themes_page_state(self, page_state, with_form=False):
		return {
			'page_name' : THEMES,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'theme_prompt' : page_state.get('theme_prompt', ''),
			'themes' : page_state.getlist('themes') if with_form else page_state.get('themes', [])
		}

	def update_montage_page_state(self, page_state, with_form=False):
		return {
			'page_name' : MONTAGE,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'width' : page_state.get('width', '512'),
			'height' : page_state.get('height', '512'),
			'cols' : page_state.get('cols', 5),
			'constrain' : page_state.get('constrain', 'false'),
			'files' : page_state.getlist('files') if with_form else page_state.get('files', [])
		}

	def update_playground_page_state(self, page_state, with_form=False):
		return {
			'page_name' : PLAYGROUND,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'cols' : page_state.get('cols', 5),
			'files' : page_state.getlist('files') if with_form else page_state.get('files', [])
		}

	def update_profile_page_state(self, page_state, with_form=False):
		return {
			'page_name' : PROFILE,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'bio' : page_state.get('bio', ''),
			'display_name' : page_state.get('display_name')
		}

	def update_image_page_state(self, page_state, with_form=False):
		return {
			'page_name' : EDITIMAGE,
			'session_id' : page_state.get('session_id', ''),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'title' : page_state.get('title', ''),
			'show_owner' : page_state.get('show_owner', 'False'),
			'show_meta'  : page_state.get('show_meta', 'False'),
		}

	def get(self, key, default=None):
		if not default:
			return self._page_state[key]

		return self._page_state.get(key, default)

	def set(self, key, value):
		self._page_state[key] = value
		return value

	@property
	def committed(self):
		return self._committed

	@property
	def id(self):
		return self._page_item.get('id', -1)

	@property
	def page_name(self):
		return self._page_name

	@property
	def page_state(self):
		return self._page_state

	@property
	def page_info(self):
		return self._page_item

