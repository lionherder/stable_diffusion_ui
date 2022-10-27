import glob
import os

from flask import escape
from dreamconsts import GENERATED_FOLDER, UPLOADS_FOLDER

def banner_page(session_info):
	session_id = session_info['session_id']

	output_images = sorted(glob.glob(f"{GENERATED_FOLDER}/{session_id}/*"))
	upload_images = sorted(glob.glob(f"{UPLOADS_FOLDER}/{session_id}/*"))

	page = ""
	page += "<html><head>"
	page += "  <link rel='stylesheet' href='/css/mystyle.css'>"
	page += "  <script>"
	page += "    function resetSeed() { document.getElementById('seed').value = -1; }"
	page += "  </script>"
	page += "  <title>Stable Diffusion V1.4</title>"
	page += "  <h2>Stable Diffusion V1.4</h2>"
	page += "</head><body>"
	page += "  <h style='font-size: 1.3em;'>"
	page += "  <form action='/' method='POST'>"

	page += "     <label for='session_id'>Session: </label>"
	page += f"    <input size='17' value='{session_id}' id='session_id' name='session_id'><br><br>"

	page += "     <label for='prompt'>prompt: </label>"
	page += f"    <input size='60' autofocus value='{escape(session_info.get('prompt'))}' id='prompt' name='prompt'>"
	page += "     <a style='font-size: .8em;' href='/prompt' target='_details'> Add details</a><br><br>"

	page += "     <label for='steps'>Steps:</label>"
	page += f"    <input size='3' value='{session_info.get('steps')}' id='steps' name='steps'>"

	page += "     <label>Samples:</label>"
	page += f"    <input size='3' value='{session_info.get('batch_size')}' name='samples'>"

	page += "     <label>Prompt Weight:</label>"
	page += f"    <input size='3' value='{session_info.get('cfg_scale')}' name='cfg_scale'>"
	page += f"    <div class='tooltip'>?<span class='tooltiptext'>Think of this as imagination.  The lower the value, the more imaginative and crazy.  Larger, the more it adheres to the prompt which can be boring.</span></div>"

	#page += "     <label>DDIM ETA:</label>"
	#page += f"    <input size='3' value='{session_info.get('ddim_eta')}' name='ddim_eta'>"
	#page += f"    <div class='tooltip'>?<span class='tooltiptext'>Randomness per image.  0.0 is deterministic.</span></div>"
	page += "<br><br>"

	page += "     <label>Seed (-1 = random):</label>"
	page += f"    <input id='seed' size='12' value='{session_info.get('seed')}' name='seed'/>"
	page += "     <a onClick=\"getElementById('seed').value = '-1';\">X</a>"

	image_dims = [ f'{8 * n}' for n in range(32, 129, 8) ]
	page += "    &nbsp;&nbsp;&nbsp;&nbsp;Width "
	page += "    <select id='width' name='width'>"
	for dim in image_dims:
		page += f"     <option value='{dim}' {'selected' if session_info.get('width')==dim else ''}>{dim}</option>"
	page += "    </select>"
	page += " Height "
	page += "    <select id='height' name='height'>"
	for dim in image_dims:
		page += f"     <option value='{dim}' {'selected' if session_info.get('height')==dim else ''}>{dim}</option>"
	page += "    </select>"
	page += "<br><br>"

	page += "     <label>Strength init_image (0.0 <> 1.0):</label>"
	page += f"    <div class='tooltip'>?<span class='tooltiptext'>Strength of initial image.  Lower means more influlence of initial image.</span></div>"
	page += f"    <input size='3' value='{session_info.get('strength')}' name='strength'>"

	page += "<br><br>"
	page += "    <select id='init_image' name='init_image'>"
	page += "    <option value='none'>No Init Image Selected (Default)</option>"
	for image in (output_images + upload_images):
		selected = "selected" if (image == session_info.get('init_image', '')) else ""
		page += f"    <option value='{image}' {selected}>{os.path.basename(image)}</option>"
	page += "    </select>"
	page += "<br>"

	page += "    <input type='submit' name='button' value='Generate'> "
	page += "    <input type='submit' name='button' value='Reload'> "
	#page += "    <input type='submit' name='button' value='Reset All'>"
	page += "    <input type='submit' name='button' value='Upscale'>"
	page += "    <input type='submit' name='button' value='Clean Files'>"
	page += "  </form>"
	#page += "  <a href='/prompt' target='_details'><button name='details' value='details'>Add Details</button></a>"
	page += "  <br><br>"

	for image in output_images:
#		filename = f"{image}?{int(time.time())}"
		filename = f"{image}"
		page += f"<a target='_image' href='{escape(filename)}'><img src='{escape(filename)}' width='128' height='128'></a> "
	page += f" <h4 style='font-size: .8em;'>{session_info.get('status_msg')}</h4>"

	page += f"  <form method='POST' action='/upload/{session_id}' enctype='multipart/form-data'>"
	page += "    <input type=file length='10' name=file class='custom-file-input'>"
	page += f"    <input type='hidden' name='session_id' value='{session_id}'>"
	page += "    <input type='submit' value='Upload'>"
	page += "  </form>"

	for image in upload_images:
#		filename = f"{image}?{int(time.time())}"
		filename = f"{image}"
		page += f"<a target='_' href='{escape(filename)}'><img src='{escape(filename)}' width='128' height='128'></a> "

	page += "</body></html>"

	return page
