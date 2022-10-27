def upscale_page(session_info):
	session_id = session_info['session_id']
	status_msg = session_info['status_msg']

	page = ""
	page += "<html><head>"
	page += "  <link rel='stylesheet' href='/css/mystyle.css'>"
	page += "  <title>Stable Diffusion V1.4</title>"
	page += "  <h2>ESRGAN Upscale</h2>"
	page += "</head><body>"
	page += "<h2>Upload picture to upscale</h2>"

	page += f"<h3>{status_msg if len(status_msg) > 0 else ''}<h3>"
	page += f"  <form method='POST' action='/upscale/{session_id}' enctype='multipart/form-data'>"
	page += "    <select style='font-size: 1em;' id='scale' name='scale'>"
	page += f"     <option value='2'>2x</option>"
	page += f"     <option value='4'>4x</option>"
	page += f"    </select>"
	page += "    <input type='file' length='10' name='file' class='custom-file-input'>"
	page += "    <input type='submit' value='Upscale'>"
	page += "  </form>"

	page += f"  <form method='POST' action='/'>"
	page += f"    <input type='hidden' name='session_id' value='{session_id}'></input>"
	page += "    <input type='submit' value='Return'></input>"
	page += "  </form>"

	page += "</body></html>"

	return page
