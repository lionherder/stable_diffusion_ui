from flask import escape
from dream_consts import PROMPT_EXTRAS
import base_pages

def themes_page(session_info, session_id):
	user_info = session_info.get_user(session_id)
	page_info = user_info.get_themes_page_info()
	theme_prompt = page_info.get('theme_prompt', '')
	themes = page_info.get('themes')

	if (len(themes) == 0 and len(theme_prompt) > 0):
		themes = [ theme.strip() for theme in theme_prompt.split(',') ]
	print(f'Themes: {themes}')
	page = base_pages.header_section("Prompt Themes")
	page += "	<body>"
	page += base_pages.navbar_section(session_id)

	page += "<div class='flex-container'>"
	page += "	<form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='themes_page'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"
	page += base_pages.generate_label_input("Theme", 'theme_prompt', escape(theme_prompt), 120)
	page += "</div>"

	for theme in sorted(PROMPT_EXTRAS.keys()):
		page += "<div class='flex-container' style='align-items: center;flex-wrap: wrap;flex-direction: row;'>"
		page += f"	<b>{theme.capitalize()}</b>"
		for prompt in sorted(PROMPT_EXTRAS[theme]):
			checked = 'checked' if prompt in themes else ''
			page += "<div class='flex-container' style='height: 12px;flex-direction: row;align-items: center;gap: 2px;'>"
			page += f"	<input type='checkbox' {checked} name='themes' value='{prompt}'/>"
			page += f"	<p style='padding: 0px; white-space: nowrap'>{prompt}</p>"
			page += "</div>"
		page += "</div>"
	page += base_pages.buttons_section(['Generate', 'Return', 'Reset'])
	page += "</div>"
	page += "</body></html>"

	return page
