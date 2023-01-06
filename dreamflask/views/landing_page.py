import random

from . import base_pages
from dreamflask.controllers.page_manager import *

def landing_page(session_db):
	pg_images = session_db.get_all_playground_file_infos()
	random.shuffle(pg_images)

	page = base_pages.header_section("Create Session")
	page += "	<body>"
	page += base_pages.navbar_section("", "")
	page += "<form action='/' method='POST'>"
	page += f"	<input type='hidden' name='page_name' value='{LANDING}'/>"
	page += "	<div style='display: flex;align-items: center;padding: 1%;'>"
	page += "		<label style='white-space: nowrap;padding-left: 4px;margin-right: 10px;' for='session_id'>Session Name&nbsp"
	page += "			<input name='session_id' type='text' class='form-control' id='session_id'/>"
	page += "		</label>"
	page += "			<button style='margin: 0.4%;padding: 0.4%;' class='button' type='submit' value='go' name='button'>GO</button>"
	page += "	</div>"
	page += "</form>"
	page += base_pages.image_table_section("Creations", pg_images, session_db, None, show_all=False, limit=25)

	page += "</div>"
	page += "</body></html>"
	return page
