from . import base_pages
from flask import escape
from dream_consts import IMAGE_DIMS
from dreamflask.controllers.sessions_manager import *
from dreamflask.controllers.page_manager import IMAGES

def image_page(sessions_db, session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_image_page_item()
	status_msg = page_info.get('status_msg')

	page = base_pages.header_section("Manage Images")
	page += "<body>"
	page += base_pages.navbar_section(f"{user_info.display_name}", session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', page_name='Manage Images')

	page += " <form action='/' method='POST' id='image_form'>"
	page += f"	<input type='hidden' name='page_name' value='{IMAGES}'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"
	page += f"	<input type='hidden' name='image_id' id='image_id'>"

	page += base_pages.buttons_section(['Update', 'Return', 'Refresh', 'Playground'])
	page += base_pages.editimage_table_section("Playground Images", user_info.file_manager.get_playground_file_infos(), sessions_db, session_id, prefix="p_")
	page += base_pages.editimage_table_section("Generated Images", user_info.file_manager.get_generated_file_infos(), sessions_db, session_id, prefix="g_")
	page += base_pages.editimage_table_section("Workbench Images", user_info.file_manager.get_workbench_file_infos(), sessions_db, session_id, prefix="w_")
	page += base_pages.buttons_section(['Update', 'Return', 'Refresh', 'Playground'])
	page += "  </form>"

	page += "</div>"
	page += "</body></html>"
	return page
