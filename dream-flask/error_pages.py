import base_pages

def page_404(status_msg):
	page = base_pages.header_section("404 - Sad AI")
	page += "<body>"
	page += base_pages.navbar_section("")
	page += base_pages.generate_banner(f"<p style='font-size: small;'>{status_msg}</p>")
	page += "</body></html>"
	
	return page

def share_404(share_hash):
	status_msg = f"<p style='font-size: 15px;'>The share you are looking for [{share_hash}] is no longer available.<p>"
	page = base_pages.header_section("No Share")
	page += "<body>"
	page += base_pages.navbar_section("")
	page += base_pages.generate_banner(status_msg)
	page += "</body></html>"

	return page