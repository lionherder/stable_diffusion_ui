from file_manager import file_manager

class user_session():
	
	def __init__(self, session_id):
		self._pages = {}
		self._session_id = session_id
		self._filemanager = file_manager(session_id)
		self.update_generate_page_info({}, with_form=False)
		self.update_upscale_page_info({}, with_form=False)
		self.update_cleanup_page_info({}, with_form=False)
		self.update_landing_page_info({}, with_form=False)
		self.update_upload_page_info({}, with_form=False)
		self.update_themes_page_info({}, with_form=False)
		self.update_montage_page_info({}, with_form=False)
		self.update_playground_page_info({}, with_form=False)
		
	def update_generate_page_info(self, page_info, with_form=True):
		generate_info = {
			'page_name' : 'generate_page',
			'session_id' : page_info.get('session_id', ''),
			'sampler' : page_info.get('sampler', 'Euler a'),
			'prompt' : page_info.get('prompt', ''),
			'neg_prompt' : page_info.get('neg_prompt', ''),
			'button' : page_info.get('button', ''),
			'init_image' : page_info.get('init_image', ''),
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
		self._pages['generate_page'] = generate_info
		
	def update_upscale_page_info(self, page_info, with_form=False):
		self._pages['upscale_page'] = {
			'page_name' : 'upscale_page',
			'session_id' : page_info.get('session_id', ''),
			'upscale_image' : page_info.get('upscale_image', 'none'),
			'button' : page_info.get('button', ''),
			'width' : page_info.get('width', '512'),
			'height' : page_info.get('height', '512'),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'scale' : page_info.get('scale', '2'),
			'upscaler' : page_info.get('upscaler', 'ESRGAN_4x'),
		}
		return self._pages['upscale_page']

	def update_cleanup_page_info(self, page_info, with_form=False):
		self._pages['cleanup_page'] = {
			'page_name' : 'cleanup_page',
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'files' : page_info.getlist('files') if with_form else page_info.get('files', [])
		}
		return self._pages['cleanup_page']

	def update_landing_page_info(self, page_info, with_form=False):
		self._pages['landing_page']  = {
			'page_name' : 'landing_page',
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
		}
		return self._pages['landing_page']

	def update_upload_page_info(self, page_info, with_form=False):
		self._pages['upload_page']  = {
			'page_name' : 'upload_page',
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
		}
		return self._pages['upload_page']

	def update_themes_page_info(self, page_info, with_form=False):
		self._pages['themes_page']  = {
			'page_name' : 'themes_page',
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'theme_prompt' : page_info.get('theme_prompt', ''),
			'themes' : page_info.getlist('themes') if with_form else page_info.get('themes', [])
		}
		return self._pages['themes_page']

	def update_montage_page_info(self, page_info, with_form=False):
		self._pages['montage_page']  = {
			'page_name' : 'montage_page',
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'width' : page_info.get('width', '512'),
			'height' : page_info.get('height', '512'),
			'cols' : page_info.get('cols', 5),
			'constrain' : page_info.get('constrain', 'false'),
			'files' : page_info.getlist('files') if with_form else page_info.get('files', [])
		}
		return self._pages['montage_page']

	def update_playground_page_info(self, page_info, with_form=False):
		self._pages['playground_page']  = {
			'page_name' : 'playground_page',
			'session_id' : page_info.get('session_id', ''),
			'button' : page_info.get('button', ''),
			'status_msg' : page_info.get('status_msg', 'Okie Dokie!'),
			'cols' : page_info.get('cols', 5),
			'files' : page_info.getlist('files') if with_form else page_info.get('files', [])
		}
		return self._pages['playground_page']

	def get_session_id(self):
		return self._session_id

	def update_page_info(self, page_name, page_info, with_form=False):
		# Just quietly skip the empty ones
		if (len(page_info) < 1):
			return
		
		#print(f"Updating page info for '{page_name}'")
		if page_name == 'upscale_page':
			self.update_upscale_page_info(page_info, with_form)
		elif page_name == 'generate_page':
			self.update_generate_page_info(page_info, with_form)
		elif page_name == 'cleanup_page':
			self.update_cleanup_page_info(page_info, with_form)
		elif page_name == 'landing_page':
			self.update_landing_page_info(page_info, with_form)
		elif page_name == 'upload_page':
			self.update_upload_page_info(page_info, with_form)
		elif page_name == 'themes_page':
			self.update_themes_page_info(page_info, with_form)
		elif page_name == 'montage_page':
			self.update_montage_page_info(page_info, with_form)
		elif page_name == 'playground_page':
			self.update_playground_page_info(page_info, with_form)
		else:
			self._pages[page_name] = page_info.copy()
	
	def get_page_info(self, page_name):
		#print(f"Getting page info for '{page_name}'")
		return self._pages.get(page_name)

	def get_landing_page_info(self):
		return self.get_page_info('landing_page')

	def get_generate_page_info(self):
		return self.get_page_info('generate_page')

	def get_upscale_page_info(self):
		return self.get_page_info('upscale_page')
		
	def get_upload_page_info(self):
		return self.get_page_info('upload_page')

	def get_cleanup_page_info(self):
		return self.get_page_info('cleanup_page')

	def get_themes_page_info(self):
		return self.get_page_info('themes_page')

	def get_montage_page_info(self):
		return self.get_page_info('montage_page')

	def get_playground_page_info(self):
		return self.get_page_info('playground_page')

	def get_file_manager(self):
		return self._filemanager

	@property
	def filemanager(self):
		return self._filemanager
	
if __name__ == '__main__':
	us = user_session('anything')
	us.add_file('../screenshot.png', filetype='something')
	print(us.get_fileinfos())
