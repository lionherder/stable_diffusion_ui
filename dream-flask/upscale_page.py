import os
import base_pages

def upscale_page(session_info, session_id):
	upscalers = session_info.get_upscalers()
	user_info = session_info.get_user(session_id)
	page_info = user_info.get_upscale_page_info()
	status_msg = page_info['status_msg']

	page = base_pages.header_section("Upscale")
	page += "	<body>"
	page += base_pages.navbar_section(session_id)
	page += base_pages.banner_section(f'Status: {status_msg}', page_name='Upscale Image')

	page += f"	<form method='POST' action='/' enctype='multipart/form-data'>"
	page += "		<input type='hidden' name='page_name' value='upscale_page'/>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'/>"
	page += "	<div class='flex-container'>"
	page += "		<label style='gap: 0px;'>Upscale&nbsp"
	page += f"			<label>2x<input {'checked' if page_info['scale'] == '2' else ''} type='radio' name='scale' id='scale' value='2'></label>"
	page += f"			<label>4x<input {'checked' if page_info['scale'] == '4' else ''} type='radio' name='scale' id='scale' value='4'></label>"
	page += "		</label>"
	page += "	</div>"

	upscalers = sorted(upscalers, key = lambda x: x.lower())
	page += "	<div class='flex-container'>"
	page += "		<label>Upscaler&nbsp"
	page += "			<select id='upscaler' name='upscaler'>"
	for upscaler in upscalers:
		selected = "selected" if (upscaler == page_info.get('upscaler', '')) else ""
		page += f"			<option value='{upscaler}' {selected}>{upscaler}</option>"
	page += "			</select>"
	page += "		</label>"
	page += "		<label>"
	page += "			<select id='upscale_image' name='upscale_image'>"
	page += "				<option value='none'>Upscale Image</option>"
	for file_info in (user_info.filemanager.get_generated_fileinfos() + user_info.filemanager.get_workbench_fileinfos()):
		page += f"			<option value='{file_info.hash}'>{os.path.basename(file_info.filename)}</option>"
	page += "			</select>"
	page += "		</label>"
	page += "	</div>"

	page += base_pages.buttons_section(['Upscale', 'Return', 'Refresh', 'Reset', 'Clean Files'])
	page += "</form>"
	page += base_pages.generated_images_section(user_info.filemanager.get_generated_fileinfos())
	page += base_pages.workbench_images_section(user_info.filemanager.get_workbench_fileinfos())
	page += "</div>"
	page += "</body></html>"

	return page
