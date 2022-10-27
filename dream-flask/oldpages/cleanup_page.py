import glob

import base_pages
from dreamconsts import GENERATED_FOLDER, UPLOADS_FOLDER

def cleanup_page(session_info):
	session_id = session_info['session_id']

	output_images = sorted(glob.glob(f"{GENERATED_FOLDER}/{session_id}/*"))
	upload_images = sorted(glob.glob(f"{UPLOADS_FOLDER}/{session_id}/*"))

	page = ""
	page += "<html><head>"
	page += "  <link rel='stylesheet' href='/css/mystyle.css'>"
	page += "  <title>Stable Diffusion V1.4</title>"
	page += f"  <h2>Cleaning up images for Session '{session_id}'</h2>"
	page += "  <script>"
	page += "      function setCheckboxValue(checkbox, value) { document.getElementById(checkbox).checked = !document.getElementById(checkbox).checked; }"
	page += "  </script>"
	page += "</head><body>"
	page += f"  <form method='POST' action='/'>"
	page += "  <h2>Created Images</h2>"
	page += f"  <input type='hidden' name='session_id' value='{session_id}'>"
	index = 0
	for image in (output_images):
		page += f"<input type='checkbox' id='{index}' name='files' value='{image}'>"
		page += f"<img onclick='setCheckboxValue({index}, true)' src='/{image}' width='128' height='128'></img>"
		page += "</input>"
		index += 1

	page += "<h2>Uploaded Images</h2>"
	for image in (upload_images):
		page += f"<input type='checkbox' id='{index}' name='files' value='{image}'>"
		page += f"<img onclick='setCheckboxValue({index}, true)' src='/{image}' width='128' height='128'></img>"
		page += "</input>"
		index += 1
	page += "    <br><br><input type='submit' name='button' value='Delete'></input>"
	page += "    <input type='submit' name='button' value='Return'></input>"
	page += "</form>"
	page += "</body></html>"

	return page
