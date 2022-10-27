import base_pages
from dreamutils import get_uploaded_images, get_generated_images
from dreamconsts import GENERATED_FOLDER, UPLOADS_FOLDER

def cleanup_page(session_info):
	session_id = session_info['session_id']
	status_msg = session_info['status_msg']

	page = base_pages.header_section("Clean Up")
	page += "	<body>"
	page += base_pages.navbar_section()	

	page += "<div class='container-fluid'>"
	page += f"Cleaning up images for <b>{session_id}</b><br><br>"
	page += f"Status: {status_msg}<br><br>"
	page += "	<form action='/' method='POST'>"
	page += "		<input type='hidden' name='page_name' value='cleanup_page'>"
	page += f"		<input type='hidden' name='session_id' value='{session_id}'>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Delete'>Delete</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Return'>Return</button>"
	page += "		<button class='btn btn-primary' type='submit' name='button' value='Refresh'>Refresh</button>"
	#page += "		<button class='btn btn-primary' type='submit' name='button' value='Nuke It All!'>Nuke It All!</button>"
	#page += "		Confirm Nuke <input type='checkbox' name='confirm'/><br><br>"
	page += "<br><br>"

#	page += " 		<div class='pmd-chip'>Invert Generated<a class="pmd-chip-action" href="javascript:void(0);">"
#	page += "		<i class="material-icons">close</i></a>
#</div>
	page += "		<span class='badge badge-primary' style='color:#FFF;background-color:#0d6efd' onClick='selectAllImg(\"g_\")'>Invert Generated</span>"
	page += "		<span class='badge badge-primary' style='color:#FFF;background-color:#0d6efd' onClick='selectAllImg(\"u_\")'>Invert Uploaded</span>"

	page += "		<br><br><h5>Generated Images</h5>"
	page += "		<div class='table-responsive-xxl'>"
	page += "			<table>"
	for idx, image in enumerate(get_generated_images(session_id)):
		page += "		<td align='center'>"
		page += f"			<img class='img-thumbnail' onclick='setCheckboxValue(\"g_{idx}\", true)' src='/{image}' width='128' height='128'></img><p>"
		page += f"			<input type='checkbox' id='g_{idx}' name='files' value='{image}'/></p>"
		page += "		</td>"
		if ((idx+1) % 5 == 0):
			page += "	<tr></tr>"
	page += "	</table>"
	page += "	</div>"
		
	page += "		<h5>Uploaded Images</h5>"
	page += "		<div class='table-responsive-xxl'>"
	page += "			<table>"
	for idx, image in enumerate(get_uploaded_images(session_id)):
		page += "		<td align='center'>"
		page += f"			<img class='img-thumbnail' onclick='setCheckboxValue(\"u_{idx}\", true)' src='/{image}' width='128' height='128'></img><p>"
		page += f"			<input type='checkbox' id='u_{idx}' name='files' value='{image}'/></p>"
		page += "		</td>"
		if ((idx+1) % 5 == 0):
			page += "	<tr></tr>"
	page += "	</table>"
	page += "	</div>"

	page += "		<input class='btn btn-primary' type='submit' name='button' value='Delete'/>"
	page += "		<input class='btn btn-primary' type='submit' name='button' value='Return'/>"
	page += "	</form>"
	page += "	<br><br><br><br>"
	page += "</div>"
	page += "	</body></html>"

	return page
