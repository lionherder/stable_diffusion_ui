import base_pages

def landing_page(session_info):
	page = base_pages.header_section("Create Session")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += "	<form action='/' method='POST'>"
	page += "		<input type='hidden' name='page_name' value='landing'/>"
	page += "		<div class='row g-3'>"
	page +=	"			<div class='col-sm'>"
	page += "				<label for='session_id' class='form-label'>Session Name</label>"
	page += "				<input style='width: 35%;' name='session_id' type='text' class='form-control' id='session_id'/>"
	page += "			</div>"
	page += "			<div class='col-12'>"
	page += "				<button type='submit' value='go' name='button' class='btn btn-primary'>Go</button>"
	page += "			</div>"
	page += "		</div>"
	page += "	</form>"
	page += "</div>"
	page += "</body></html>"
	return page
