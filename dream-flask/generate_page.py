import os

import base_pages
from flask import escape
from dream_consts import IMAGE_DIMS

def generate_page(session_info, session_id):
	user_info = session_info.get_user(session_id)
	page_info = user_info.get_generate_page_info()
	status_msg = page_info.get('status_msg')

	page = base_pages.header_section("Generate")
	page += "<body>"
	page += base_pages.navbar_section(session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', page_name='Generate Image')

	page += " <form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='generate_page'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"

	page += "	<div class='flex-container'>"
	page += f"		<textarea onInput=adjustTextAreaHeight() onClick=adjustTextAreaHeight() onkeydown='if (event.keyCode == 13) {{ this.form.submit(); return false; }}' placeholder='Prompt' rows=2 id='prompt' autofocus name='prompt'>{escape(page_info.get('prompt', ''))}</textarea>"
	page += "		<a class='button' onClick='clearPrompt()'>X</a>"
	page += "	</div>"

	page += "	<div class='flex-container'>"
	page += f"		<textarea onInput=adjustTextAreaHeight() onClick=adjustTextAreaHeight() onkeydown='if (event.keyCode == 13) {{ this.form.submit(); return false; }}' placeholder='Negative Prompt' rows=2 name='neg_prompt' id='neg_prompt'>{escape(page_info.get('neg_prompt', ''))}</textarea>"
	page += "		<a class='button' onClick='clearNegPrompt()'>X</a>"
	page += "	</div>"

	# Line 1
	page += "	<div class='flex-container' style='flex-wrap:wrap;gap:8px;'>"
	page += base_pages.generate_label_input('Steps', 'steps', page_info.get('steps'), 3)
	page += base_pages.generate_label_input('Samples', 'samples', page_info.get('samples'), 3)
	page += base_pages.generate_label_input('Prompt Weight', 'cfg_scale', page_info.get('cfg_scale'), 3)
	page += f"		<label>Seed&nbsp"
	page += f"			<input size='12' value='{page_info.get('seed')}' name='seed' id='seed'>"
	page += "			<a class='button' style='padding: 2px;'onClick='resetSeed()'>x</a>"
	page += "		</label>"
	page += "	</div>"

	# Line 2
	page += "	<div class='flex-container' style='flex-wrap:wrap;gap:8px;'>"
	page += "		<label>Width&nbsp"
	page += "			<select id='width' name='width'>"
	for dim in IMAGE_DIMS:
		page += f"			<option value='{dim}' {'selected' if page_info.get('width')==dim else ''}>{dim}</option>"
	page += "			</select>"
	page += "		</label>"

	page += "		<label>Height&nbsp"
	page += "			<select id='height' name='height'>"
	for dim in IMAGE_DIMS:
		page += f"			<option value='{dim}' {'selected' if page_info.get('height')==dim else ''}>{dim}</option>"
	page += "			</select>"
	page += "		</label>"

	models = sorted(session_info.get_models(), key = lambda x: x.lower())
	page += "		<label>Model&nbsp"
	page += "			<select id='model' name='model'>"
	for model in models:
		crop_model = os.path.basename(model).split('.')[0]
		selected = "selected" if (model == page_info.get('model', '')) else ""
		page += f"			<option value='{model}' {selected}>{crop_model}</option>"
	page += "			</select>"
	page += "		</label>"

	page += "		<label>Sampler&nbsp"
	page += "			<select id='sampler' name='sampler'>"
	for sampler in session_info.get_samplers():
		page += f"			<option value='{sampler}' {'selected' if page_info.get('sampler')==sampler else 'k_euler_a'}>{sampler}</option>"
	page += "			</select>"
	page += "		</label>"
	page += "	</div>"

	# Line 3
	page += "	<div class='flex-container' style='flex-wrap:wrap;gap:8px;'>"
	page += "		<label>Init Image&nbsp"
	page += "			<select style='id='init_image' name='init_image'>"
	page += "				<option value='none'>No Init Image</option>"
	for file_info in (user_info.filemanager.get_generated_fileinfos() + user_info.filemanager.get_workbench_fileinfos()):
		selected = "selected" if (file_info.hash == page_info.get('init_image', '')) else ""
		page += f"			<option value='{file_info.hash}' {selected}>{os.path.basename(file_info.filename)}</option>"
	page += "			</select>"
	page += "		</label>"
	page += base_pages.generate_label_input('Influence [Less <0.0 - 1.0> More]', 'strength', page_info.get('strength'), 3)
	page += "	</div>"
	page += base_pages.buttons_section(['Generate', 'Refresh', 'Reset', 'Upscale', 'Upload',  'Clean Files', 'Themes', 'Montage', 'Playground'])
	page += "  </form>"

	page += base_pages.generated_images_section(user_info.filemanager.get_generated_fileinfos(), cols=int(page_info['cols']))
	page += base_pages.workbench_images_section(user_info.filemanager.get_workbench_fileinfos(), cols=int(page_info['cols']))

	page += "</div>"
	page += "</body></html>"
	return page
