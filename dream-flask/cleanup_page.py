import base_pages

def cleanup_page(session_info, session_id):
	user_info = session_info.get_user(session_id)
	page_info = user_info.get_cleanup_page_info()
	status_msg = page_info['status_msg']

	page = base_pages.header_section("Clean Up")
	page += "<body>"
	page += base_pages.navbar_section(session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', "Clean Up Images")

	page += "	<form action='/' method='POST' enctype='multipart/form-data'>"
	page += "		<input type='hidden' name='page_name' value='cleanup_page'>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'>"
	page += base_pages.buttons_section(['Delete', 'Return', 'Refresh'])

	page += "		<div class='flex-container' style='gap: 2px;'>"
	page += "			<div style='cursor: pointer;' class='chip' onClick='selectAllImg(\"g_\")'>Invert Generated</div>"
	page += "			<div style='cursor: pointer;' class='chip' onClick='selectAllImg(\"w_\")'>Invert Workbench</div>"
	page += "			<div style='cursor: pointer;' class='chip' onClick='clearCheckboxes()'>Clear Selections</div>"
	page += "		</div>"

	page += base_pages.checkbox_table_section("Generated Images", user_info.filemanager.get_generated_fileinfos(), "g_", selected_list=page_info.get('files'))
	page += base_pages.checkbox_table_section("Workbench Images", user_info.filemanager.get_workbench_fileinfos(), "w_", selected_list=page_info.get('files'))

	page += base_pages.buttons_section(['Delete', 'Return', 'Refresh'])
	page += "	</form>"
	page += "	<br><br><br><br>"
	page += "</div>"
	page += "</body></html>"

	return page
