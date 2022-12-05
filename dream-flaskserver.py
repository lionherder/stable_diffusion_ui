#!/usr/bin/python3

import json
import sys
import traceback
import base64
import shutil

sys.path.append('.'); sys.path.append('dream-flask')

import os
import time
import requests

from gradio.processing_utils import encode_pil_to_base64, decode_base64_to_image

from PIL import Image
from random import randint

from flask import Flask
from flask import request, send_file
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename

from sessions import sessions
from montage import create_montage
from dream_consts import *
from error_pages import page_404, share_404
from dream_utils import generate_options, generate_img2img, convert_bytes
from dream_utils import generate_progress, generate_txt2img, generate_upscaling

from themes_page import themes_page
from generate_page import generate_page
from cleanup_page import cleanup_page
from upscale_page import upscale_page
from landing_page import landing_page
from upload_page import upload_page
from montage_page import montage_page
from playground_page import playground_page

app = Flask(__name__, template_folder="dream-flask/templates")
app.config['MAX_CONTENT_LENGTH'] = 10 ** 8
app.config['RELEASE'] = True

# Flask globals
sessions_db = None

class WildcardConverter(BaseConverter):
    regex = r'(|/.*?)'
    weight = 200

app.url_map.converters['wildcard'] = WildcardConverter

hostName = "0.0.0.0"
hostPort = 8080 if app.config['RELEASE'] else 8080

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

	user_info = sessions_db.get_user(session_id)
	page_name = request.form.get('page_name', '')
	user_info.update_page_info(page_name, request.form, with_form=True)
	user_info.filemanager.update_fileinfos(refresh=True)

	sessions_db.sync()

	print(f"Dispatching user '{session_id}' -> {page_name}")
	if (page_name == "landing_page"):
		return generate_page(sessions_db, session_id)
	elif (page_name == "generate_page"):
		return GenerateImage(session_id)
	elif (page_name == "cleanup_page"):
		return CleanUp(session_id)
	elif (page_name == "upscale_page"):
		return UpscaleFile(session_id)
	elif (page_name == "upload_page"):
		return UploadFile(session_id)
	elif (page_name == "themes_page"):
		return CreateThemes(session_id)
	elif (page_name == "montage_page"):
		return MakeMontage(session_id)
	elif (page_name == "playground_page"):
		return Playground(session_id)

	return landing_page()

def Playground(session_id):
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_playground_page_info()
	button = page_info['button']
	files = page_info.get('files', [])
	status_msg = ""

	if (button == 'Add'):
		count = len(files)
		if (count < 1):
			page_info['status_msg'] = 'Select some files'
		for file_hash in files:
			file_info = user_info.filemanager.get_file_by_hash(file_hash)
			src_filename = os.path.basename(file_info.filename)
			dest_filename = f"{PLAYGROUND_FOLDER}/{session_id}/{src_filename}"
			try:
				status_msg += f"Adding to Playground: {file_info.basename}<br>"
				os.makedirs(f"{PLAYGROUND_FOLDER}/{session_id}", exist_ok=True)
				shutil.copyfile(file_info.filename, dest_filename)
			except Exception as e:
				print(e)
				status_msg += f"Error: {file_info.filename} : {e}"

			user_info.filemanager.update_fileinfos(refresh=True)
			page_info['status_msg'] = status_msg
			page_info['files'] = []
	elif (button== 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.filemanager.remove_file(filename)

		page_info['status_msg'] = f"{len(del_files)} file(s) removed"
		user_info.filemanager.update_fileinfos(clean=True)
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		page_info['files'] = []
		user_info.filemanager.update_fileinfos(refresh=True)
		user_info.update_playground_page_info(page_info)

	return playground_page(sessions_db, session_id)

def CreateThemes(session_id):
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_themes_page_info()
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
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_montage_page_info()
	button = page_info.get('button')

	if (button == 'Reset'):
		user_info.update_montage_page_info({})
		user_info.filemanager.clean_thumbnail_dir(wipe=True)
		user_info.filemanager.update_fileinfos(clean=True)
		return montage_page(sessions_db, session_id)
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		user_info.filemanager.update_fileinfos(refresh=True)
		user_info.update_montage_page_info(request.form, with_form=True)
		return montage_page(sessions_db, session_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Create'):
		image_files = request.form.getlist('files')
		workbench_session_folder = f'{WORKBENCH_FOLDER}/{session_id}'
		constrain = page_info.get('constrain', 'false') == 'true'
		cols = int(page_info.get('cols', 5))
		width = int(page_info.get('width', 256))
		height = int(page_info.get('height', 256))

		if (len(image_files) < 1):
			page_info['status_msg'] = "How about selecting some files?"
		else:
			# Create montage and drop it in the workbench directory
			try:
				save_filename = f'{workbench_session_folder}/montage-{int(time.time())}.png'
				os.makedirs(f'{workbench_session_folder}', exist_ok=True)
				image_filenames = [ user_info.filemanager.get_file_by_hash(image).filename for image in image_files ]
				create_montage(save_filename, image_filenames, cols, width, height, 5, 5, 5, 5, 5, constrain)
				img_info = user_info.filemanager.add_file(save_filename, 'workbench', thumbnail=True)
				user_info.filemanager.update_fileinfos()
				print(f"Montage: {img_info}")
				page_info['status_msg'] = f"Montage created.<br><br><a href='/share/{img_info.hash}' target='_'><img class='img-thumbnail' src='/share/{img_info.thumbnail}' width='128' height='128'></a>"

			except Exception as e:
				print(traceback.print_exc())
				page_info['status_msg'] = "Error with montage creation"
	
	return montage_page(sessions_db, session_id)

def UpscaleFile(session_id):
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_upscale_page_info()
	button = page_info.get('button', '')
	image_hash = page_info['upscale_image']

	if (button == "Upscale"):
		if (image_hash == 'none'):
			page_info['status_msg'] = 'Select an image to upscale'
		else:
			image_fileinfo = user_info.filemanager.get_file_by_hash(image_hash)
			output_filename = f'{WORKBENCH_FOLDER}/{session_id}/{int(time.time())}-upscaled-{os.path.basename(image_fileinfo.filename)}'
			upscaled_resp = generate_upscaling(page_info, encode_pil_to_base64(Image.open(image_fileinfo.filename)))
			upscaled_image = decode_base64_to_image(f"data:image/png;base64,{upscaled_resp['image']}")
			upscaled_image.save(output_filename)
			user_info.filemanager.update_fileinfos(refresh=True)
	elif (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == 'Reset'):
		user_info.update_upscale_page_info({})
		user_info.filemanager.clean_thumbnail_dir(wipe=True)
		user_info.filemanager.update_fileinfos(clean=True)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Refresh'):
		user_info.filemanager.update_fileinfos(refresh=True)
		user_info.update_upscale_page_info(page_info)

	return upscale_page(sessions_db, session_id)

def CleanUp(session_id):
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_cleanup_page_info()
	button = page_info.get('button')

	if (button == "Return"):
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		user_info.update_cleanup_page_info(request.form, with_form=True)
		user_info.filemanager.update_fileinfos(refresh=True)
		return cleanup_page(sessions_db, session_id)
	elif (button == 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			user_info.filemanager.remove_file(filename)

		page_info['status_msg'] = f"{len(del_files)} file(s) removed"
		user_info.filemanager.update_fileinfos(clean=True)
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
		print(progress_percent)
		status += f"GPU: Rendering {progress_percent}% complete..."
	else:
		status = "GPU: Idle"
	return status

def GenerateImage(session_id):
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_generate_page_info()

	button = page_info['button']
	prompt = page_info['prompt']
	seed = int(page_info['seed'])
	page_info['seed'] = randint(0, 2**32) if seed < 0 else seed

	if (button == 'Reset'):
		LoadAPIConfig()
		user_info.update_generate_page_info({})
		user_info.filemanager.clean_thumbnail_dir(wipe=True)
		user_info.filemanager.update_fileinfos(clean=True)
		return generate_page(sessions_db, session_id)
	elif (button == "Refresh"):
		user_info.filemanager.update_fileinfos(refresh=True)
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

	print(f'Generating:')

	[ print(f'  {k}: {v}') for k,v in page_info.items() ]
	session_output_folder = f'{GENERATED_FOLDER}/{clean_name(session_id)}'
	os.makedirs(session_output_folder, exist_ok=True)

	toc = time.time()

	# Update model if the value has changed
	generate_options(page_info)
	if (page_info['init_image'] == 'none'):
		generated_resp = generate_txt2img(page_info)
	else:
		image_hash = page_info['init_image']
		file_info = user_info.filemanager.get_file_by_hash(image_hash)
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
		print(f'Saving image to {output_filename}')
		with open(output_filename, "wb") as fp:
			fp.write(base64.b64decode(image_b64))

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
		user_info.filemanager.update_fileinfos(refresh=True)

	return generate_page(sessions_db, session_id)

def UploadFile(session_id):
	user_info = sessions_db.get_user(session_id)
	page_info = user_info.get_upload_page_info()
	button = page_info['button']

	if (button == 'Return'):
		return generate_page(sessions_db, session_id)
	elif (button == "Clear"):
		user_info.update_cleanup_page_info(page_info)
		return upload_page(sessions_db, session_id)
	elif (button == 'Clean Files'):
		return cleanup_page(sessions_db, session_id)

	for file in request.files.getlist('file'):
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		if file.filename == '':
			page_info['status_msg'] = "Select a file, doofus!"
			return upload_page(sessions_db, session_id)

		print(f"Uploading file: {file.filename}")
		if file and allowed_file(file.filename):
			os.makedirs(f'{WORKBENCH_FOLDER}/{session_id}', exist_ok=True)
			filename = secure_filename(file.filename)
			file.save(f'{WORKBENCH_FOLDER}/{session_id}/{filename}')
			page_info['status_msg'] = "File uploaded"

	user_info.filemanager.update_fileinfos(refresh=True)
	return upload_page(sessions_db, session_id)

@app.route("/share/<string:share_uuid>")
def ShareFile(share_uuid):
	# NOTE: Search scales linarly by number of users.  Not really a problem for me
	filename = None
	for _, user_info in sessions_db.get_users().items():
		file_infos = user_info.filemanager.has_hash(share_uuid)
		if (file_infos):
			filename = file_infos.filename
			break

	if filename and len(filename) > 0 and os.path.isfile(filename):
		#print(f"Sending file: '{filename}' - {convert_bytes(file_infos.size)}")
		return send_file(filename)

	print(f"Share hash doesn't exist: {share_uuid}")
	return share_404(share_uuid), 404

@app.errorhandler(404)
def page_not_found(e):
	page = page_404(str(e))
	return page, 404

@app.errorhandler(400)
def page_error(e):
	print("400: Say hello to my little friend!")
	return send_file('outputs/ewok_beefcake.png'), 400

@app.route("/css/<string:css_file>")
def LoadCSS(css_file):
	#print(f"Loading CSS: {css_file}")
	return send_file(f"{CSS_FILES}/{css_file}")

@app.route("/js/<string:js_file>")
def LoadJS(js_file):
	#print(f"Loading JS: {js_file}")
	return send_file(f"{JS_FILES}/{js_file}")

@app.route("/favicon.ico")
def LoadFavIcon():
	return send_file(FAVICON)

def LoadAPIConfig():
	# Get the models
	resp = requests.get("http://127.0.0.1:7860/sdapi/v1/sd-models")
	resp_dict = resp.json()
	sessions_db.set_models([ os.path.basename(model['title']) for model in resp_dict if model['model_name'] != 'None'])

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
	print("* Initializing model, be patient...")
	sessions_db = sessions('test_sessions_db')
	sessions_db.init()
	LoadAPIConfig()
	print("* Initialization done!")

if __name__ == "__main__":
	app.run(host=hostName, port=hostPort, debug=True, threaded=True)
