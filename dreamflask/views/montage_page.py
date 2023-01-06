from . import base_pages
from dream_consts import IMAGE_DIMS

image_selections = {
	'Invert Generated' : 'g_',
	'Invert Workbench' : 'w_',
}

def montage_page(sessions_db, session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_montage_page_item()
	status_msg = page_info.get('status_msg')

	page = base_pages.header_section("Montage")
	page += "<body>"
	page += base_pages.navbar_section(f"{user_info.display_name}", session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', "Gonna Make a Montage")

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

	page += base_pages.buttons_section(['Create', 'Return', 'Refresh', 'Clean Files', 'Clear'])
	page += base_pages.image_selection_buttons(image_selections)

	page += base_pages.checkbox_table_section("Generated Images", user_info.image_manager.get_generated_file_infos(), sessions_db, session_id, prefix="g_", selected_list=page_info.get('files'))
	page += base_pages.checkbox_table_section("Workbench Images", user_info.image_manager.get_workbench_file_infos(), sessions_db, session_id, prefix="w_", selected_list=page_info.get('files'))

	page += base_pages.image_selection_buttons(image_selections)
	page += base_pages.buttons_section(['Create', 'Return', 'Refresh', 'Clean Files', 'Clear'])


	page += "	</form>"
	page += "	</body></html>"

	return page
