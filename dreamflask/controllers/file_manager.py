import glob
import os
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import *
from dream_consts import GENERATED_FOLDER, PLAYGROUND_FOLDER, THUMBNAILS_FOLDER, WORKBENCH_FOLDER
from dreamflask.models.sd_model import *
from dreamflask.controllers.image_info import PLAYGROUND, THUMBNAIL, WORKBENCH, GENERATED, image_info
from dreamflask.libs.sd_logger import SD_Logger, logger_levels

class file_manager():

	def __init__(self, user_id, engine):
		self._user_id = user_id
		self._engine = engine

		self._logger = SD_Logger(__name__.split(".")[-1], logger_levels.INFO)
		self.info = self._logger.info
		self.debug = self._logger.debug

	def init(self):
		self.update_fileinfos()

	def update_fileinfos(self):
		# Check that all DB image entries have a file on disk
		#self.info("Checking DB entries against disk")
		file_infos_resp = self.get_all_file_infos()
		for file_info_list in file_infos_resp:
			img_info = image_info.from_filename(file_info_list[0].filename, self._user_id, self._engine)
			#self.info(f"  - img_info: {img_info.filename} [{img_info.has_thumbnail()}]")
			if (not img_info.exists()):
				self.info(f"  - stale DB entry")
				self.remove_file(img_info.hash)

			# Check that all DB image thumbnails are valid
			if (img_info.has_thumbnail()):
				th_img_info = image_info.from_hash(img_info.thumbnail, self._user_id, self._engine)
				#self.info(f"    - checking thumbnail integrity: [{img_info.thumbnail}] [{img_info.filename}]")
				if (not th_img_info):
					self.info(f"    - stale thumbnail [{img_info.thumbnail}].  clearing field")
					with Session(self._engine) as session:
						session.query(FileInfo).\
							filter(FileInfo.id==img_info.id).\
							update({'thumbnail' : ''})
						session.commit()

			"""
			Area to do some simple migration stuff
			"""
			#old_info = image_info.from_filename(file_info_list[0].filename, self._user_id, self._engine)
			#img_info._committed = False
			#img_info.refresh_info()
			#new_metadata = img_info.metadata
			#width = img_info.width
			#height = img_info.height
			#img_info._committed = True
			#img_info.refresh_info()
			#img_info._image_info['meta'] = new_metadata
			#img_info._image_info['width'] = width
			#img_info._image_info['height'] = height
			#img_info._image_info['show_meta'] = 'False'
			#img_info._image_info['show_owner'] = 'False'
			#img_info.update_file_info()

		# Load up all the images on disk
		#self.info("Checking disk images against DB")
		user_all_filenames = self.get_all_filenames_on_disk()
		for filename in user_all_filenames:
			img_info = image_info.from_filename(filename, self._user_id, self._engine)
			#self.info(f"  - filename: {img_info.filename} {img_info.has_thumbnail()}")
			if img_info and not img_info.committed:
					img_info.insert_file_info()

			#self.info(f"  - Type: [{img_info.filetype}] Size: [{img_info.size} b]")

		# Check thumbnails
		user_all_file_infos = self.get_all_file_infos_except_thumbnails()
		for file_info_obj in user_all_file_infos:
			img_info = image_info.from_filename(file_info_obj[0].filename, self._user_id, self._engine)
			if not img_info.has_thumbnail():
				self.generate_thumbnail(img_info)

	def generate_thumbnail(self, img_info):
		thumbnails_session = f'{THUMBNAILS_FOLDER}/{self._user_id}'
		th_basename = os.path.basename(img_info.filename)
		th_filename = f'{thumbnails_session}/th-{img_info.filetype[:2]}-{th_basename}'

		self.info(f"Generating thumbnail for: {img_info.filename}")
		self.info(f"  - th_filename: {th_filename}")

		# Check if the thumbnail already exists
		th_img_info = image_info.from_filename(th_filename, self._user_id, self._engine)
		if (th_img_info and th_img_info.committed):
			self.info("  - thumbnail already exists")
			self.info(f"  - linking: {img_info.filename} <-> {th_img_info}")
			img_info.set_thumbnail(th_img_info.id)
			th_img_info.set_thumbnail(img_info.id)
			img_info.update_file_info()
			th_img_info.update_file_info()
		else:
			os.makedirs(thumbnails_session, exist_ok=True)
			self.info("  - creating thumbnail...")
			img = Image.open(img_info.filename)
			img.thumbnail((128, 128))
			img.save(th_filename)
			img.close()
			th_img_info = image_info.from_filename(th_filename, self._user_id, self._engine)
			th_img_info.insert_file_info()
			th_img_info.set_thumbnail(img_info.id)
			img_info.set_thumbnail(th_img_info.id)
			img_info.update_file_info()
			th_img_info.update_file_info()

		return 

	def clean_thumbnail_dir(self):
		self.info("Cleaning up thumbnails dir")
		self.info("  - wiping thumbnail db entries")
		th_file_info_resp = self.get_thumbnail_file_infos()
		#self.info(f"  - th_file_info_resp: {th_file_info_resp}")
		if (th_file_info_resp and len(th_file_info_resp) > 0):
			for th_file_info_list in th_file_info_resp:
				self.info(f"    - [{th_file_info_list[0].id}]")
				self.remove_file(th_file_info_list[0].id)
		self.info("  - wiping the thumnbails cache")
		try:
			[ os.remove(filename) for filename in glob.glob(f'{THUMBNAILS_FOLDER}/{self._user_id}/*.png') ]
		except Exception as e:
			self.debug(e)

		# This will straighten everything out
		self.update_fileinfos()

	def has_filename(self, filename):
		file_info = self.get_file_info_by_filename(filename)
		return file_info and len(file_info) > 0

	def has_hash(self, file_hash):
		file_info = self.get_file_info_by_hash(file_hash)
		return file_info and len(file_info) > 0

	# Return the names of the files on disk
	def get_generated_filenames_on_disk(self):
		return sorted(glob.glob(f"{GENERATED_FOLDER}/{self._user_id}/*"), key=os.path.getctime, reverse=True)

	def get_workbench_filenames_on_disk(self):
		return sorted(glob.glob(f"{WORKBENCH_FOLDER}/{self._user_id}/*"), key=os.path.getctime, reverse=True)

	def get_thumbnail_filenames_on_disk(self):
		return sorted(glob.glob(f"{THUMBNAILS_FOLDER}/{self._user_id}/*"), key=os.path.getctime, reverse=True)

	def get_playground_filenames_on_disk(self):
		return sorted(glob.glob(f"{PLAYGROUND_FOLDER}/{self._user_id}/*"), key=os.path.getctime, reverse=True)

	def get_all_filenames_on_disk(self):
		filenames = self.get_generated_filenames_on_disk()
		filenames.extend(self.get_thumbnail_filenames_on_disk())
		filenames.extend(self.get_playground_filenames_on_disk())
		filenames.extend(self.get_workbench_filenames_on_disk())
		return filenames

	# getting file_infos hits the database
	def get_all_file_infos(self):
		with Session(self._engine) as session:
			return session.execute(select(FileInfo).\
				where(FileInfo.owner_id==self._user_id).\
				order_by(desc(FileInfo.c_time))).fetchall()

	def get_all_file_info_filenames_db(self):
		with Session(self._engine) as session:
			return session.execute(select(FileInfo.filename).\
				where(FileInfo.owner_id==self._user_id).\
				order_by(desc(FileInfo.c_time))).fetchall()

	def get_all_file_infos_except_thumbnails(self):
		with Session(self._engine) as session:
			return session.execute(select(FileInfo).\
				where(FileInfo.filetype!=THUMBNAIL).\
				where(FileInfo.owner_id==self._user_id).\
				order_by(desc(FileInfo.c_time))).fetchall()

	def get_file_infos_by_type(self, filetype):
		with Session(self._engine) as session:
			return session.execute(select(FileInfo).\
				where(FileInfo.filetype==filetype).\
				where(FileInfo.owner_id==self._user_id).\
				order_by(desc(FileInfo.c_time))).fetchall()

	def get_file_info_by_hash(self, filehash):
		with Session(self._engine) as session:
			return session.execute(select(FileInfo).\
				filter(FileInfo.id==filehash).\
				order_by(desc(FileInfo.c_time))).fetchone()
	
	def get_file_info_by_filename(self, filename):
		with Session(self._engine) as session:
			return session.execute(select(FileInfo).\
				filter(FileInfo.filename==filename).\
				order_by(desc(FileInfo.c_time))).fetchone()

	def get_hash_by_filename(self, filename):
		file_info = image_info.from_filename(filename, self._user_id, self._engine)
		if (file_info):
			return file_info.id
		return None

	def get_filename_by_hash(self, hash):
		file_info = image_info.from_hash(hash, self._user_id, self._engine)
		if (file_info):
			return file_info.filename
		return None

	def get_generated_file_infos(self):
		return self.get_file_infos_by_type(GENERATED)
	
	def get_workbench_file_infos(self):
		return self.get_file_infos_by_type(WORKBENCH)

	def get_thumbnail_file_infos(self):
		return self.get_file_infos_by_type(THUMBNAIL)

	def get_playground_file_infos(self):
		return self.get_file_infos_by_type(PLAYGROUND)

	def add_file(self, filename):
		new_img_info = image_info.from_filename(filename, self._user_id, self._engine)
		self.info(f"add_file: {filename} committed: {new_img_info.committed}")

		if (new_img_info and new_img_info.committed):
			self.info("  - file is already in db")
			return new_img_info
		else:
			new_img_info.insert_file_info()
		return new_img_info

	def remove_file(self, file_hash):
		img_info = image_info.from_hash(file_hash, self._user_id, self._engine)
		if (img_info):
			self.info(f'Removing: {img_info.filename} [{img_info.hash}]')
			with Session(self._engine) as session:
				session.execute(delete(FileInfo).where(FileInfo.id==file_hash))
				session.commit()

			try:
				if (os.path.exists(img_info.filename)):
					os.remove(img_info.filename)
			except Exception as e:
				print(f'Error removing file: {e}')	
		else:
			self.info(f"File hash doesn't exist: {img_info.hash}")

