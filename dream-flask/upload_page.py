import base_pages

def upload_page(session_db, session_id):
	user_info = session_db.get_user(session_id)
	page_info = user_info.get_upload_page_info()
	status_msg = page_info['status_msg']

	page = base_pages.header_section("Upload")
	page += "<body>"
	page += base_pages.navbar_section(session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', "Upload Images")

	page += f"	<form method='POST' action='/' enctype='multipart/form-data'>"
	page += "		<input type='hidden' name='page_name' value='upload_page'/>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'/>"

	page += f"		<div class='file-input'>"
	page += "			<input accept='.jpg, .png' class='file' multiple id='file' type='file' name='file'>"
	page += "			<label for='file'>Select Files</label>"
	page += "				<div id='file-selections'>"
	#page += "					<div class='file-selection'>"
	#page += "						<div class='file-name' id='file-name'>00114-1312200173-midjourneyart___.png - 421.74</div>"
	#page += "					</div>"
	#page += "					<div class='file-selection'>"
	#page += "						<div class='file-name' id='file-name'>00114-1312200173-midjourneyart___.png - 421.74</div>"
	#page += "					</div>"
	page += "				</div>"
	page += f"			</label>"
	page += f"		</div>"

	page += "<br>"
	page += base_pages.buttons_section(['Upload', 'Return', 'Clear', 'Clean Files'])
	page += "	</form>"

	page += base_pages.workbench_images_section(user_info.filemanager.get_workbench_fileinfos())

	page += "</div>"
	page += "</body></html>"

	return page
