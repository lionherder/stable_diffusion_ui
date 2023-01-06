#!/usr/bin/python3

import io
import json
import sys
import traceback
import base64
import shutil

sys.path.append('dreamflask')

import os
import time
import requests
import gradio

from gradio.processing_utils import encode_pil_to_base64, decode_base64_to_image

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from random import randint

from flask import Flask
from flask import request, send_file, escape
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename

from dreamflask.dream_utils import *
from dreamflask.dream_consts import *
from dreamflask.controllers.sessions_manager import sessions_manager
from dreamflask.controllers.page_manager import *
from dreamflask.controllers.image_item import image_item
from dreamflask.libs.montage import create_montage
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.views.error_pages import page_404, share_404
from dreamflask.views.landing_page import landing_page
from dreamflask.views.generate_page import generate_page
from dreamflask.views.themes_page import themes_page
from dreamflask.views.cleanup_page import cleanup_page
from dreamflask.views.upscale_page import upscale_page
from dreamflask.views.upload_page import upload_page
from dreamflask.views.montage_page import montage_page
from dreamflask.views.playground_page import playground_page
from dreamflask.views.profile_page import profile_page
from dreamflask.views.image_page import image_page
from dreamflask.views.view_page import view_page
from dreamflask.views.edit_image_page import edit_image_page

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 ** 8

# Flask globals
sessions_db = None
log = None

class WildcardConverter(BaseConverter):
    regex = r'(|/.*?)'
    weight = 200

app.url_map.converters['wildcard'] = WildcardConverter

@app.route("/", methods = ['GET', 'POST'])
def index():
	session_id = request.form.get('session_id', 'default')

	if (request.method != "POST" or session_id == 'default' or len(session_id) < 1):
		return landing_page(sessions_db)

	user_obj = sessions_db.get_user_by_id(session_id)

	if (not user_obj):
		user_obj = sessions_db.add_user(session_id)

	page_name = request.form.get('page_name', '')
	page_name = page_name if page_name != NAVBAR else PROFILE

	if (not page_name in PAGE_LIST):
		return landing_page(sessions_db)

	# Update page state with new request.form
	user_obj.page_manager.update_page_state(page_name, request.form, with_form=True, commit=True)
	# Write the new state to the DB
	user_obj.page_manager.update_page_item(page_name)

	log.info(f"Dispatching user '{session_id}' -> '{page_name}'")
	#log.info(f"request.form: {request.form}")
	if (page_name == LANDING):
		return generate_page(sessions_db, session_id)
	elif (page_name == GENERATE):
		return GenerateImage(session_id)
	elif (page_name == CLEANUP):
		return CleanUp(session_id)
	elif (page_name == UPSCALE):
		return UpscaleFile(session_id)
	elif (page_name == UPLOAD):
		return UploadFile(session_id)
	elif (page_name == THEMES):
		return CreateThemes(session_id)
	elif (page_name == MONTAGE):
		return MakeMontage(session_id)
	elif (page_name == PLAYGROUND):
		return Playground(session_id)
	elif (page_name == NAVBAR or page_name == PROFILE):
		return ProfilePage(session_id)
	elif (page_name == IMAGES):
		return ImagePage(session_id)
	elif (page_name == EDITIMAGE):
		return EditImagePage(session_id)

	return landing_page(sessions_db)

def EditImagePage(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_edit_image_page_item()
	button = page_item.get('button')
	image_id = page_item.get('image_id')

	# Shouldn't be here without an image hash
	if (not image_id):
		return image_page(sessions_db, user_id)

	if (button == 'Update'):
		img_item = user_info.image_manager.get_file_item_by_hash(image_id)
		if (not img_item):
			page_item.status_msg = "Image doesn't exist in the DB"
			return edit_image_page(sessions_db, user_id, image_id)

		img_item.update_file_info(img_info= {
			'title' : page_item.get('title',''),
			'show_owner' : page_item.get('show_owner', 'False'),
			'show_meta' :  page_item.get('show_meta', 'False'),
			'is_visible' :  page_item.get('is_visible', 'False'),
			'meta' : page_item.get('meta') } )
		page_item.status_msg = "Image info updated"
		user_info.refresh()
	if (button == 'Delete'):
		user_info.image_manager.remove_file(image_id)
		page_item.status_msg = "Image removed."
		user_info.refresh()
		return image_page(sessions_db, user_id)
	elif (button == 'Return'):
		return image_page(sessions_db, user_id)
	elif (button == 'Refresh'):
		user_info.refresh()
	elif (button == 'Reset URL'):
		img_item = user_info.image_manager.get_file_item_by_hash(image_id)
		if (not img_item):
			page_item.status_msg = "Image doesn't exist in the DB"
			return image_page(sessions_db, user_id)

		log.info(f"  - reset image info: {img_item.id}")
		user_info.image_manager.rehash_file(image_id)
		img_item.refresh()
		return edit_image_page(sessions_db, user_id, img_item.id)
		
	return edit_image_page(sessions_db, user_id, image_id)

def ImagePage(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_image_page_item()
	image_id = page_item.get('image_id')
	button = page_item.get('button')
	#log.info(f"page_item: {page_item}")

	if (image_id and image_id != '-1'):
		return edit_image_page(sessions_db, user_id, image_id)
	
	elif (button == 'Return'):
		return generate_page(sessions_db, user_id)
	elif (button == 'Refresh'):
		user_info.refresh()
	elif (button == 'Playground'):
		return playground_page(sessions_db, user_id)

	return image_page(sessions_db, user_id)

def ProfilePage(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_profile_page_item()
	button = page_item.get('button')
	#log.info(f"page_item: {page_item}")
	# Don't want to cache this in page state
	confirmed = request.form.get('confirm', "") == 'True'

	if (button == 'Reset'):
		if (not confirmed):
			page_item.status_msg = 'Please confirm the reset'
			return profile_page(sessions_db, user_id)
		LoadAPIConfig()
		page_item.update_profile_page_state({})
		user_info.image_manager.clean_thumbnail_dir()
		user_info.image_manager.update_fileinfos()
		page_item.status_msg = 'Image file links reset'
		return profile_page(sessions_db, user_id)
	elif (button == "Nuke Account"):
		if (not confirmed):
			page_item.status_msg = 'Please confirm the nuke'
			return profile_page(sessions_db, user_id)
		sessions_db.remove_user(user_id)
		# TODO: Nuke account
		return landing_page(sessions_db)
	elif (button == 'Update'):
		user_info.update_user_info( {
			'user_id' : user_id,
			'display_name' : request.form['display_name'],
			'bio' : request.form['bio']
		})
		page_item.status_msg = "User profile updated"

	elif (button == 'Return'):
		return generate_page(sessions_db, user_id)
	elif (button == 'Refresh'):
		user_info.refresh()
	elif (button == 'Clear'):
		page_item.update_page_state({})

	return profile_page(sessions_db, user_id)

def Playground(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_playground_page_item()
	button = page_item.get('button')
	files = page_item.get('files', [])
	status_msg = ""

	if (button == 'Add'):
		count = len(files)
		if (count < 1):
			page_item.status_msg = 'Select some files'
		for file_hash in files:
			file_item = image_item.from_hash(file_hash, user_info, sessions_db.engine)
			src_filename = os.path.basename(file_item.filename)
			dest_filename = f"{PLAYGROUND_FOLDER}/{user_id}/{src_filename}"
			try:
				status_msg += f"Adding to Playground: {src_filename}<br>"
				shutil.copyfile(file_item.filename, dest_filename)
				img_info = image_item.from_filename(dest_filename, user_id, sessions_db.engine)
				img_info.set('meta', file_item.meta)
				img_info.insert_file_info()
				user_info.image_manager.generate_thumbnail(img_info)
				user_info.image_manager.refresh()
			except Exception as e:
				log.info(e)
				status_msg += f"Error: {file_hash} : {e}"
			page_item.status_msg = status_msg
			page_item.set('files', [])
	elif (button== 'Remove'):
		del_files = request.form.getlist('files')
		num_removed = 0
		for file_hash in del_files:
			file_item = user_info.image_manager.get_file_item_by_hash(file_hash)
			log.info(f"filename: {file_item}")
			if (not file_item):
				return image_page(sessions_db, user_id)
			# Only delete files from playground
			if (file_item.filename.find(PLAYGROUND_FOLDER) > -1):
				num_removed += 1
				user_info.image_manager.remove_file(file_hash)
		page_item.status_msg = f"{num_removed} playground file(s) removed."
	elif (button == 'Return'):
		return generate_page(sessions_db, user_id)
	elif (button == 'Refresh'):
		user_info.image_manager.refresh()
	elif (button == 'Clear'):
		page_item.update_page_state({})
	elif (button == 'Image Info'):
		return image_page(sessions_db, user_id)

	return playground_page(sessions_db, user_id)

def CreateThemes(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_themes_page_item()
	button = page_item.get('button')
	
	themes = request.form.getlist('themes')
	theme_prompt = ", ".join(themes)
	if (button == 'Generate'):
		page_item.set('theme_prompt', theme_prompt)
		page_item.set('themes', themes)
	elif (button == 'Clear'):
		page_item.update_page_state({})
	elif (button == 'Return'):
		page_item.set('themes', themes)
		return generate_page(sessions_db, user_id)

	return themes_page(sessions_db, user_id)

def MakeMontage(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_montage_page_item()
	button = page_item.get('button')

	if (button == 'Return'):
		return generate_page(sessions_db, user_id)
	elif (button == 'Refresh'):
		user_info.image_manager.refresh()
	elif (button == "Clear"):
		page_item.update_page_state({})
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, user_id)
	elif (button == 'Create'):
		image_hashes = request.form.getlist('files')
		workbench_session_folder = f'{WORKBENCH_FOLDER}/{user_id}'
		constrain = page_item.get('constrain', 'false') == 'true'
		cols = int(page_item.get('cols'))
		width = int(page_item.get('width'))
		height = int(page_item.get('height'))

		if (len(image_hashes) < 1):
			page_item.status_msg = "How about selecting some files?"
		else:
			# Create montage and drop it in the workbench directory
			try:
				save_filename = f'{workbench_session_folder}/montage-{int(time.time())}.png'
				os.makedirs(f'{workbench_session_folder}', exist_ok=True)
				image_filenames = [ user_info.image_manager.get_filename_by_hash(image_hash) for image_hash in image_hashes ]
				create_montage(save_filename, image_filenames, cols, width, height, 5, 5, 5, 5, 5, constrain)

				img = Image.open(save_filename)
				montage_meta = f"Montage image.  Images: {len(image_hashes)}, Size: {img.width}x{img.height}"
				metadata = PngInfo()
				metadata.add_text("filename", montage_meta)
				img.save(save_filename, pnginfo=metadata)
				img.close()

				img_info = image_item.from_filename(save_filename, user_id, sessions_db.engine)
				img_info.insert_file_info()
				user_info.image_manager.generate_thumbnail(img_info)
				user_info.image_manager.refresh()
				#log.info(f"Montage: {img_info}")
				page_item.status_msg = f"Montage created.<br><br><a href='/share/{img_info.id}' title='{img_info.get_title_text(user_id)}' target='_'><img class='img-thumbnail' src='/share/{img_info.thumbnail}' width='128' height='128'></a>"
			except Exception as e:
				log.info(traceback.print_exc())
				page_item.status_msg = "Error with montage creation"
	
	return montage_page(sessions_db, user_id)

def UpscaleFile(user_id):
	user_item = sessions_db.get_user_by_id(user_id)
	page_item = user_item.page_manager.get_upscale_page_item()
	button = page_item.get('button', '')
	image_hash = page_item.get('upscale_image')

	if (button == "Upscale"):
		if (image_hash == 'none'):
			page_item.status_msg = "Select an image to upscale"
		else:
			img_item = image_item.from_hash(image_hash, user_id, sessions_db.engine)
			save_filename = f'{WORKBENCH_FOLDER}/{user_id}/{int(time.time())}-upscaled-{os.path.basename(img_item.filename)}'
			upscaled_resp = generate_upscaling(page_item, encode_pil_to_base64(Image.open(img_item.filename)))
			upscaled_image = decode_base64_to_image(f"data:image/png;base64,{upscaled_resp['image']}")
			upscaled_image.save(save_filename)

			upscaled_meta = f"{page_item.get('scale')}x upscale image"
			metadata = PngInfo()
			metadata.add_text("info", upscaled_meta)
			upscaled_image.save(save_filename, pnginfo=metadata)
			upscaled_image.close()

			upscaled_item = user_item.image_manager.add_file(save_filename)
			user_item.image_manager.generate_thumbnail(upscaled_item)
	elif (button == 'Return'):
		return generate_page(sessions_db, user_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, user_id)
	elif (button == 'Refresh'):
		user_item.image_manager.refresh()
	elif (button == "Clear"):
		page_item.update_page_state({})

	return upscale_page(sessions_db, user_id)

def CleanUp(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_cleanup_page_item()
	button = page_item.get('button')

	if (button == "Return"):
		return generate_page(sessions_db, user_id)
	elif (button == "Refresh"):
		user_info.image_manager.refresh()
		return cleanup_page(sessions_db, user_id)
	elif (button == "Clear"):
		page_item.update_page_state({})
	elif (button == 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.image_manager.remove_file(filename)

		page_item.status_msg = f"{len(del_files)} file(s) removed"
		user_info.image_manager.refresh()
	return cleanup_page(sessions_db, user_id)

def GenerateStatusMsg(user_id):
	status = "Okie Dokie!<br>"
	progress_info = generate_progress(user_id)
	progress_percent = progress_info.get('progress', 0.0) * 100.0
	if ( progress_percent > 0.0):
		status = f"Rendering<br>Progress: {int(progress_percent)}% complete...<br>"
		status += f"Remaining: ~{int(progress_info.get('eta_relative', 'N/A'))}s"
	else:
		status += "GPU: Idle"
	return status

def GenerateImage(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_generate_page_item()

	button = page_item.get('button')
	prompt = page_item.get('prompt')
	seed = int(page_item.get('seed'))
	page_item.set('seed', randint(0, 2**32) if seed < 0 else seed)


	if (button == "Refresh"):
		LoadAPIConfig()
		user_info.refresh()
		page_item.status_msg = GenerateStatusMsg(user_id)
		return generate_page(sessions_db, user_id)
	elif (button == "Clean Files"):
		return cleanup_page(sessions_db, user_id)
	elif (button == "Clear"):
		page_item.update_page_state({})
		return generate_page(sessions_db, user_id)
	elif (button == "Upscale"):
		return upscale_page(sessions_db, user_id)
	elif (button == "Upload"):
		return upload_page(sessions_db, user_id)
	elif (button == "Themes"):
		return themes_page(sessions_db, user_id)
	elif (button == "Montage"):
		return montage_page(sessions_db, user_id)
	elif (button == "Playground"):
		return playground_page(sessions_db, user_id)
	elif (button == "Profile"):
		return profile_page(sessions_db, user_id)
	elif (button == "Image Info"):
		return image_page(sessions_db, user_id)
	else:
		log.info(f'Generating:')

		[ log.info(f'  {k}: {v}') for k,v in page_item.page_state.items() ]

		toc = time.time()
		# Update model if the value has changed
		generate_options(page_item)
		if (page_item.get('init_image', 'none') == 'none'):
			generated_resp = generate_txt2img(page_item)
		else:
			image_hash = page_item['init_image']
			file_info = user_info.image_manager.get_filename_by_hash(image_hash)
			generated_resp = generate_img2img(page_item, encode_pil_to_base64(Image.open(file_info.filename)))

		generated_images = generated_resp.get('images', [])
		index = 0
		for image_b64 in generated_images:
			prompt_filename = clean_name(prompt[0:20]) if len(prompt) > 0 else 'BLANK'
			output_filename = f'{GENERATED_FOLDER}/{user_id}/{prompt_filename}-{index:05}.png'
			# Make sure we don't write over existing images
			while os.path.exists(output_filename):
				index += 1
				output_filename = f'{GENERATED_FOLDER}/{user_id}/{prompt_filename}-{index:05}.png'
			log.info(f"Saving image to {output_filename} [{page_item.get('width')}x{page_item.get('height')}]")
			img = decode_base64_to_image(f"data:image/png;base64,{image_b64}")
			
			info = ""
			for item in [
				('prompt', 'Prompt'),
				('neg_prompt', 'Neg Prompt'),
				('init_image', 'Init Image'),
				('model', 'Model'),
				('steps', 'Steps'),
				('batch_size', 'Samples'),
				('batches', 'Batches'),
				('scale', 'Init Scale'),
				('strength', 'Strength'),
				('cfg_scale', 'Weight') ]:
				info += f"{item[1]}: {page_item.get(item[0])}\n"
			# Clear out any metadata
			metadata = PngInfo()
			img.save(output_filename, pnginfo=metadata)
			img.close()

			img_item = image_item.from_filename(output_filename, user_id, sessions_db.engine)
			img_item.set('meta', info[:-1])
			img_item.insert_file_info()
			user_info.image_manager.generate_thumbnail(img_item)
			
		if (len(generated_images) < 1):
			page_item.status_msg = "Failed to generate pictures.  Lower resolution and/or the number of samples."
		else:
			# Make a nice little success status message
			infotexts = json.loads(generated_resp['info'])['infotexts'][0]
			index = infotexts.find("Steps: ")
			prompt = f'"{infotexts[:index-1]}"'
			infotexts = infotexts[index:]
			# Change , to | and recreate the info text 
			infotexts = infotexts.replace(",", " |")
			# Wrap quotes around the prompt
			infotexts = f'Last Prompt: {prompt}<br>{infotexts}'
			page_item.status_msg = f"{len(generated_images)} images generated in {time.time() - toc} sec.<br>{infotexts}"
			user_info.image_manager.refresh()

	return generate_page(sessions_db, user_id)

def UploadFile(user_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_upload_page_item()
	button = page_item.get('button')

	if (button == 'Return'):
		return generate_page(sessions_db, user_id)
	elif (button == "Refresh"):
		LoadAPIConfig()
		user_info.image_manager.refresh()
		page_item.set_status = "<br>" + GenerateStatusMsg(user_id)
		return upload_page(sessions_db, user_id)
	elif (button == "Clear"):
		page_item.update_page_state({})
		return upload_page(sessions_db, user_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, user_id)

	for file_info in request.files.getlist('file'):
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		if file_info.filename == '':
			page_item.status_msg = "Select a file, doofus!"
			return upload_page(sessions_db, user_id)

		log.info(f"Uploading file: {file_info.filename}")
		if file_info and allowed_file(file_info.filename):
			os.makedirs(f'{WORKBENCH_FOLDER}/{user_id}', exist_ok=True)
			save_filename = f'{WORKBENCH_FOLDER}/{user_id}/{secure_filename(file_info.filename)}'
			file_info.save(save_filename)
			img_info = user_info.image_manager.add_file(save_filename)
			user_info.image_manager.generate_thumbnail(img_info)
			page_item.status_msg = f"File uploaded {file_info.filename}"

	return upload_page(sessions_db, user_id)

@app.route("/share/<string:share_uuid>")
def ShareFile(share_uuid):
	pass_thru = False
	
	#log.info(f"Sharing request: {share_uuid}")
	if (share_uuid[-3:] == '-PT'):
		share_uuid = share_uuid[:-3]
		#log.info(f"  -- pass_thru file: {share_uuid}")
		pass_thru = True

	img_info = sessions_db.get_image_item_by_hash(share_uuid)

	#log.info(f"img_info: {img_info}")
	if img_info:
		if not img_info.exists():
			#log.info(f"  - file doesn't exist for hash: {share_uuid}")
			return share_404(share_uuid), 404
		elif pass_thru:
			# Send it on through if it's an -ST file
			return send_file(img_info.filename)
		elif not img_info.is_thumbnail():
			#log.info(f"  - view page: '{img_info.filename}' - {convert_bytes(img_info.size)}")
			return view_page(img_info)
		else:
			return send_file(img_info.filename)

	return share_404(share_uuid), 404

@app.errorhandler(404)
def not_found_404(e=None):
	page = page_404(e)
	return page, 404

@app.route("/css/<string:css_file>")
def LoadCSS(css_file):
	filename = f"{CSS_FILES}/{css_file}"
	#log.info(f"Loading CSS: {css_file}")
	if (not os.path.exists(filename)):
		return page_404(css_file)
	else:
		return send_file(f"{CSS_FILES}/{css_file}")

@app.route("/js/<string:js_file>")
def LoadJS(js_file):
	filename = f"{JS_FILES}/{js_file}"
	#log.info(f"Loading JS: {js_file}")
	if (not os.path.exists(filename)):
		return page_404(js_file)
	else:
		return send_file(filename)

@app.route("/images/<string:img_file>")
def LoadImage(img_file):
	filename = f"{IMG_FILES}/{img_file}"
	log.info(f"Sending Image: {img_file}")
	if (not os.path.exists(filename)):
		return page_404(img_file)
	return send_file(f"{IMG_FILES}/{img_file}")

@app.route("/favicon.ico")
def LoadFavIcon():
	return send_file(FAVICON)

def LoadAPIConfig():
	# Get the models
	resp = requests.get(MODELS_API_URL)
	resp_dict = resp.json()
	sessions_db.set_models([ f"{os.path.basename(model['title'])}" for model in resp_dict if model['model_name'] != 'None'])

	# Get the samplers
	resp = requests.get(SAMPLERS_API_URL)
	resp_dict = resp.json()
	sessions_db.set_samplers([ sampler['name'] for sampler in resp_dict if sampler['name'] != 'None'])
	
	# Hardcode.  Upscalers config is messed up.
	#resp = requests.get(UPSCALERS_API_URL)
	#resp_dict = resp.json()
	#g_config['upscalers'] = [ upscaler['model_name'] for upscaler in resp_dict if upscaler['model_name'] is not None]
	sessions_db.set_upscalers([ 'ESRGAN_4x', 'Lanczos', 'Nearest', 'ScuNET GAN', 'ScuNET PSNR', 'SwinIR 4x' ])
	
with app.app_context():
	log = SD_Logger("FlaskServer", logger_levels.INFO)

	log.info(f"Initializing... [{sys.argv[1]} mode]")
	sessions_db = sessions_manager(PROD_DB if sys.argv[1] == 'release' else DEV_DB)
	LoadAPIConfig()
	log.info("Initialization done!")

if __name__ == "__main__":
	release = False
	host_name = "0.0.0.0"
	host_port = "8081"
	if (len(sys.argv) > 1):
		release = sys.argv[1] == 'release'
		host_port = "8080" if release else "8081"
	else:
		print(f"{sys.argv[0]}: release/debug")
		exit(1)

	app.run(host=host_name, port=host_port, debug=(not release), threaded=True)

