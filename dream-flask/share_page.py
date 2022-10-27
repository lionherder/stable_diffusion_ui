from flask import escape
from dreamutils import get_generated_images, get_hashes, get_uploaded_images
import base_pages
import uuid
import os

def share_page(session_info):
	session_id = session_info.get('session_id')
	status_msg = session_info.get('status_msg')
	file_hashes = session_info.get('file_hashes')

	page = base_pages.header_section("Prompt Themes")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += f"Share image URL for <b>{session_id}</b><br><br>"
	page += f"	Status: {status_msg}<br>"

	page += " 	<form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='share'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"

	page += "<br>"
	page += "<h5>Generated Images</h5>"
	for file_hash in get_hashes(file_hashes, 'generated'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "<br><br>"
	page += "<h5>Uploaded Images</h5>"
	for file_hash in get_hashes(file_hashes, 'uploaded'):
		file_info = file_hashes.get(file_hash)
		page += f"<a target='_output' title='{os.path.basename(file_info['filename'])}' href='/share/{file_hash}'>"
		page += f"  <img class='img-thumbnail' src='/share/{file_hash}' width='128' height='128'></a>"

	page += "<br><br>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Refresh'>Refresh</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Reset'>Reset</button>"
	page += "    <button class='btn btn-primary' type='submit' name='button' value='Return'>Return</button>"

	page += "</div>"
	page += "</body></html>"

	return page

'''
'sessions' -> {
	'session_id_1' -> {
		'file_hashes' -> {
			'uuid' -> {
				'filename' : filename,
				'ctime' : os.path.getctime(filename),
				'atime' : os.path.getatime(filename),
				'mtime' : os.path.getmtime(filename),
				'size' : os.path.getsize(filename)
			}, ...
		}
	},
	'session_id_2' -> { ... },
	'session_id_3' -> { ... },
}
'''