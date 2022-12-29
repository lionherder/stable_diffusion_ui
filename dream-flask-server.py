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
from random import randint

from sqlalchemy import select

from flask import Flask
from flask import request, send_file, escape
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename
from werkzeug.exceptions import *

from http import HTTPStatus

from dreamflask.controllers.sessions_manager import sessions_manager
from dreamflask.controllers.page_manager import LANDING, GENERATE, UPSCALE, UPLOAD, CLEANUP, THEMES, MONTAGE, PLAYGROUND
from dreamflask.controllers.image_info import image_info
from dreamflask.libs.montage import create_montage
from dreamflask.libs.sd_logger import SD_Logger, logger_levels
from dreamflask.dream_consts import *
from dreamflask.views.error_pages import page_404, share_404
from dreamflask.dream_utils import convert_bytes, generate_options, generate_img2img
from dreamflask.dream_utils import generate_progress, generate_txt2img, generate_upscaling

from dreamflask.views.landing_page import landing_page
from dreamflask.views.generate_page import generate_page
from dreamflask.views.themes_page import themes_page
from dreamflask.views.cleanup_page import cleanup_page
from dreamflask.views.upscale_page import upscale_page
from dreamflask.views.upload_page import upload_page
from dreamflask.views.montage_page import montage_page
from dreamflask.views.playground_page import playground_page
from dreamflask.views.view_page import view_page

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 ** 8
app.config['RELEASE'] = True

# Flask globals
sessions_db = None
log = None

class WildcardConverter(BaseConverter):
    regex = r'(|/.*?)'
    weight = 200

app.url_map.converters['wildcard'] = WildcardConverter

hostName = "0.0.0.0"
hostPort = 8080 if app.config['RELEASE'] else 8081

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

	user_obj = sessions_db.get_user_by_id(session_id)
	page_name = request.form.get('page_name', '')
	user_obj.page_manager.update_page_info(page_name, request.form, with_form=True)
	user_obj.file_manager.update_fileinfos()

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

	return landing_page(sessions_db)

def Playground(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_playground_page_info()
	button = page_info['button']
	files = page_info.get('files', [])
	status_msg = ""

	if (button == 'Add'):
		count = len(files)
		if (count < 1):
			page_info['status_msg'] = 'Select some files'
		for file_hash in files:
			filename = user_info.file_manager.get_filename_by_hash(file_hash)
			src_filename = os.path.basename(filename)
			dest_filename = f"{PLAYGROUND_FOLDER}/{session_id}/{src_filename}"
			try:
				status_msg += f"Adding to Playground: {src_filename}<br>"
				os.makedirs(f"{PLAYGROUND_FOLDER}/{session_id}", exist_ok=True)
				shutil.copyfile(filename, dest_filename)
			except Exception as e:
				log.info(e)
				status_msg += f"Error: {filename} : {e}"
			user_info.file_manager.update_fileinfos()
			page_info['status_msg'] = status_msg
			page_info['files'] = []
	elif (button== 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.file_manager.remove_file(filename)
		page_info['status_msg'] = f"{len(del_files)} file(s) removed"
		user_info.file_manager.update_fileinfos()
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		page_info['files'] = []
		user_info.file_manager.update_fileinfos()
		user_info.page_manager.update_playground_page_info(page_info)

	return playground_page(sessions_db, session_id)

def CreateThemes(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_themes_page_info()
	button = page_info['button']
	
	themes = request.form.getlist('themes')
	theme_prompt = ", ".join(themes)
	if (button == 'Generate'):
		page_info['theme_prompt'] = theme_prompt
		page_info['themes'] = themes
		return themes_page(sessions_db, session_id)
	elif (button == 'Reset'):
		page_info['theme_prompt'] = ''
		page_info['themes'] = []
		return themes_page(sessions_db, session_id)
	elif (button == 'Return'):
		page_info['themes'] = themes
		return generate_page(sessions_db, session_id)

	## Proud of this one -- flatten a list of lists from a dictionary
	#prompt = ', '.join([ item for sublist in [ request.form.getlist(key) for key in sorted(PROMPT_EXTRAS.keys()) ]  for item in sublist ])

	return themes_page(sessions_db, session_id)

def MakeMontage(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_montage_page_info()
	button = page_info.get('button')

	if (button == 'Reset'):
		user_info.page_manager.update_montage_page_info({})
		user_info.file_manager.clean_thumbnail_dir()
		user_info.file_manager.update_fileinfos()
		return montage_page(sessions_db, session_id)
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		user_info.file_manager.update_fileinfos()
		user_info.page_manager.update_montage_page_info(request.form, with_form=True)
		return montage_page(sessions_db, session_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Create'):
		image_hashes = request.form.getlist('files')
		workbench_session_folder = f'{WORKBENCH_FOLDER}/{session_id}'
		constrain = page_info.get('constrain', 'false') == 'true'
		cols = int(page_info.get('cols', 5))
		width = int(page_info.get('width', 256))
		height = int(page_info.get('height', 256))

		if (len(image_hashes) < 1):
			page_info['status_msg'] = "How about selecting some files?"
		else:
			# Create montage and drop it in the workbench directory
			try:
				save_filename = f'{workbench_session_folder}/montage-{int(time.time())}.png'
				os.makedirs(f'{workbench_session_folder}', exist_ok=True)
				image_filenames = [ user_info.file_manager.get_filename_by_hash(image_hash) for image_hash in image_hashes ]
				create_montage(save_filename, image_filenames, cols, width, height, 5, 5, 5, 5, 5, constrain)
				img_info = user_info.file_manager.add_file(save_filename)
				user_info.file_manager.generate_thumbnail(img_info)
				img_info.refresh_info()
				user_info.file_manager.update_fileinfos()
				log.info(f"Montage: {img_info}")
				page_info['status_msg'] = f"Montage created.<br><br><a href='/share/{img_info.hash}' target='_'><img class='img-thumbnail' src='/share/{img_info.thumbnail}' width='128' height='128'></a>"
			except Exception as e:
				log.info(traceback.print_exc())
				page_info['status_msg'] = "Error with montage creation"
	
	return montage_page(sessions_db, session_id)

def UpscaleFile(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_upscale_page_info()
	button = page_info.get('button', '')
	image_hash = page_info['upscale_image']

	if (button == "Upscale"):
		if (image_hash == 'none'):
			page_info['status_msg'] = 'Select an image to upscale'
		else:
			img_info = image_info.from_hash(image_hash, session_id, sessions_db._engine)
			save_filename = f'{WORKBENCH_FOLDER}/{session_id}/{int(time.time())}-upscaled-{os.path.basename(img_info.filename)}'
			upscaled_resp = generate_upscaling(page_info, encode_pil_to_base64(Image.open(img_info.filename)))
			upscaled_image = decode_base64_to_image(f"data:image/png;base64,{upscaled_resp['image']}")
			upscaled_image.save(save_filename)
			user_info.file_manager.add_file(save_filename)
			user_info.file_manager.generate_thumbnail(img_info)
			user_info.file_manager.update_fileinfos()
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Reset'):
		user_info.page_manager.update_upscale_page_info({})
		user_info.file_manager.clean_thumbnail_dir()
		user_info.file_manager.update_fileinfos()
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		user_info.file_manager.update_fileinfos()
		user_info.page_manager.update_upscale_page_info(page_info)

	return upscale_page(sessions_db, session_id)

def CleanUp(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_cleanup_page_info()
	button = page_info.get('button')

	if (button == "Return"):
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		user_info.page_manager.update_cleanup_page_info(request.form, with_form=True)
		user_info.file_manager.update_fileinfos()
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.file_manager.remove_file(filename)

		page_info['status_msg'] = f"{len(del_files)} file(s) removed"
		user_info.file_manager.update_fileinfos()
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
	page_info = user_info.page_manager.get_generate_page_info()

	button = page_info['button']
	prompt = page_info['prompt']
	seed = int(page_info['seed'])
	page_info['seed'] = randint(0, 2**32) if seed < 0 else seed

	if (button == 'Reset'):
		LoadAPIConfig()
		user_info.page_manager.update_generate_page_info({})
		user_info.file_manager.clean_thumbnail_dir()
		user_info.file_manager.update_fileinfos()
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		LoadAPIConfig()
		user_info.file_manager.update_fileinfos()
		page_info['status_msg'] += "<br>" + GenerateStatusMsg(session_id)
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
	else: # (button == 'Generate'):
		log.info(f'Generating:')

		[ log.info(f'  {k}: {v}') for k,v in page_info.items() ]
		session_output_folder = f'{GENERATED_FOLDER}/{clean_name(session_id)}'
		os.makedirs(session_output_folder, exist_ok=True)

		toc = time.time()

		# Update model if the value has changed
		generate_options(page_info)
		if (page_info['init_image'] == 'none'):
			generated_resp = generate_txt2img(page_info)
		else:
			image_hash = page_info['init_image']
			file_info = user_info.file_manager.get_filename_by_hash(image_hash)
			generated_resp = generate_img2img(page_info, encode_pil_to_base64(Image.open(file_info.filename)))

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
			img_info = image_info.from_filename(output_filename, session_id, sessions_db._engine)
			img_info.insert_file_info()
			user_info.file_manager.generate_thumbnail(img_info)
			
		if (len(generated_images) < 1):
			page_info['status_msg'] = "Failed to generate pictures.  Lower resolution and/or the number of samples."
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
			page_info['status_msg'] = f"{len(generated_images)} images generated in {time.time() - toc} sec.<br>{infotexts}"
			user_info.file_manager.update_fileinfos()

	return generate_page(sessions_db, session_id)

def UploadFile(session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_upload_page_info()
	button = page_info['button']

	if (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		LoadAPIConfig()
		user_info.file_manager.update_fileinfos()
		page_info['status_msg'] += "<br>" + GenerateStatusMsg(session_id)
		return upload_page(sessions_db, session_id)
	elif (button == "Clear"):
		user_info.page_manager.update_cleanup_page_info(page_info)
		return upload_page(sessions_db, session_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)

	for file in request.files.getlist('file'):
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		if file.filename == '':
			page_info['status_msg'] = "Select a file, doofus!"
			return upload_page(sessions_db, session_id)

		log.info(f"Uploading file: {file.filename}")
		if file and allowed_file(file.filename):
			os.makedirs(f'{WORKBENCH_FOLDER}/{session_id}', exist_ok=True)
			filename = secure_filename(file.filename)
			file.save(f'{WORKBENCH_FOLDER}/{session_id}/{filename}')
			page_info['status_msg'] = "File uploaded"

	user_info.file_manager.update_fileinfos()
	return upload_page(sessions_db, session_id)

@app.route("/share/<string:share_uuid>")
def ShareFile(share_uuid):
	pass_thru = False
	
	log.info(f"Sharing request: {share_uuid}")
	if (share_uuid[-3:] == '-PT'):
		share_uuid = share_uuid[:-3]
		log.info(f"  -- pass_thru file: {share_uuid}")
		pass_thru = True

	img_info = sessions_db.get_image_info_by_hash(share_uuid)

	#log.info(f"img_info: {img_info}")
	if img_info:
		if not img_info.exists():
			log.info(f"  - file doesn't exist for hash: {share_uuid}")
			return share_404(share_uuid), 404
		elif pass_thru:
			# Send it on through if it's an -ST file
			return send_file(img_info.filename)
		elif not img_info.is_thumbnail():
			log.info(f"  - view page: '{img_info.filename}' - {convert_bytes(img_info.size)}")
			return view_page(img_info)
		else:
			return send_file(img_info.filename)

	return not_found_404()

@app.errorhandler(404)
def not_found_404(e=None):
	banner = "<div class='error_404'>"
	banner = "	<img width='90%' height='5%' src='/images/404_lost.png'></img>"
	banner += f"<p>404 Not Found</p>"
	banner += f"<p>Sorry, the AI was unable to find the file you are looking for</p>"
	banner += "</div>"
	page = page_404(banner)
	return page, 404

# TODO: Can't intercept 400's.  Lame.
#@app.errorhandler(400)
#def bad_request_400(e):
#	banner = "<div class='error_404'>"
#	banner = "	<img width='90%' height='5%' src='/images/404_lost.png'></img>"
#	banner += f"<p>400 Busted</p>"
#	banner += "</div>"
#	page = page_404(banner)
#	return page, 400

@app.route("/css/<string:css_file>")
def LoadCSS(css_file):
	filename = f"{CSS_FILES}/{css_file}"
	#log.info(f"Loading CSS: {css_file}")
	if (not os.path.exists(filename)):
		return page_not_found()
	else:
		return send_file(f"{CSS_FILES}/{css_file}")

@app.route("/js/<string:js_file>")
def LoadJS(js_file):
	filename = f"{JS_FILES}/{js_file}"
	#log.info(f"Loading JS: {js_file}")
	if (not os.path.exists(filename)):
		return page_not_found()
	else:
		return send_file(filename)

@app.route("/images/<string:img_file>")
def LoadImage(img_file):
	filename = f"{IMG_FILES}/{img_file}"
	log.info(f"Sending Image: {img_file}")
	if (not os.path.exists(filename)):
		return page_not_found()
	return send_file(f"{IMG_FILES}/{img_file}")

@app.route("/favicon.ico")
def LoadFavIcon():
	return send_file(FAVICON)

def LoadAPIConfig():
	# Get the models
	resp = requests.get("http://127.0.0.1:7860/sdapi/v1/sd-models")
	resp_dict = resp.json()
	sessions_db.set_models([ f"{os.path.basename(model['title'])}" for model in resp_dict if model['model_name'] != 'None'])

	# Get the samplers
	resp = requests.get("http://127.0.0.1:7860/sdapi/v1/samplers")
	resp_dict = resp.json()
	sessions_db.set_samplers([ sampler['name'] for sampler in resp_dict if sampler['name'] != 'None'])
	
	# Hardcode.  Upscalers config is messed up.
	#resp = requests.get("http://127.0.0.1:7860/sdapi/v1/upscalers")
	#resp_dict = resp.json()
	#g_config['upscalers'] = [ upscaler['model_name'] for upscaler in resp_dict if upscaler['model_name'] is not None]
	sessions_db.set_upscalers([ 'ESRGAN_4x', 'Lanczos', 'Nearest', 'ScuNET GAN', 'ScuNET PSNR', 'SwinIR 4x' ])
	
with app.app_context():
	log = SD_Logger("FlaskServer", logger_levels.INFO)

	log.info("Initializing...")
	sessions_db = sessions_manager(PROD_DB if app.config['RELEASE'] else DEV_DB)
	sessions_db.init()
	LoadAPIConfig()
	log.info("Initialization done!")

if __name__ == "__main__":
	app.run(host=hostName, port=hostPort, debug=False, threaded=True)
