from dreamflask.libs.sd_logger import SD_Logger, logger_levels

LANDING = 'landing_page'
GENERATE = 'generate_page'
UPSCALE = 'upscale_page'
UPLOAD = 'upload_page'
CLEANUP = 'cleanup_page'
THEMES = 'themes_page'
MONTAGE = 'montage_page'
PLAYGROUND = 'playground_page'

class page_manager():

	def __init__(self, user_id, engine):
		self._user_id = user_id
		self._engine = engine
		self._pages = {}

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

	def init(self):
		for page in [LANDING, GENERATE, UPLOAD, UPSCALE, CLEANUP, THEMES, MONTAGE, PLAYGROUND]:
			#self.info(f"Init: {page}")
			self.update_page_info(page, {})

	def get_page_info(self, page_name):
		return self._pages.get(page_name, {})

	def get_landing_page_info(self):
		return self.get_page_info(LANDING)

	def get_generate_page_info(self):
		return self.get_page_info(GENERATE)

	def get_upscale_page_info(self):
		return self.get_page_info(UPSCALE)
		
	def get_upload_page_info(self):
		return self.get_page_info(UPLOAD)

	def get_cleanup_page_info(self):
		return self.get_page_info(CLEANUP)

	def get_themes_page_info(self):
		return self.get_page_info(THEMES)

	def get_montage_page_info(self):
		return self.get_page_info(MONTAGE)

	def get_playground_page_info(self):
		return self.get_page_info(PLAYGROUND)

	def update_page_info(self, page_name, page_info, with_form=False):
		if (page_info == None):
			return

		#self.info(f"Updating page info for '{page_name}'")
		if page_name == LANDING:
			self.update_landing_page_info(page_info, with_form)
		elif page_name == GENERATE:
			self.update_generate_page_info(page_info, with_form)
		elif page_name == UPSCALE:
			self.update_upscale_page_info(page_info, with_form)
		elif page_name == UPLOAD:
			self.update_upload_page_info(page_info, with_form)
		elif page_name == CLEANUP:
			self.update_cleanup_page_info(page_info, with_form)
		elif page_name == THEMES:
			self.update_themes_page_info(page_info, with_form)
		elif page_name == MONTAGE:
			self.update_montage_page_info(page_info, with_form)
		elif page_name == PLAYGROUND:
			self.update_playground_page_info(page_info, with_form)
		else:
			self._pages[page_name] = page_info.copy()

	def update_landing_page_info(self, page_info, with_form=False):
		self._pages[LANDING]  = {
			'page_name' : LANDING,
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
		}
		return self._pages[LANDING]

	def update_generate_page_info(self, page_info, with_form=True):
		self._pages[GENERATE] = {
			'page_name' : GENERATE,
			'session_id' : page_info.get('session_id', ''),
			'sampler' : page_info.get('sampler', 'Euler a'),
			'prompt' : page_info.get('prompt', ''),
			'neg_prompt' : page_info.get('neg_prompt', ''),
			'button' : page_info.get('button', ''),
			'init_image' : page_info.get('init_image', 'none'),
			'model' : page_info.get('model', 'sd-v2.ckpt [2c02b20a]'),
			'width' : page_info.get('width', '768'),
			'height' : page_info.get('height', '768'),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'steps' : page_info.get('steps', '25'),
			'skips' : page_info.get('skips', '0'),
			'batch_size' : page_info.get('batch_size', '5'),
			'batches' : page_info.get('batches', '1'),
			'seed' : page_info.get('seed', '-1'),
			'scale' : page_info.get('scale', '2'),
			'strength' : page_info.get('strength', '0.5'),
			'cfg_scale' : page_info.get('cfg_scale', '7.5'),
			'ddim_eta' : page_info.get('ddim_eta', '0.0'),
			'samplers' : page_info.get('samplers', []),
			'models' : page_info.get('models', []),
			'cols' : page_info.get('cols', 5)
		}
		return self._pages[GENERATE]
		
	def update_upscale_page_info(self, page_info, with_form=False):
		self._pages[UPSCALE] = {
			'page_name' : UPSCALE,
			'session_id' : page_info.get('session_id', ''),
			'upscale_image' : page_info.get('upscale_image', 'none'),
			'button' : page_info.get('button', ''),
			'width' : page_info.get('width', '512'),
			'height' : page_info.get('height', '512'),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'scale' : page_info.get('scale', '2'),
			'upscaler' : page_info.get('upscaler', 'ESRGAN_4x'),
		}
		return self._pages[UPSCALE]

	def update_upload_page_info(self, page_info, with_form=False):
		self._pages[UPLOAD]  = {
			'page_name' : UPLOAD,
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
		}
		return self._pages[UPLOAD]

	def update_cleanup_page_info(self, page_info, with_form=False):
		self._pages[CLEANUP] = {
			'page_name' : CLEANUP,
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'files' : page_info.getlist('files') if with_form else page_info.get('files', [])
		}
		return self._pages[CLEANUP]

	def update_themes_page_info(self, page_info, with_form=False):
		self._pages[THEMES]  = {
			'page_name' : THEMES,
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'theme_prompt' : page_info.get('theme_prompt', ''),
			'themes' : page_info.getlist('themes') if with_form else page_info.get('themes', [])
		}
		return self._pages[THEMES]

	def update_montage_page_info(self, page_info, with_form=False):
		self._pages[MONTAGE]  = {
			'page_name' : MONTAGE,
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'width' : page_info.get('width', '512'),
			'height' : page_info.get('height', '512'),
			'cols' : page_info.get('cols', 5),
			'constrain' : page_info.get('constrain', 'false'),
			'files' : page_info.getlist('files') if with_form else page_info.get('files', [])
		}
		return self._pages[MONTAGE]

	def update_playground_page_info(self, page_info, with_form=False):
		self._pages[PLAYGROUND]  = {
			'page_name' : PLAYGROUND,
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'cols' : page_info.get('cols', 5),
			'files' : page_info.getlist('files') if with_form else page_info.get('files', [])
		}
		return self._pages[PLAYGROUND]
