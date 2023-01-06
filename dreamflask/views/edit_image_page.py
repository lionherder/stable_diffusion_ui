from . import base_pages
from flask import escape
from dreamflask.dream_consts import *
from dreamflask.dream_utils import *
from dreamflask.controllers.sessions_manager import *
from dreamflask.controllers.page_manager import EDITIMAGE

log = SD_Logger("EditImagePage", logger_levels.INFO)

def edit_image_page(sessions_db, user_id, image_id):
	user_info = sessions_db.get_user_by_id(user_id)
	page_item = user_info.page_manager.get_image_page_item()
	img_item = user_info.image_manager.get_file_item_by_hash(image_id)
	status_msg = page_item.get('status_msg')
	title = img_item.get_title_text(viewer_id=user_id)

	meta_decrypt = img_item.meta # decrypt_text(img_info.meta, sessions_db._private_key)

	selected_o = 'checked' if img_item.show_owner else ''
	selected_i = 'checked' if img_item.show_meta else ''
	visible = 'checked' if img_item.is_visible else ''

	page = base_pages.header_section("Edit Image Info")
	page += "<body>"
	page += base_pages.navbar_section(f"{user_info.display_name}", user_id)
	page += base_pages.banner_section(f'Status: {status_msg}', page_name='Edit Image Info')

	page += " <form action='/' method='POST' id='image_form'>"
	page += f"	<input type='hidden' name='page_name' value='{EDITIMAGE}'>"
	page += f"	<input type='hidden' name='session_id' value='{user_id}'>"
	page += f"	<input type='hidden' name='image_id' id='image_id' value='{image_id}'>"

	page += f"	<div class='gallery' style='flex-direction:column'>"
	page += f"		<div class='gallery-img'>"
	page += f"		 	 <img title='{title}' width=256px style='cursor:auto;max-width:100%' src='/share/{img_item.thumbnail}'></img>"
	page += f"		</div>"
	page += f"		<div class='gallery-img'>"
	page += f"				<a target='_' href='{SHARE_URL}/{img_item.id}' style='text-decoration: none;color: #444;'>{img_item.id}</a>"
	page += f"		</div>"
	page += f"	</div>"

	page += f"	<div class='flex-row'>"
	page += f"			<textarea onInput=adjustTextAreaHeight() onClick=adjustTextAreaHeight() placeholder='Title' name='title'>{img_item.title}</textarea>"
	page += f"	</div>"
	page += f"	<div class='flex-row'>"
	page += f"			<textarea onInput=adjustTextAreaHeight() onClick=adjustTextAreaHeight() placeholder='Meta' name='meta'>{meta_decrypt}</textarea>"
	page += f"	</div>"
	page += f"	<div class='flex-container' style='flex-direction:row;margin:0px 0px 0px 1.2%;gap:4px;'>"
	page += f"		<label style='padding: 2px 8px 2px 2px'>"
	page += f"			<input type='checkbox' {selected_o} name='show_owner' value='True'>Show Owner</input>"
	page += f"		</label>"
	page += f"		<label style='padding: 2px 8px 2px 2px'>"
	page += f"			<input type='checkbox' {selected_i} name='show_meta' value='True'>Show Info</input>"
	page += f"		</label>"
	page += f"		<label style='padding: 2px 8px 2px 2px'>"
	page += f"			<input type='checkbox' {visible} name='is_visible' value='True'>Visible</input>"
	page += f"		</label>"
	page += f"	</div>"

	page += base_pages.buttons_section(['Update', 'Return', 'Refresh', 'Reset URL', 'Delete'])

	#page += "	<div class='page-title' style=''>"
	page += "		<div class='page-title' style='font-size:small;text-align:left;'>"
	page += "			Title: Always shown if present.  Leave blank to disable.<br>"
	page += "			Show Owner: Name will be shown to others on hover.<br>"
	page += "			Show Info: The meta info will be shown to others on hover.<br>"
	page += "			Reset URL: Creates a new URL hash for this image.<br>"
	page += "		</div>"
	#page += "	</div>"

	page += "  </form>"
	page += "</div>"
	page += "</body></html>"
	return page
