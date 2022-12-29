import os

from . import base_pages
from dreamflask.dream_utils import convert_bytes

def view_page(img_info):
	page = base_pages.header_section(f"{img_info.filename}")
	page += "<body>"
	page += base_pages.navbar_section("")
	page += "</body></html>"

	title = img_info.get_title_text()
	page += "<div class='col_404'>"
	page += f"	<img class='cell_404' src='/share/{img_info.id}-PT' title='{title}'></img>"
	page += "</div>"

	return page

if __name__ == '__main__':
	view_page({
		'filename' : 'tesingfilename',
		'size' : 600000,
		'id' : 'lyon-furry'
	})