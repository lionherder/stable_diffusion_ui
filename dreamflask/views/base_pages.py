import os

from dream_utils import convert_bytes
from dreamflask.libs.sd_logger import SD_Logger, logger_levels

log = SD_Logger(__name__.split('.')[-1], logger_levels.INFO)

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

def navbar_section(display_name=None):
	page = "<div class='diffusion'>"
	page += "	<div class='flex-container' style='margin-bottom: 0px;align-items: center;font-size: large;'>"
	page += "		<p style='margin-right: 1%;'>SD</p>"
	page += "		<div class='flex-container'>"
	page += "			<a href='/' style='text-decoration: none;color: #555;'>Clear Session</a>"
	page += "		</div>"

	if display_name:
		page += "	<div class='flex-container' style='margin-left: auto;'>"
		page += f"		{display_name}"	
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

def checkbox_table_section(section_title, file_infos, session_db, session_id, prefix='', selected_list=[], limit=0):
	page = f"<div class='gallery-title collapsible active'>-&nbsp&nbsp{section_title}</div>"
	page += "<div class='gallery'>"
	for idx, file_obj in enumerate(file_infos):
		img_info = session_db.get_image_item_by_hash(file_obj.id)
		#log.info(f"IDX, FILEINFO: {idx}, {file_info}")
		selected = 'checked' if img_info.id in selected_list else ''
		title = img_info.get_title_text(viewer_id=session_id)
		page += "	<div class='gallery-img content' style='flex-shrink: 0;'>"
		page += f"		<img title='{title}' onclick='setCheckboxValue(\"{prefix}_{idx}\", true)' src='/share/{img_info.thumbnail}' width='128' height='128'></img>"
		page += f"		<input style='margin-bottom: 10%;' type='checkbox' {selected} id='{prefix}_{idx}' name='files' value='{img_info.id}'/>"
		page += "	</div>"
		if (limit > 0 and idx > limit):
			break
	page += "</div>"
	return page

def image_table_section(section_title, file_infos, session_db, session_id, limit=0):
	page = f"<div class='gallery-title collapsible active'>-&nbsp&nbsp{section_title}</div>"
	page += "<div class='gallery'>"
	for idx, file_obj in enumerate(file_infos):
		img_info = session_db.get_image_item_by_hash(file_obj.id)
		#log.info(f"IDX, FILEINFO: {idx}, {file_info}")
		title = img_info.get_title_text(viewer_id=session_id)
		page += f"	<a class='gallery-img content' target='_output' title='{title}' href='/share/{img_info.id}'>"
		page += f"		<img src='/share/{img_info.thumbnail}' width='128' height='128'>"
		page += "	</a>"
		#page += "</div>"
		if (limit > 0 and idx > limit):
			break
	page += "</div>"
	return page

def image_selection_buttons(buttons_info):
	page = "		<div class='flex-container' style='gap: 2px;'>"
	for k,v in buttons_info.items():
		page += f"			<div class='chip' onClick='selectAllImg(\"{v}\")'>{k}</div>"
	page += "			<div class='chip' onClick='clearCheckboxes()'>Clear Selections</div>"
	page += "		</div>"
	return page

def buttons_section(button_names):
	page = "<div class='button-container'>"
	for button_name in button_names:
		page += f"    <button class='button' type='submit' name='button' value='{button_name}'>{button_name}</button>"
	page += "</div>"
	return page

def generated_images_section(file_infos, session_db, session_id, cols=0):
	return image_table_section('Generated Images', file_infos, session_db, session_id, cols)

def workbench_images_section(file_infos, session_db, session_id, cols=0):
	return image_table_section('Workbench Images', file_infos, session_db, session_id, cols)

def playground_image_section(file_infos, session_db, session_id, cols=0):
	return image_table_section('Playground Images', file_infos, session_db, session_id, cols)

