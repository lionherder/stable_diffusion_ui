import os

from dream_utils import convert_bytes

def header_section(page_title, script=''):
	page = "<!doctype html>"
	page += "<html lan='en'>"
	page += "	<head>"
	page += "		<meta charset='utf-8'>"
	page += "		<meta name='viewport' content='width=device-width, initial-scale=1'>"
	page += "		<link rel='stylesheet' type='text/css' href='/css/nightmare.css'/>"
	page += " 		<script src='/js/nightmare.js' defer></script>"
	page += f"		<title>Stable Diffusion -- {page_title}</title>"
	page += script
	page += "	</head>"
	return page

def navbar_section(session_id=None):
	page = "<div class='diffusion'>"
	page += "	<div class='flex-container' style='margin-bottom: 0px;align-items: center;font-size: large;'>"
	page += "		<p style='margin-right: 1%;'>SD</p>"
	page += "		<div class='flex-container'>"
	page += "			<a href='/' style='text-decoration: none;color: #555;'>Clear Session</a>"
	page += "		</div>"

	if (session_id):
		page += "	<div class='flex-container' style='margin-left: auto;'>"
		page += f"		{session_id}"	
		page += "	</div>"

	page += "	"
	page += "	</div>"
	page += "	<div class='banner' style='margin-top: 0px;margin-bottom: 0px;padding: 1px;'></div>"
	return page

def banner_section(status_msg, page_name):
	page = ""
	if (page_name):
		page += f"		<div class='page-title'>{page_name}</div>"
	page += f"		<div class='banner-status'>{status_msg}</div>"
	return page

def generate_banner(banner_text):
	return f"<div class='banner'>{banner_text}</div>"

def generate_label_input(label_title, label_name, default='', size=3):
	page = f"<label>{label_title}&nbsp"
	page += f"	<input size='{size}' value='{default}' name='{label_name}'>"
	page += "</label>"
	return page


def checkbox_table_section(title, file_infos, prefix='', selected_list=[], limit=0):
	page = f"<div class='gallery-title collapsible active'>-&nbsp&nbsp{title}</div>"
	page += "<div class='gallery'>"
	for idx, file_info in enumerate(file_infos):
		#print(f"IDX, FILEINFO: {idx}, {file_info}")
		selected = 'checked' if file_info.hash in selected_list else ''
		title = f'{os.path.basename(file_info.filename)} [{convert_bytes(file_info.size)}]'
		page += "	<div class='gallery-img content' style='flex-shrink: 0;'>"
		page += f"		<img title='{title}' onclick='setCheckboxValue(\"{prefix}_{idx}\", true)' src='/share/{file_info.thumbnail}' width='128' height='128'></img>"
		page += f"		<input style='margin-bottom: 10%;' type='checkbox' {selected} id='{prefix}_{idx}' name='files' value='{file_info.hash}'/>"
		page += "	</div>"
		if (limit > 0 and idx > limit):
			break
	page += "</div>"
	return page

def image_table_section(title, file_infos, cols=0, limit=0):
	page = f"<div class='gallery-title collapsible active'>-&nbsp&nbsp{title}</div>"
	page += "<div class='gallery'>"
	for idx, file_info in enumerate(file_infos):
		#print(f"IDX, FILEINFO: {idx}, {file_info}")
		title = f'{os.path.basename(file_info.filename)} [{convert_bytes(file_info.size)}]'
		page += f"	<a class='gallery-img content' target='_output' title='{title}' href='/share/{file_info.hash}'>"
		page += f"		<img src='/share/{file_info.thumbnail}' width='128' height='128'>"
		page += "	</a>"
		#page += "</div>"
		if (limit > 0 and idx > limit):
			break
	page += "</div>"
	return page

def buttons_section(button_names):
	page = "<div class='button-container'>"
	for button_name in button_names:
		page += f"    <button class='button' type='submit' name='button' value='{button_name}'>{button_name}</button>"
	page += "</div>"
	return page

def generated_images_section(file_infos, cols=0):
	return image_table_section('Generated Images', file_infos, cols)

def workbench_images_section(file_infos, cols=0):
	return image_table_section('Workbench Images', file_infos, cols)

def playground_image_section(file_infos, cols=0):
	return image_table_section('Playground Images', file_infos, cols)

