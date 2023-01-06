from . import base_pages
from flask import escape
from dream_consts import IMAGE_DIMS
from dreamflask.controllers.sessions_manager import *
from dreamflask.controllers.page_manager import PROFILE

def profile_page(sessions_db, session_id):
	user_info = sessions_db.get_user_by_id(session_id)
	page_info = user_info.page_manager.get_profile_page_item()
	status_msg = page_info.get('status_msg')

	page = base_pages.header_section("User Profile")
	page += "<body>"
	page += base_pages.navbar_section(f"{user_info.display_name}", session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', page_name='User Profile')

	page += " <form action='/' method='POST'>"
	page += f"	<input type='hidden' name='page_name' value='{PROFILE}'>"
	page += f"	<input type='hidden' name='session_id' value='{session_id}'>"
	page += "	<div class='flex-container' style='gap:8px;flex-direction:column;width:auto;'>"
	page += "		<label style='justify-content:left;'>User Id:&nbsp"
	page += f"			<input name='user_id' value='{session_id}' readonly>"
	page += "		</label>"
	page += "		<label style='justify-content:left;'>Display Name:&nbsp"
	page += f"			<input name='display_name' value='{user_info.display_name}'>"
	page += "		</label>"
	page += "	</div>"

	page += "	<div class='flex-container'>"
	page += f"		<textarea style='margin: 5px 0px 0px 0px;' onInput=adjustTextAreaHeight() onClick=adjustTextAreaHeight() {{ this.form.submit(); return false; }}' placeholder='Bio' rows=2 id='bio' autofocus name='bio'>{escape(user_info.bio)}</textarea>"
	page += "	</div>"
	page += "		<div class='page-title' style='font-size:small;text-align:left;'>"
	page += "			Reset: Rebuild your image DB library<br>"
	page += "			Nuking your account is forever!"
	page += "		</div>"
	page += "	</div>"

	page += base_pages.buttons_section(['Update', 'Return', 'Refresh', 'Reset', 'Nuke Account', 'Clear'])
	page += f"	<div class='flex-container' style='flex-direction:row;font-family:Arial;font-size:small;'>"
	page += f"		<label style='padding: 0 6px 0 0;justify-content:left;'>"
	page += f"		<input type='checkbox' name='confirm' value='True'>Confirm</input>"
	page += f"		</label>"
	page += f"	</div>"

	page += "  </form>"

	page += "</div>"
	page += "</body></html>"
	return page
