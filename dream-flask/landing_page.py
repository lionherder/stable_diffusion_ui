import random
import base_pages

def landing_page(session_db):
	cols = 5
	pg_images = []
	user_ids = session_db.get_user_session_ids()
	for user_id in user_ids:
		user_info = session_db.get_user(user_id)
		pg_images.extend(user_info.filemanager.get_playground_fileinfos())
	random.shuffle(pg_images)

	page = base_pages.header_section("Create Session")
	page += "	<body>"
	page += base_pages.navbar_section()
	page += "<form action='/' method='POST'>"
	page += "	<input type='hidden' name='page_name' value='landing_page'/>"

	page += "	<div style='display: flex;align-items: center;padding: 1%;'>"
	page += "		<label style='white-space: nowrap;padding-left: 4px;margin-right: 10px;' for='session_id'>Session Name&nbsp"
	page += "			<input name='session_id' type='text' class='form-control' id='session_id'/>"
	page += "		</label>"
	page += "			<button style='padding: 0.5%;' class='button' type='submit' value='go' name='button'>Go</button>"
	page += "	</div>"
	page += "</form>"
	page += base_pages.image_table_section("Creations", pg_images, cols=cols, limit=25)

	page += "</div>"
	page += "</body></html>"
	return page
