import glob
import os
import base_pages
from dreamutils import get_hashes, get_uploaded_images, get_generated_images, get_upscaled_images
from flask import escape

def upscale_page(session_info):
	session_id = session_info['session_id']
	file_hashes = session_info['file_hashes']

	page = base_pages.header_section("Upscale")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += f"ESRGAN Upscale image for <b>{session_id}</b><br><br>"
	page += f"Status: { session_info['status_msg'] }<br><br>"
	page += "<h5>Upscale Images -- Could be huge</h5>"

	for image in get_upscaled_images(session_id):
		page += f"<a target='_image' href='/{image}'>{os.path.basename(image)}</a><br>"

	page += "<br>"
	page += f"	<form method='POST' action='/' enctype='multipart/form-data'>"
	page += "		<input type='hidden' name='page_name' value='upscale_page'/>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'/>"
	page += "	Upscale"
	page += "	<div class='form-check form-check-inline'>"
	page += "		<input class='form-check-input' checked type='radio' name='scale' id='scale' value='2'>"
	page += "		<label class='form-check-label' for='scale'>2x</label>"
	page += "	</div>"
	page += "	<div class='form-check form-check-inline'>"
	page += "		<input class='form-check-input' type='radio' name='scale' id='scale' value='4'>"
	page += " 		<label class='form-check-label'>4x</label>"
	page += "	</div>"
	page += "	<div class='form-check form-check-inline'>"
	page += "		<input class='form-check-input' type='checkbox' name='use_gpu' value='true'>"
	page += " 		<label class='form-check-label'>Use GPU (Hopefully)</label>"
	page += "	</div>"

	#page += "	<div class='row g-3'>"
	#page += "		<div class='col-sm'>"
	page += "			<select style='width: 35%;' class='form-select' id='upscale_image' name='upscale_image'>"
	page += "				<option value='none'>Select Image to Upscale</option>"
	for image in (get_generated_images(session_id) + get_uploaded_images(session_id)):
		selected = "selected" if (image == session_info.get('upscale_image', '')) else ""
		page += f"			<option value='{image}' {selected}>{os.path.basename(image)}</option>"
	page += "			</select>"
	#page += "		</div>"
	#page += "	</div>"
	page += "Or"

	page += "	<div class='input-group mb-3 col'>"
	page += "		<input type='file' class='form-control' name='file'>"
	page += "	</div>"
	page += "	<div class='col-12'>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Upscale'>Upscale</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Refresh'>Refresh</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Reset'>Reset</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Return'>Return</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='DeleteAll'>Nuke Upscales!</button>"
	page += "		Confirm Nuke <input type='checkbox' name='confirm'/>"

	page += "<br><br><h5>Generated Images</h5>"
	for file_hash in get_hashes(file_hashes, 'generated'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "<br><br><h5>Uploaded Images</h5>"
	for file_hash in get_hashes(file_hashes, 'uploaded'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "	</div>"
	page += "</form>"
	page += "</div>"
	page += "</body></html>"

	return page
