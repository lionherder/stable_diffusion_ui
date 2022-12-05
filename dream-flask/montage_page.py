import base_pages
from dream_consts import IMAGE_DIMS

def montage_page(session_info, session_id):
	user_info = session_info.get_user(session_id)
	page_info = user_info.get_montage_page_info()
	status_msg = page_info['status_msg']

	page = base_pages.header_section("Montage")
	page += "<body>"
	page += base_pages.navbar_section(session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', "Generate Image Montage")

	page += "	<form action='/' method='POST'>"
	page += "		<input type='hidden' name='page_name' value='montage_page'>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'>"

	page += "	<div class='flex-container' style='gap:8px;'>"
	page += base_pages.generate_label_input('Images Per Row', 'cols', page_info.get('cols'), 3)
	page += "	</div>"
	page += "	<div class='flex-container' style='gap:8px;'>"
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

	page += "		<label>Montage Size&nbsp"
	page += f"			<input type='checkbox' {'checked' if page_info.get('constrain') == 'true' else ''} name='constrain' value='true'/>"
	page += "		<label>"
	page += "	</div>"

	page += base_pages.buttons_section(['Create', 'Return', 'Refresh', 'Clean Files', 'Reset'])

	page += "		<div class='flex-container' style='gap: 2px;'>"
	page += "			<div style='cursor: pointer;' class='chip' onClick='selectAllImg(\"g_\")'>Invert Generated</div>"
	page += "			<div style='cursor: pointer;' class='chip' onClick='selectAllImg(\"w_\")'>Invert Workbench</div>"
	page += "			<div style='cursor: pointer;' class='chip' onClick='clearCheckboxes()'>Clear Selections</div>"
	page += "		</div>"

	page += base_pages.checkbox_table_section("Generated Images", user_info.filemanager.get_generated_fileinfos(), "g_", selected_list=page_info.get('files'))
	page += base_pages.checkbox_table_section("Workbench Images", user_info.filemanager.get_workbench_fileinfos(), "w_", selected_list=page_info.get('files'))

	page += "	</form>"
	page += "	</body></html>"

	return page
