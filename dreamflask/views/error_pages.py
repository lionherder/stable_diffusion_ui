from . import base_pages

def page_404(e):
	page = base_pages.header_section("404 - Sad AI")
	page += "<body>"
	page += base_pages.navbar_section("")

	status_msg = "<div class='error_404'>"
	status_msg += f"<p>404 Not Found</p>"
	status_msg += "	<img width='90%' height='5%' src='/images/404_lost.png'></img>"
	status_msg += f"<p>Sorry, the AI was unable to find the file you are looking for</p>"
	status_msg += "</div>"

	page += base_pages.generate_banner(f"{status_msg}")
	page += "</body></html>"
	
	return page

def share_404(share_hash):
	page = base_pages.header_section("Share Not Found")
	page += "<body>"
	page += base_pages.navbar_section("")

	status_msg = "<div class='error_404'>"
	status_msg += "	<p>Share Not Found</p>"
	status_msg += "	<img width='90%' height='5%' src='/images/404_lost.png'></img>"
	status_msg += f"<p>The share you are looking for [{share_hash}] is no longer available<p>"
	status_msg += "</div>"

	page += base_pages.generate_banner(status_msg)
	page += "</body></html>"

	return page