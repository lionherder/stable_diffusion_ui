import glob
import os
import base_pages
from flask import escape
from dreamutils import get_hashes, get_uploaded_images

def upload_page(session_info):
	session_id = session_info['session_id']
	file_hashes = session_info['file_hashes']

	page = base_pages.header_section("Upload")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += f"Upload image for <b>{session_id}</b><br><br>"
	page += f"Status: { session_info['status_msg'] }<br><br>"

	page += "<h5>Uploaded Images</h5>"
	for file_hash in get_hashes(file_hashes, 'uploaded'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "<br>"
	page += f"	<form method='POST' action='/' enctype='multipart/form-data'>"
	page += "		<input type='hidden' name='page_name' value='upload_page'/>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'/>"
	page += "	<br><br>"
	page += "	<div class='input-group mb-3 col'>"
	page += "		<input type='file' class='form-control' name='file'>"
	page += "	</div>"
	page += "	<div class='col-12'>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Upload'>Upload</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Return'>Return</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Clean Files'>Clean Files</button>"
	page += "	</div>"
	page += "</form>"
	page += "</div>"
	page += "</body></html>"

	return page
