from . import base_pages
from flask import escape
from dream_consts import IMAGE_DIMS
from dreamflask.controllers.sessions_manager import *
from dreamflask.controllers.page_manager import EDITIMAGE

def edit_image_page(sessions_db, user_id, image_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_image_page_item()
	img_info = user_info.file_manager.get_file_info_by_hash(image_id)
	status_msg = page_item.get('status_msg')

	selected_o = 'checked' if img_info.show_owner == 'True' else ''
	selected_i = 'checked' if img_info.show_meta == 'True' else ''

	page = base_pages.header_section("Edit Image Info")
	page += "<body>"
	page += base_pages.navbar_section(f"{user_info.display_name}", user_id)
	page += base_pages.banner_section(f'Status: {status_msg}', page_name='Edit Image Info')

	page += " <form action='/' method='POST' id='image_form'>"
	page += f"	<input type='hidden' name='page_name' value='{EDITIMAGE}'>"
	page += f"	<input type='hidden' name='session_id' value='{user_id}'>"
	page += f"	<input type='hidden' name='image_id' id='image_id' value='{image_id}'>"

	page += base_pages.buttons_section(['Update', 'Return', 'Refresh'])

	page += f"<div class='flex-container' style='flex-direction:column;'>"
	page += f"	<div class='gallery'>"
	page += f"		<div class='gallery-img'>"
	page += f"		 	 <img width=256px style='cursor:auto;max-width:100%' src='/share/{img_info.thumbnail}'></img>"
	page += f"		</div>"
	page += f"	</div>"
	page += f"	<div class='flex-container' style='flex-direction:column;row-gap:4px;'>"
	page += f"		<label style='justify-content:left;'>Title:&nbsp"
	page += f"			<textarea name='title'>{img_info.title}</textarea>"
	page += f"		</label>"
	page += f"		<label style='justify-content:left;'>Meta:&nbsp"
	page += f"			<textarea name='meta'>{img_info.meta}</textarea>"
	page += f"		</label>"
	page += f"		<label style='justify-content:left;'>"
	page += f"			<input type='checkbox' {selected_o} name='show_owner' value='True'>Show Owner</input>"
	page += f"			&nbsp&nbsp"
	page += f"			<input type='checkbox' {selected_i} name='show_meta' value='True'>Show Info</input>"
	page += f"		</label>"
	page += f"	</div>"
	page += f"</div>"

	page += base_pages.buttons_section(['Update', 'Return', 'Refresh'])
	page += "  </form>"

	page += "</div>"
	page += "</body></html>"
	return page
