def header_section(page_title):
	page = "<!doctype html>"
	page += "<html lan='en'>"
	page += "	<head>"
	page += "		<meta charset='utf-8'>"
	page += "		<meta name='viewport' content='width=device-width, initial-scale=1'>"
	page += "		<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css' rel='stylesheet' integrity='sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We' crossorigin='anonymous'>"
	page += f"		<title>Stable Diffusion -- {page_title}</title>"
	page += " 		<script src='https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js' integrity='sha384-U1DAWAznBHeqEIlVSCgzq+c9gqGAJn5c/t99JyeKa9xxaYpSvHU5awsuZVVFIhvj' crossorigin='anonymous'></script>"
	page += "		<script>"
	page += "			function resetSeed() { document.getElementById('seed').value = -1; }"
	page += "			function clearPrompt() { document.getElementById('prompt').value = ''; }"
	page += "			function setCheckboxValue(checkbox) { document.getElementById(checkbox).checked = !document.getElementById(checkbox).checked; }"
	page += "			function selectAllImg(imgType) { for (let image of document.getElementsByTagName('input')) { if (image['id'].includes(imgType)) { image.checked = !image.checked; } } }"
	page += "		</script>"
	page += "	</head>"

	return page

def navbar_section():
	page = "	<nav class='navbar navbar-expand-lg navbar-light bg-light'>"
	page += "		<div class='container-fluid'>"
	page += "			<a class='navbar-brand' href='/'>SD</a>"
	page += "			<button class='navbar-toggler' type='button' data-bs-toggle='collapse' data-bs-target='#navbarNav' aria-controls='navbarNav' aria-expanded='false' aria-label='Toggle navigation'>"
	page += "				<span class='navbar-toggler-icon'></span>"
	page += "			</button>"
	page += "			<div class='collapse navbar-collapse' id='navbarNav'>"
	page += "				<ul class='navbar-nav'>"
	page += "					<li class='nav-item'>"
	page += "					<a class='nav-link' href='/'>Clear Session</a>"
	page += "				</li>"
	page += "			</div>"
	page += "		</div>"
	page += "	</nav>"

	return page
