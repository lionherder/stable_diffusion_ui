from flask import escape
from dreamconsts import PROMPT_EXTRAS
import base_pages

def themes_page(session_info):
	session_id = session_info.get('session_id')
	theme_prompt = session_info.get('theme_prompt', '')
	themes = session_info.get('themes', [])

	if (len(themes) == 0 and len(theme_prompt) > 0):
		themes = [ theme.strip() for theme in theme_prompt.split(',') ]
	print(f'Themes: {themes}')
	page = base_pages.header_section("Prompt Themes")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += "	<form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='themes_page'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"
	page += "		<label>Theme: </label>"
	page += f"		<input size='120' autofocus value='{escape(theme_prompt)}' name='theme_prompt'>"
	page += "		<br><br>"

	page += "		<div class='table-responsive-xxl'>"
	for theme in sorted(PROMPT_EXTRAS.keys()):
		page += f'<b>{theme.capitalize()}</b>'
		page += "<br>"
		page += "			<table>"
		for prompt in sorted(PROMPT_EXTRAS[theme]):
			checked = 'checked' if prompt in themes else ''
			page += f"			<input type='checkbox' {checked} name='themes' value='{prompt}'/> {prompt}"
		page += "			</table>"
		page += "<br>"
	page += "		</div>"
	page += "	<br>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Generate'>Generate</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Reset'>Reset</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Return'>Return</button>"
	page += "</div>"
	page += "</body></html>"

	return page
