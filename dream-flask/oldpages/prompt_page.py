from flask import Flask
from flask import request, escape
from dreamconsts import PROMPT_EXTRAS

def prompt_page(session_info):
	page = ""
	page += "<html><head>"
	page += "  <link rel='stylesheet' href='/css/mystyle.css'>"
	page += "  <script>"
	page += "    function selectText() { var selectText = document.getElementById('prompt'); selectText.select(); }"
	page += "  </script>"
	page += "  <title>Stable Diffusion V1.4</title>"
	page += "  <h2>Stable Diffusion V1.4</h2>"
	page += "</head><body>"
	page += "  <h style='font-size: 1em;'>"
	page += "  <form action='/prompt' method='POST'>"

	page += "     <label for='prompt'>prompt: </label>"
	page += f"    <input size='120' autofocus value='{escape(session_info.get('prompt', ''))}' id='prompt' name='prompt'>"
	page += "     <a onclick='selectText()'>Select text</a>"
	page += "     <br><br>"

	for extra in sorted(PROMPT_EXTRAS.keys()):
		page += f'{extra.capitalize()}'
		page += "<p>"
		items = request.form.getlist(extra)
		for item in sorted(PROMPT_EXTRAS[extra]):
			page += f"  <input type='checkbox' {'checked' if item in items else ''} name='{extra}' value='{item}'>{item}"
		page += "</p>"

	page += "    <input type='submit' name='button' value='Generate'> "
	#page += "    <input type='submit' name='button' value='Return'> "

	return page
