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
IMAGES = 'images_page'
EDITIMAGE = 'edit_image_page'
NAVBAR = 'nav_bar'

PAGE_LIST = [ LANDING, GENERATE, UPSCALE, UPLOAD, CLEANUP, THEMES, MONTAGE, PLAYGROUND, PROFILE, IMAGES, EDITIMAGE ]

class page_item():

	def __init__(self, user_id, page_name, engine):
		self._user_id = user_id
		self._page_name = page_name
		self._engine = engine
		self._modified = False
		self._page_info = {}
		self._page_state = {}

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

		self.init()

	def init(self):
		#self.info(f"Init: {page_name}")
		# Create base state with default properties for the page
		self.update_page_state({})
		# Refresh state from DB if there is an entry
		self.refresh()
		# Insert the page in DB if it's not there
		self.insert_page_item()

	def update_page_state(self, page_info={}, with_form=False, commit=False):
		#self.info(f"Updating page info for: '{self._page_name}' -> [{page_info}]")
		if (not self._page_name or len(self._page_name) < 1):
			return None
		
		if (page_info == None):
			return None

		update_page_state = {}
		if self.page_name == LANDING:
			update_page_state = self.update_landing_page_state(page_info, with_form)
		elif self.page_name == GENERATE:
			update_page_state = self.update_generate_page_state(page_info, with_form)
		elif self.page_name == UPSCALE:
			update_page_state = self.update_upscale_page_state(page_info, with_form)
		elif self.page_name == UPLOAD:
			update_page_state = self.update_upload_page_state(page_info, with_form)
		elif self.page_name == CLEANUP:
			update_page_state = self.update_cleanup_page_state(page_info, with_form)
		elif self.page_name == THEMES:
			update_page_state = self.update_themes_page_state(page_info, with_form)
		elif self.page_name == MONTAGE:
			update_page_state = self.update_montage_page_state(page_info, with_form)
		elif self.page_name == PLAYGROUND:
			update_page_state = self.update_playground_page_state(page_info, with_form)
		elif self.page_name == PROFILE:
			update_page_state = self.update_profile_page_state(page_info, with_form)
		elif self.page_name == IMAGES:
			update_page_state = self.update_image_page_state(page_info, with_form)
		elif self.page_name == EDITIMAGE:
			update_page_state = self.update_edit_image_page_state(page_info, with_form)
		else:
			self.info(f"***** ERROR: unhandled page name {self._page_name}")
			update_page_state = None
			return None

		self._page_info = {
			'id' : None,
			'page_name' : self._page_name,
			'page_info' : json.dumps(update_page_state),
			'u_time' : time.time(),
			'owner_id' : self._user_id
		}

		# Commit, if we ask
		if (commit):
			self.update_page_item()

		self._page_state = update_page_state

	# Create/update page item in database
	def update_page_item(self):
		#self.info("  - committing the update")
		with Session(self._engine) as session:
			page_info_resp = session.execute(select(PageInfo).\
				where(PageInfo.owner_id==self._user_id).\
				where(PageInfo.page_name==self._page_name)).fetchone()
			#self.info(f"  - page_info_resp: {page_info_resp}")

			# Always create the record if needed
			if (page_info_resp == None):
				self.insert_page_item()
			else:
				#self.info("  - updating record")
				session.query(PageInfo).\
					filter(PageInfo.owner_id==self._user_id).\
					filter(PageInfo.page_name==self._page_name).\
					update(self.get_page_info_fields())
				session.commit()
			self._modified = True
		return self._page_info

	# Insert page into DB if page isn't in DB
	def insert_page_item(self):
		#self.info(f"  - inserting page: {self._page_name}")

		with Session(self._engine) as session:
			page_info_resp = session.execute(select(PageInfo).\
				where(PageInfo.owner_id==self._user_id).\
				where(PageInfo.page_name==self._page_name)).fetchone()
			#self.info(f"  - page_info_resp: {page_info_resp[0].as_dict()}")

			# Don't insert if it's there
			if (page_info_resp):
				#self.info(f"  - page already exists.  skipping.")
				return

			#self.info(f"  - new_page_args: {self.get_page_info_fields()}")
			new_page_info = PageInfo(**self.get_page_info_fields())
			session.add(new_page_info)
			session.commit()

			self._modified = True
			self._page_info = new_page_info.as_dict()
			self._page_state = json.loads(self._page_info['page_info'])
		return self._page_state

	def refresh(self):
		with Session(self._engine) as session:
			page_info = session.execute(select(PageInfo).\
				where(PageInfo.owner_id == self._user_id).\
				where(PageInfo.page_name == self._page_name)).fetchone()
			if (page_info):
				self._page_info = page_info[0].as_dict()
				self._page_state = json.loads(self._page_info.get('page_info'))
			else:
				self._modified = False
		return self._page_state

	def get_page_info_fields(self):
		new_file_fields = [ 'page_name', 'page_info', 'u_time', 'owner_id' ]
		new_file_info = { k : self._page_info[k] for k in new_file_fields }
		new_file_info['page_info'] = json.dumps(self._page_state)
		return new_file_info

	def update_landing_page_state(self, page_state, with_form=False):
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
			'model' : page_state.get('model', 'sd-v2-1_768-ema-pruned.ckpt [4bdfc29c]'),
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
			'page_name' : IMAGES,
			'session_id' : page_state.get('session_id', ''),
			'image_id' : page_state.get('image_id', '-1'),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'title' : page_state.get('title', ''),
			'show_owner' : page_state.get('show_owner', 'False'),
			'show_meta'  : page_state.get('show_meta', 'False'),
		}

	def update_edit_image_page_state(self, page_state, with_form=False):
		return {
			'page_name' : EDITIMAGE,
			'session_id' : page_state.get('session_id', ''),
			'image_id' : page_state.get('image_id', '-1'),
			'button' : page_state.get('button', ''),
			'status_msg' : page_state.get('status_msg', 'Okie Dokie!'),
			'title' : page_state.get('title', ''),
			'show_owner' : page_state.get('show_owner', 'False'),
			'show_meta'  : page_state.get('show_meta', 'False'),
			'is_visible'  : page_state.get('is_visible', 'False'),
			'meta' : page_state.get('meta', '')
		}

	def __str__(self):
		return 'page_item: {' + ','.join([ f" '{k}' : '{v}'" for k,v in self._page_state.items() ]) + ' }'

	def get(self, key, default=None):
		if default == None:
			return self._page_state[key]

		return self._page_state.get(key, default)

	def set(self, key, value):
		self._page_state[key] = value
		self._modified = True
		return value

	# This is on almost every page
	@property
	def status_msg(self):
		return self._page_state.get('status_msg', '')

	@status_msg.setter
	def status_msg(self, msg):
		self.set('status_msg', msg)

	@property
	def committed(self):
		return self._modified

	@property
	def id(self):
		return self._page_info.get('id', -1)

	@property
	def page_name(self):
		return self._page_name

	@property
	def page_state(self):
		return self._page_state

	@property
	def page_info(self):
		return self._page_info

