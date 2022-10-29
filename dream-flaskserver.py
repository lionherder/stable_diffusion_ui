#!/usr/bin/python3

import subprocess
import sys
import traceback

sys.path.append('.'); sys.path.append('dream-flask')

import os
import time
import shelve
import transformers
import torch

from random import randint
from ldm.simplet2i import T2I

from flask import Flask
from flask import request, send_file
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename

from dreamconsts import ALLOWED_EXTENSIONS, UPSCALE_FOLDER, GENERATED_FOLDER, UPLOADS_FOLDER
from dreamutils import get_generated_images, get_uploaded_images, get_upscaled_images, get_filehashes_for_session
from themes_page import themes_page
from generate_page import generate_page
from cleanup_page import cleanup_page
from upscale_page import upscale_page
from landing_page import landing_page
from upload_page import upload_page

app = Flask(__name__, template_folder="dream-flask/templates")
app.config['MAX_CONTENT_LENGTH'] = 10 ** 8
app.config['UPLOAD_FOLDER'] = UPLOADS_FOLDER
app.config['RELEASE'] = True

# Flask globals
t2i = {}
g_sessions = None
g_queue = {}

session_frame = [ "confirm", "use_theme", "button" ]

class WildcardConverter(BaseConverter):
    regex = r'(|/.*?)'
    weight = 200

app.url_map.converters['wildcard'] = WildcardConverter

hostName = "0.0.0.0"
hostPort = 8080 if app.config['RELEASE'] else 8081 

def update_filehashes_for_session(session_info, refresh=False):
	session_id = session_info['session_id']
	session_db = g_sessions[session_id]
	file_hashes = session_db['file_hashes']

	if (refresh):
		session_db['file_hashes'] = {}
		session_info['file_hashes'] = {}

	session_db['file_hashes'] = get_filehashes_for_session(session_info)
	session_info['file_hashes'] = session_db['file_hashes']
	g_sessions[session_id] = session_db
	g_sessions.sync()

	return file_hashes

def update_session_info(session_id, update_request=True):
	"""
	Return session_info and optionally update it with the current request.form info
	"""

	session_id = clean_name(session_id, '')
	print(f"Gathering info for session '{session_id}'")
	if (not session_id or len(session_id) < 1):
		print("PullInfo: Skipping empty session id")
		return {}

	if (session_id not in g_sessions):
		print(f"Creating new db session '{session_id}")
		g_sessions[session_id] = { 'file_hashes' : {} }
		g_sessions.sync()

	if (session_id not in g_queue):
		print(f"Creating new session for '{session_id}")
		g_queue[session_id] = {}

	# Clean out some state items that are local to pages
	for item in session_frame:
		if (item in g_queue[session_id]):
			del g_queue[session_id][item]

	if (update_request):
		print("Updating session info with request form data")
		for k,v in request.form.items():
			print(f"  Updating '{k}' - '{v}'")
			g_queue[session_id][k] = v

	# Gather all info and fill in defaults
	session_info = g_queue.get(session_id)
	session_info['session_id'] = session_id
	session_info['file_hashes'] = g_sessions[session_id]['file_hashes']
	session_info['sampler'] = session_info.get('sampler', 'ddim')
	session_info['page_name'] = session_info.get('page_name', '')
	session_info['prompt'] = session_info.get('prompt', '')
	session_info['theme_prompt'] = session_info.get('theme_prompt', '')
	session_info['button'] = session_info.get('button', '')
	session_info['init_image'] = session_info.get('init_image', 'none')
	session_info['width'] = session_info.get('width', '512')
	session_info['height'] = session_info.get('height', '512')
	session_info['status_msg'] = session_info.get('status_msg', 'Okie Dokie!')
	session_info['model'] = session_info.get('model', 'models/ldm/stable-diffusion/sd-v1-5-pruned.ckpt')
	session_info['steps'] = min(int(session_info.get('steps', 25)), 200)
	session_info['skips'] = min(int(session_info.get('skips', 0)), 199)
	session_info['batch_size'] = min(int(session_info.get('samples', 5)), 20)
	session_info['batches'] = min(int(session_info.get('batches', 1)), 1)
	session_info['seed'] = int(session_info.get('seed', -1))
	session_info['strength'] = float(session_info.get('strength', 0.5))
	session_info['cfg_scale'] = float(session_info.get('cfg_scale', 7.5))
	session_info['ddim_eta'] = float(session_info.get('ddim_eta', 0.0))

	return session_info

def clean_name(name, replace='_'):
	return ''.join( [ c if c.isalnum() or c == "_" or c == "-"  else replace for c in name ] )[:36]

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upscale_image(session_id, filename, scale=2, use_gpu=False, tile=400):
	cmd = []
	if (use_gpu and not g_queue['active']):
		print("Upscaling with GPU")
		t2i.model = None
		t2i.sampler = None
		torch.cuda.empty_cache()
		cmd = ['python', 'inference_realesrgan.py', '-i', filename, '-o', f'{UPSCALE_FOLDER}/{session_id}', '-t', f'{tile}','--fp32', '-s', f'{scale}', '--suffix', 'upscale']
	else:
		print("Upscaling with CPU")
		cmd = ['python', 'inference_realesrgan.py', '-i', filename, '-o', f'{UPSCALE_FOLDER}/{session_id}', '-t', f'{tile}','--fp32', '-s', f'{scale}', '--suffix', 'upscale']
	print(cmd)
	output = subprocess.run(cmd, capture_output=True)
	print(output)	

@app.route("/", methods = ['GET', 'POST'])
def index():
	session_id = request.form.get('session_id', 'default')
	session_info = update_session_info(session_id)

	[ print(f'"{k}" : "{v}"') for k,v in session_info.items() ]

	if (request.method == "GET" or session_id == 'default' or len(session_id) < 1):
		return landing_page(session_info)

	page_name = session_info['page_name']

	if (page_name == "landing"):
		return generate_page(session_info)
	elif (page_name == "generate"):
		return GenerateImage(session_info)
	elif (page_name == "cleanup_page"):
		return CleanUp(session_info)
	elif (page_name == "upscale_page"):
		return UpscaleFile(session_info)
	elif (page_name == "upload_page"):
		return UploadFile(session_info)
	elif (page_name == "themes_page"):
		return CreateThemes(session_info)

	return landing_page(session_info)

def CreateThemes(session_info):
	button = session_info['button']

	themes = request.form.getlist('themes')
	theme_prompt = ", ".join(themes)
	print(themes)
	if (button == 'Generate'):
		session_info['theme_prompt'] = theme_prompt
		session_info['themes'] = themes
		return themes_page(session_info)
	elif (button == 'Reset'):
		session_info['theme_prompt'] = ''
		session_info['themes'] = []
		return themes_page(session_info)
	elif (button == 'Return'):
		session_info['themes'] = themes
		#update_global_info(session_info)
		return generate_page(session_info)

	## Proud of this one -- flatten a list of lists from a dictionary
	#prompt = ', '.join([ item for sublist in [ request.form.getlist(key) for key in sorted(PROMPT_EXTRAS.keys()) ]  for item in sublist ])
	return themes_page(session_info)

def UpscaleFile(session_info):
	session_id = session_info['session_id']
	button = request.form.get('button')

	if (button == 'Reset'):
		if ('upscale_image' in session_info):
			del session_info['upscale_image']
		return upscale_page(session_info)
	elif (button == 'Refresh'):
		if (g_queue['upscaling']):
			session_info['status_msg'] = "Image upscale in progress.  Refresh in a few seconds."
		return upscale_page(session_info)
	elif (button == 'Upscale'):
		image_name = session_info.get('upscale_image')
		upscale_session = f'{UPSCALE_FOLDER}/{session_id}'
		upscale_scale = int(session_info.get('scale', 2))
		use_gpu = True if 'use_gpu' in session_info else False

		# Only allow one upscale at a time.  These are CPU painful.
		if (g_queue['upscaling']):
			session_info['status_msg'] = "Upscale in progress.  Try again in few."
			return upscale_page(session_info)

		# Check if this is an upload or an existing file
		if (image_name and image_name != 'none'):
			print(f"Upscaling existing image: {image_name}")
			filename = image_name
		else:
			# Check if the post request has the file part
			if 'file' not in request.files:
				session_info['status_msg'] = 'No file selected'
				return upscale_page(session_info)

			file = request.files['file']
			# If the user does not select a file, the browser submits an
			# empty file without a filename.
			if file.filename == '':
				session_info['status_msg'] = 'No file selected'
				return upscale_page(session_info)

			if file and allowed_file(file.filename):
				os.makedirs(f'{upscale_session}', exist_ok=True)
				filename = f'{upscale_session}/{secure_filename(file.filename)}'
				file.save(filename)

		# Upscale image and offer link
		toc = time.time()
		while(g_queue['upscaling']):
			print("Waiting for lock...")
			time.sleep(1)
		g_queue['upscaling'] = True
		try:
			upscale_image(session_id, filename, upscale_scale, use_gpu)
			session_info['status_msg'] = "Image upscaled.  Check it out!"
		except Exception as e:
			print(traceback.print_exc())
		g_queue['upscaling'] = False
		g_queue[session_id]['status_msg'] = f'Image scaled in { time.time() - toc} secs'
	elif (button == 'Return'):
		return generate_page(session_info)
	elif (button == 'DeleteAll'):
		if (session_info.get('confirm')):
			session_info['status_msg'] = "Nuked it all!"
			print(f"Deleting all upscale files: {get_upscaled_images(session_id)}")
			[ os.remove(image) for image in get_upscaled_images(session_id) ]
		else:
			session_info['status_msg'] = "Confirm the nuke!"

	return upscale_page(session_info)

def CleanUp(session_info):
	session_id = request.form.get('session_id')
	button = session_info.get('button')

	if (button == "Return"):
		return generate_page(session_info)
	elif (button == "Refresh"):
		update_filehashes_for_session(session_info, refresh=False)
		return cleanup_page(session_info)
	elif (button == 'Nuke It All!'):
		if (not request.form.get('confirm', False)):
			session_info['status_msg'] = "Must Confirm Nuke!"
		else:
			print('Nuking it all!')
			for filename in (get_generated_images(session_id) + get_uploaded_images(session_id)):
				print(f'[{session_id}] Removing: {filename}')
				os.remove(filename)
			session_info['status_msg'] = "Nuked it all!"
	elif (button == 'Delete'):
		del_files = request.form.getlist('files')
		for filename in del_files:
			print(f'[{session_id}] Removing: {filename}')
			os.remove(filename)
		session_info['status_msg'] = f"{len(del_files)} file(s) removed"
	update_filehashes_for_session(session_info, refresh=False)
	return cleanup_page(session_info)

def GenerateImage(session_info):
	session_id = session_info.get("session_id")
	button = session_info['button']
	prompt = session_info['prompt']
	theme_prompt = session_info['theme_prompt']
	seed = session_info['seed']
	model = session_info['model']

	if (button == 'Reset'):
		g_queue[session_id] = { 'session_id' : session_id }
		t2i.model = None
		t2i.sampler = None
		torch.cuda.empty_cache()
		return generate_page(update_session_info(session_id, False))
	elif (button == "Refresh"):
		update_filehashes_for_session(session_info, refresh=False)
		if (g_queue['active']):
			session_info['status_msg'] = "Rendering in progress.  Refresh in a few seconds."
		return generate_page(session_info)
	elif (button == "Clean Files"):
		return cleanup_page(session_info)
	elif (button == "Upscale"):
		return upscale_page(session_info)
	elif (button == "Upload"):
		return upload_page(session_info)
	elif (button == "Themes"):
		return themes_page(session_info)

	if (len(prompt) > 0):
		print(f'Generating:')

		session_info['seed'] = randint(0, 2**32) if seed < 0 else seed
		[ print(f'  {k}: {v}') for k,v in session_info.items() ]
		session_output_folder = f'{GENERATED_FOLDER}/{clean_name(session_id)}'
		os.makedirs(session_output_folder, exist_ok=True)

		toc = time.time()
		generated_images = []
		while(g_queue['active']):
			print("Waiting for lock...")
			time.sleep(2)
		
		if (t2i.weights != model):
			print(f"Loading new Model: {model}")
			t2i.model = None
			t2i.weights = model

		real_prompt = f"{prompt}{', ' + theme_prompt if session_info.get('use_theme', False) else ''}"
		print(f"Full Prompt: {real_prompt}")
		if (app.config['RELEASE'] == True):
			g_queue['active'] = True
			try:
				real_prompt = f"{prompt}{', ' + theme_prompt if session_info.get('use_theme', False) else ''}"
				t2i.sampler_name = session_info['sampler']
				generated_images = t2i.prompt2image(
					real_prompt,
					batch_size=session_info['batch_size'],
					iterations=session_info['batches'],
					init_img=session_info['init_image'] if session_info['init_image'] != 'none' else None,
					width=int(session_info['width']),
					height=int(session_info['height']),
					strength=session_info['strength'],
					steps=session_info['steps'],
					outdir=session_output_folder,
					seed=session_info['seed'],
					ddim_eta=session_info['ddim_eta'],
					cfg_scale=session_info['cfg_scale'],
					grid=False
				)
			except Exception as e:
				print(traceback.print_exc())

			g_queue['active'] = False

			# Save images in the session directory
			index = 0
			for image_info in generated_images:
				prompt_filename = clean_name(prompt[0:20])
				output_filename = f'{session_output_folder}/{prompt_filename}-{index:05}.png'
				while os.path.exists(output_filename):
					index += 1
					output_filename = f'{session_output_folder}/{prompt_filename}-{index:05}.png'
				print(f'Saving image to {output_filename}')
				image_info[0].save(output_filename)

			if (len(generated_images) < 1):
				session_info['status_msg'] = "Failed to generate pictures.  Lower resolution and/or the number of samples."
			else:
				session_info['status_msg'] = f"{len(generated_images)} images generated in {time.time() - toc} sec."
				update_filehashes_for_session(session_info, refresh=False)
		else:
			print("Non-release version.  Skipped Generation.")
			session_info['status_msg'] = "Non-release version.  Skipped Generation."
	else:
		session_info['status_msg'] = "Enter a prompt"

	g_queue[session_id] = session_info.copy()
	return generate_page(session_info)

def UploadFile(session_info):
	session_id = session_info['session_id']
	button = session_info['button']

	if (button == 'Return'):
		return generate_page(session_info)
	elif (button == 'Clean Files'):
		return cleanup_page(session_info)

	# check if the post request has the file part
	if 'file' not in request.files:
		return upload_page(session_info)
	file = request.files['file']
	# If the user does not select a file, the browser submits an
	# empty file without a filename.
	if file.filename == '':
		session_info['status_msg'] = "Select a file, doofus!"
		return upload_page(session_info)

	if file and allowed_file(file.filename):
		os.makedirs(f'{UPLOADS_FOLDER}/{session_id}', exist_ok=True)
		filename = secure_filename(file.filename)
		file.save(f'{UPLOADS_FOLDER}/{session_id}/{filename}')
		session_info['status_msg'] = "File uploaded"

	update_filehashes_for_session(session_info, refresh=False)
	return upload_page(session_info)

@app.route("/share/<string:share_uuid>")
def ShareFile(share_uuid):
	# TODO: Turn this into a global hash that is updated on event instead of
	# traversing the entire list of users for the file hash
	filename = None
	for session_id in g_sessions:
		file_hashes = g_sessions[session_id]['file_hashes'].get(share_uuid)
		if (file_hashes):
			filename = file_hashes['filename']
			break

	if filename and len(filename) > 0 and os.path.isfile(filename):
		return send_file(filename)

	print(f"Share hash doesn't exist: {share_uuid}")
	return ''

@app.route(f"/{UPSCALE_FOLDER}/<string:session_id>/<string:image>")
@app.route(f"/{GENERATED_FOLDER}/<string:session_id>/<string:image>")
@app.route(f"/{UPLOADS_FOLDER}/<string:session_id>/<string:image>")
def ServeFiles(session_id, image):
	filename = request.path[1:]
	if os.path.isfile(filename):
		return send_file(filename)
	if (image and image == 'favicon.ico'):
		return send_file("outputs/favicon.ico")
	print(f"File doesn't exist: {filename}")
	return ''

@app.route("/css/<string:css_file>")
def LoadCSS(css_file):
	return send_file(f"outputs/{css_file}")

@app.route("/js/<string:js_file>")
def LoadJS(js_file):
	return send_file(f"outputs/{js_file}")

@app.route("/favicon.ico")
def LoadFavIcon():
	return send_file("outputs/favicon.ico")

with app.app_context():
	print("* Initializing model, be patient...")
	transformers.logging.set_verbosity_error()
	t2i = T2I(width=512,
			height=512,
			batch_size=1,
			weights='models/ldm/stable-diffusion/model-1-4-ema.ckpt',
			full_precision=True,
			config='configs/stable-diffusion/v1-inference.yaml',
			latent_diffusion_weights=False
	)
	g_queue['active'] = False
	g_queue['upscaling'] = False
	g_sessions = shelve.open('sessions_dev_db')
	print("* Initialization done!")

if __name__ == "__main__":
	app.run(host=hostName, port=hostPort, debug=False, threaded=True)
