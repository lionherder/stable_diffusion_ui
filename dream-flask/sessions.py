from user_session import user_session

import shelve

class sessions():

	def __init__(self, session_db_name):
		self._globals = {}
		self._users = {}
		self._session_db_name = session_db_name
		self._session_db = shelve.open(session_db_name, writeback=True)

	def init(self):
		self._globals = self._session_db.get('_globals', {})
		self._users = self._session_db.get('_users', {})

	def sync(self):
		print(f"Syncing database: {self._session_db_name}")
		self._session_db['_globals'] = self._globals.copy()
		self._session_db['_users'] = self._users.copy()
		self._session_db.sync()

	def get_users(self):
		return self._users
	
	def get_user_session_ids(self):
		return self._users.keys()

	def get_user(self, session_id, create=True):
		if create:
			self._users[str(session_id)] = self._users.get(session_id, user_session(session_id))
		return self._users[session_id]

	def get_globals(self):
		return self._globals

	def get_models(self):
		return self._globals.get('models', [])
	
	def set_models(self, models):
		self._globals['models'] = models
		return self._globals['models']

	def get_samplers(self):
		return self._globals.get('samplers', [])

	def set_samplers(self, samplers):
		self._globals['samplers'] = samplers
		return self._globals['samplers']

	def get_upscalers(self):
		return self._globals.get('upscalers', [])

	def set_upscalers(self, upscalers):
		self._globals['upscalers'] = upscalers
		return self._globals['upscalers']

	def get_session_db(self):
		return self._session_db

	def new_user(self, session_id):
		self._session_db[session_id] = user_session(session_id)
