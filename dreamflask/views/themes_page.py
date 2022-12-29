from flask import escape
from dream_consts import PROMPT_EXTRAS
from . import base_pages

def themes_page(session_info, session_id):
	user_info = session_info.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_themes_page_info()
	theme_prompt = page_info.get('theme_prompt', '')
	themes = page_info.get('themes')

	if (len(themes) == 0 and len(theme_prompt) > 0):
		themes = [ theme.strip() for theme in theme_prompt.split(',') ]
	print(f'Themes: {themes}')
	page = base_pages.header_section("Prompt Themes")
	page += "	<body>"
	page += base_pages.navbar_section(session_id)

	page += "	<form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='themes_page'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"

	page += "	<div class='flex-container'>"
	page += f"		<textarea onInput=adjustTextAreaHeight() onClick=adjustTextAreaHeight() onkeydown='if (event.keyCode == 13) {{ this.form.submit(); return false; }}' placeholder='Theme Prompt' rows=2 id='theme_prompt' autofocus name='theme_prompt'>{escape(page_info.get('theme_prompt', ''))}</textarea>"
	page += "	</div>"
	page += base_pages.buttons_section(['Generate', 'Return', 'Reset'])

	for theme in sorted(PROMPT_EXTRAS.keys()):
		page += f"<div class='theme-label'>{theme.capitalize()}</div>"
		page += "<div class='theme-container'>"
		for prompt in sorted(PROMPT_EXTRAS[theme]):
			checked = 'checked' if prompt in themes else ''
			page += "	<div class='theme-item' style='margin:0%;'>"
			page += f"		<input type='checkbox' {checked} name='themes' value='{prompt}'/>"
			page += f"		<p style='white-space: nowrap'>{prompt}</p>"
			page += "	</div>"
		page += "</div>"
	page += base_pages.buttons_section(['Generate', 'Return', 'Reset'])
	page += "</div>"
	page += "</body></html>"

	return page
