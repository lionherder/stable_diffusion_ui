import glob
from operator import ge
import os
from statistics import mode

import base_pages
from flask import escape
from dreamutils import get_generated_images, get_hashes, get_models_list, get_uploaded_images
from dreamconsts import IMAGE_DIMS

def generate_page(session_info):
	session_id = session_info.get('session_id')
	status_msg = session_info.get('status_msg')
	file_hashes = session_info.get('file_hashes')

	page = base_pages.header_section("Generate")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += f"	<div class='alert alert-dark'>Welcome back, <b>{session_id}</b></div>"
	page += f"	Status: {status_msg}<br>"

	page += " 	<form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='generate'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"

	page += "	<br>"
	page += f"	<textarea onkeydown='if (event.keyCode == 13) {{ this.form.submit(); return false; }}' placeholder='Enter prompt' rows=2 id='prompt' style='width: 40%;' autofocus name='prompt'>{escape(session_info.get('prompt'))}</textarea>"
	page += "	<a onClick='clearPrompt()'>X</a>"

	page += "	<br><br>"
	page += f"      <textarea placeholder='Theme' rows=2 style='width: 40%;' name='theme_prompt'>{escape(session_info.get('theme_prompt', ''))}</textarea>"
	page += f"		<input {'checked' if session_info.get('use_theme', False) else ''} type='checkbox' name='use_theme' value='true'>"
	page += " 		<label> Use Theme</label>"
	page += "	<br><br>"

	page += "	<label>Steps:</label>"
	page += f"	<input size='3' value='{session_info.get('steps')}' name='steps'>"
	
	page += "	<label>Samples:</label>"
	page += f"	<input size='3' value='{session_info.get('batch_size')}' name='samples'>"

	page += "	<label>Prompt Weight:</label>"
	page += f"	<input size='3' value='{session_info.get('cfg_scale')}' name='cfg_scale'>"

	page += "	<label>Seed (-1 = random):</label>"
	page += f"	<input id='seed' size='12' value='{session_info.get('seed')}' name='seed'/>"
	page += "	<a onClick='resetSeed()'>X</a>"

	page += "    <br><br>Width "
	page += "    <select name='width'>"
	for dim in IMAGE_DIMS:
		page += f"     <option value='{dim}' {'selected' if session_info.get('width')==dim else ''}>{dim}</option>"
	page += "    </select>"

	page += " Height "
	page += "    <select id='height' name='height'>"
	for dim in IMAGE_DIMS:
		page += f"     <option value='{dim}' {'selected' if session_info.get('height')==dim else ''}>{dim}</option>"
	page += "    </select>"

	page += "     <label>Strength init_image (0.0 <> 1.0)</label>"
	page += f"    <input size='3' value='{session_info.get('strength')}' name='strength'>"

	page += "     <label>Sampler</label>"
	page += "    <select name='sampler'>"
	for sampler in ['plms', 'ddim', 'k_dpm_2_a', 'k_dpm_2', 'k_euler_a', 'k_euler', 'k_heun', 'k_lms']:
		page += f"     <option value='{sampler}' {'selected' if session_info.get('sampler')==sampler else 'k_euler_a'}>{sampler}</option>"
	page += "    </select>"

	page += "<br><br>"
	page += "    <select id='init_image' name='init_image'>"
	page += "    <option value='none'>No Init Image Selected (Default)</option>"
	for image in (get_generated_images(session_id) + get_uploaded_images(session_id)):
		selected = "selected" if (image == session_info.get('init_image', '')) else ""
		page += f"    <option value='{image}' {selected}>{os.path.basename(image)}</option>"
	page += "    </select>"

	models = sorted(get_models_list(), key = lambda x: x.lower())
	page += "    Model <select id='model' name='model'>"
	for model in models:
		selected = "selected" if (model == session_info.get('model', '')) else ""
		page += f"    <option value='{model}' {selected}>{os.path.basename(model)}</option>"
	page += "    </select>"

	page += "<br><br>"

	page += "    <button class='btn btn-primary' type='submit' name='button' value='Generate'>Generate</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Refresh'>Refresh</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Reset'>Reset</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Upscale'>Upscale</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Upload'>Upload</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Clean Files'>Clean Files</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Themes'>Themes</button>"
	page += "  </form>"
	page += "<br><br>"

	page += "<h5>Generated Images</h5>"
	for file_hash in get_hashes(file_hashes, 'generated'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "<br><br><h5>Uploaded Images</h5>"
	for file_hash in get_hashes(file_hashes, 'uploaded'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "</div>"
	page += "</body></html>"
	return page
