#!/usr/bin/python3

import json
import sys
import traceback
import base64
import shutil

sys.path.append('dreamflask')

import os
import time
import requests

from gradio.processing_utils import encode_pil_to_base64, decode_base64_to_image

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from random import randint

from flask import Flask
from flask import request, send_file, escape
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename

from dreamflask.controllers.sessions_manager import sessions_manager
from dreamflask.controllers.page_manager import *
from dreamflask.controllers.image_item import image_item
from dreamflask.libs.montage import create_montage
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.views.error_pages import page_404, share_404
from dreamflask.dream_utils import convert_bytes, generate_options, generate_img2img
from dreamflask.dream_utils import generate_progress, generate_txt2img, generate_upscaling

from dreamflask.dream_consts import *
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

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 ** 8

# Flask globals
sessions_db = None
log = None

class WildcardConverter(BaseConverter):
    regex = r'(|/.*?)'
    weight = 200

app.url_map.converters['wildcard'] = WildcardConverter

def clean_name(name, replace='_'):
	return ''.join( [ c if c.isalnum() or c == "_" or c == "-"  else replace for c in name ] )[:36]

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods = ['GET', 'POST'])
def index():
	session_id = request.form.get('session_id', 'default')

	if (request.method != "POST" or session_id == 'default' or len(session_id) < 1):
		return landing_page(sessions_db)

	user_obj = sessions_db.get_user_by_id(session_id, create=True)
	page_name = request.form.get('page_name', '')
	log.info(f"request.form: {request.form}")
	if user_obj:
		user_obj.page_manager.update_page_item(page_name, request.form, with_form=True)

	log.info(f"Dispatching user '{session_id}' -> {page_name}")
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
	elif (page_name == PROFILE):
		return ProfilePage(session_id)
	elif (page_name == EDITIMAGE):
		return ImagePage(session_id)

	return landing_page(sessions_db)

# TODO
def ProfilePage(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_profile_page_item()
	log.info(f"page_item: {page_item}")
	button = page_item.get('button')
	status_msg = ""

	if (button == 'Update'):
		pass
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		pass

	return profile_page(sessions_db, session_id)

# TODO
def ImagePage(self):
	pass


def Playground(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_playground_page_item()
	button = page_item.get('button')
	files = page_item.get('files', [])
	status_msg = ""

	if (button == 'Add'):
		count = len(files)
		if (count < 1):
			page_item.set('status_msg', 'Select some files')
		for file_hash in files:
			filename = user_info.file_manager.get_filename_by_hash(file_hash)
			src_filename = os.path.basename(filename)
			dest_filename = f"{PLAYGROUND_FOLDER}/{session_id}/{src_filename}"
			try:
				# TODO: Add new file to playground!!!
				status_msg += f"Adding to Playground: {src_filename}<br>"
				os.makedirs(f"{PLAYGROUND_FOLDER}/{session_id}", exist_ok=True)
				shutil.copyfile(filename, dest_filename)
				img_info = user_info.file_manager.add_file(dest_filename)
				user_info.file_manager.generate_thumbnail(img_info)

			except Exception as e:
				log.info(e)
				status_msg += f"Error: {filename} : {e}"
			page_item.set('status_msg', status_msg)
			page_item.set('files', [])
	elif (button== 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.file_manager.remove_file(filename)
		page_item.set('status_msg', f"{len(del_files)} file(s) removed")
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		page_item.set('files', [])
		page_item.update_page_item(page_item)
		user_info.file_manager.refresh()

	return playground_page(sessions_db, session_id)

def CreateThemes(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_themes_page_item()
	button = page_item.get('button')
	
	themes = request.form.getlist('themes')
	theme_prompt = ", ".join(themes)
	if (button == 'Generate'):
		page_item.set('theme_prompt', theme_prompt)
		page_item.set('themes', themes)
		return themes_page(sessions_db, session_id)
	elif (button == 'Reset'):
		page_item.set('theme_prompt', '')
		page_item.set('themes', [])
		return themes_page(sessions_db, session_id)
	elif (button == 'Return'):
		page_item.set('themes', themes)
		return generate_page(sessions_db, session_id)

	## Proud of this one -- flatten a list of lists from a dictionary
	#prompt = ', '.join([ item for sublist in [ request.form.getlist(key) for key in sorted(PROMPT_EXTRAS.keys()) ]  for item in sublist ])

	return themes_page(sessions_db, session_id)

def MakeMontage(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_montage_page_item()
	button = page_item.get('button')

	if (button == 'Reset'):
		page_item.update_page_item({})
		user_info.file_manager.clean_thumbnail_dir()
		user_info.file_manager.update_fileinfos()
		return montage_page(sessions_db, session_id)
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		page_item.update_page_item(request.form, with_form=True)
		user_info.file_manager.refresh()
		return montage_page(sessions_db, session_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Create'):
		image_hashes = request.form.getlist('files')
		workbench_session_folder = f'{WORKBENCH_FOLDER}/{session_id}'
		constrain = page_item.get('constrain', 'false') == 'true'
		cols = int(page_item.get('cols'))
		width = int(page_item.get('width'))
		height = int(page_item.get('height'))

		if (len(image_hashes) < 1):
			page_item.set('status_msg', "How about selecting some files?")
		else:
			# Create montage and drop it in the workbench directory
			try:
				save_filename = f'{workbench_session_folder}/montage-{int(time.time())}.png'
				os.makedirs(f'{workbench_session_folder}', exist_ok=True)
				image_filenames = [ user_info.file_manager.get_filename_by_hash(image_hash) for image_hash in image_hashes ]
				create_montage(save_filename, image_filenames, cols, width, height, 5, 5, 5, 5, 5, constrain)

				img = Image.open(save_filename)
				montage_meta = f"Montage image.  Images: {len(image_hashes)}, Size: {img.width}x{img.height}"
				metadata = PngInfo()
				metadata.add_text("filename", montage_meta)
				img.save(save_filename, pnginfo=metadata)
				img.close()

				img_info = user_info.file_manager.add_file(save_filename)
				user_info.file_manager.generate_thumbnail(img_info)

				img_info = image_item.from_filename(save_filename, session_id, sessions_db._engine)
				img_info.insert_file_info()
				user_info.file_manager.generate_thumbnail(img_info)
				log.info(f"Montage: {img_info}")
				page_item.set('status_msg', f"Montage created.<br><br><a href='/share/{img_info.hash}' title='{img_info.get_title_text(session_id)}' target='_'><img class='img-thumbnail' src='/share/{img_info.thumbnail}' width='128' height='128'></a>")
			except Exception as e:
				log.info(traceback.print_exc())
				page_item.set('status_msg', "Error with montage creation")
	
	return montage_page(sessions_db, session_id)

def UpscaleFile(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_upscale_page_item()
	button = page_item.get('button', '')
	image_hash = page_item.get('upscale_image')

	if (button == "Upscale"):
		if (image_hash == 'none'):
			page_item.set('status_msg', 'Select an image to upscale')
		else:
			img_info = image_item.from_hash(image_hash, session_id, sessions_db._engine)
			save_filename = f'{WORKBENCH_FOLDER}/{session_id}/{int(time.time())}-upscaled-{os.path.basename(img_info.filename)}'
			upscaled_resp = generate_upscaling(page_item, encode_pil_to_base64(Image.open(img_info.filename)))
			upscaled_image = decode_base64_to_image(f"data:image/png;base64,{upscaled_resp['image']}")
			upscaled_image.save(save_filename)
			user_info.file_manager.add_file(save_filename)
			user_info.file_manager.generate_thumbnail(img_info)
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Reset'):
		page_item.update_page_item({})
		user_info.file_manager.clean_thumbnail_dir()
		user_info.file_manager.update_fileinfos()
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		page_item.update_page_item(page_item)
		user_info.file_manager.refresh()

	return upscale_page(sessions_db, session_id)

def CleanUp(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_cleanup_page_item()
	button = page_item.get('button')

	if (button == "Return"):
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		page_item.update_page_item(request.form, with_form=True)
		user_info.file_manager.refresh()
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.file_manager.remove_file(filename)

		page_item.set('status_msg', f"{len(del_files)} file(s) removed")
		user_info.file_manager.refresh()
	return cleanup_page(sessions_db, session_id)

def GenerateStatusMsg(session_id):
	status = ""
	progress_info = generate_progress(session_id)
	# Check if we're working
	state_info = progress_info.get('state', {})
	if (int(state_info.get('sampling_step', 0)) > 0):
		sampling_step = int(state_info.get('sampling_step', 0))
		sampling_steps = int(state_info.get('sampling_steps', 0))
		progress_percent = sampling_step / min(1, sampling_steps)
		log.info(progress_percent)
		status += f"GPU: Rendering {progress_percent}% complete..."
	else:
		status = "GPU: Idle"
	return status

def GenerateImage(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_generate_page_item()

	button = page_item.get('button')
	prompt = page_item.get('prompt')
	seed = int(page_item.get('seed'))
	page_item.set('seed', randint(0, 2**32) if seed < 0 else seed)

	if (button == 'Reset'):
		LoadAPIConfig()
		page_item.update_generate_page_state({})
		user_info.file_manager.clean_thumbnail_dir()
		user_info.file_manager.update_fileinfos()
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		LoadAPIConfig()
		page_item.update_generate_page_state(page_item)
		user_info.file_manager.refresh()
		page_item.set('status_msg', "<br>" + GenerateStatusMsg(session_id))
		return generate_page(sessions_db, session_id)
	elif (button == "Clean Files"):
		return cleanup_page(sessions_db, session_id)
	elif (button == "Upscale"):
		return upscale_page(sessions_db, session_id)
	elif (button == "Upload"):
		return upload_page(sessions_db, session_id)
	elif (button == "Themes"):
		return themes_page(sessions_db, session_id)
	elif (button == "Montage"):
		return montage_page(sessions_db, session_id)
	elif (button == "Playground"):
		return playground_page(sessions_db, session_id)
	elif (button == "Profile"):
		return profile_page(sessions_db, session_id)
	elif (button == "Image Info"):
		return image_page(sessions_db, session_id)
	else: # (button == 'Generate'):
		log.info(f'Generating:')

		[ log.info(f'  {k}: {v}') for k,v in page_item.page_state.items() ]
		session_output_folder = f'{GENERATED_FOLDER}/{clean_name(session_id)}'
		os.makedirs(session_output_folder, exist_ok=True)

		toc = time.time()

		# Update model if the value has changed
		generate_options(page_item)
		if (page_item.get('init_image', 'none') == 'none'):
			generated_resp = generate_txt2img(page_item)
		else:
			image_hash = page_item['init_image']
			file_info = user_info.file_manager.get_filename_by_hash(image_hash)
			generated_resp = generate_img2img(page_item, encode_pil_to_base64(Image.open(file_info.filename)))

		generated_images = generated_resp.get('images', [])
		index = 0
		for image_b64 in generated_images:
			prompt_filename = clean_name(prompt[0:20]) if len(prompt) > 0 else 'BLANK'
			output_filename = f'{session_output_folder}/{prompt_filename}-{index:05}.png'
			# Make sure we don't write over existing images
			while os.path.exists(output_filename):
				index += 1
				output_filename = f'{session_output_folder}/{prompt_filename}-{index:05}.png'
			log.info(f'Saving image to {output_filename}')
			with open(output_filename, "wb") as fp:
				fp.write(base64.b64decode(image_b64))
			img_info = user_info.file_manager.add_file(output_filename)
			user_info.file_manager.generate_thumbnail(img_info)
			
		if (len(generated_images) < 1):
			page_item.set('status_msg', "Failed to generate pictures.  Lower resolution and/or the number of samples.")
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
			page_item.set('status_msg', f"{len(generated_images)} images generated in {time.time() - toc} sec.<br>{infotexts}")

	return generate_page(sessions_db, session_id)

def UploadFile(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_item = user_info.page_manager.get_upload_page_item()
	button = page_item.get('button')

	if (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		LoadAPIConfig()
		page_item.update_page_item(page_item)
		user_info.file_manager.refresh()
		page_item.set('status_msg', "<br>" + GenerateStatusMsg(session_id))
		return upload_page(sessions_db, session_id)
	elif (button == "Clear"):
		page_item.update_page_item(page_item)
		return upload_page(sessions_db, session_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)

	for file_info in request.files.getlist('file'):
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		if file_info.filename == '':
			page_item.set('status_msg', "Select a file, doofus!")
			return upload_page(sessions_db, session_id)

		log.info(f"Uploading file: {file_info.filename}")
		if file_info and allowed_file(file_info.filename):
			os.makedirs(f'{WORKBENCH_FOLDER}/{session_id}', exist_ok=True)
			save_filename = f'{WORKBENCH_FOLDER}/{session_id}/{secure_filename(file_info.filename)}'
			file_info.save(save_filename)
			img_info = user_info.file_manager.add_file(save_filename)
			user_info.file_manager.generate_thumbnail(img_info)
			page_item.set('status_msg', f"File uploaded {file_info.filename}")

	return upload_page(sessions_db, session_id)

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

	log.info(f"Initializing... {sys.argv[1]}")
	sessions_db = sessions_manager(PROD_DB if sys.argv[1] == 'release' else DEV_DB)
	sessions_db.init()
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

