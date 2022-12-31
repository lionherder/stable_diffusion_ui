from . import base_pages

image_selections = {
	'Invert Generated' : 'g_',
	'Invert Workbench' : 'w_',
}

def cleanup_page(sessions_db, session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_cleanup_page_item()
	status_msg = page_info.get('status_msg')

	page = base_pages.header_section("Clean Up")
	page += "<body>"
	page += base_pages.navbar_section(f"{user_info.display_name} / {user_info.user_id}")
	page += base_pages.banner_section(f'Status: {status_msg}', "Clean Up Images")

	page += "	<form action='/' method='POST' enctype='multipart/form-data'>"
	page += "		<input type='hidden' name='page_name' value='cleanup_page'>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'>"

	page += base_pages.buttons_section(['Delete', 'Return', 'Refresh'])
	page += base_pages.image_selection_buttons(image_selections)

	page += base_pages.checkbox_table_section("Generated Images", user_info.file_manager.get_generated_file_infos(), sessions_db, session_id, prefix="g_", selected_list=page_info.get('files'))
	page += base_pages.checkbox_table_section("Workbench Images", user_info.file_manager.get_workbench_file_infos(), sessions_db, session_id, prefix="w_", selected_list=page_info.get('files'))

	page += base_pages.image_selection_buttons(image_selections)
	page += base_pages.buttons_section(['Delete', 'Return', 'Refresh'])
	page += "	</form>"
	page += "	<br><br><br><br>"
	page += "</div>"
	page += "</body></html>"

	return page
