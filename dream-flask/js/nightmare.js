function resetSeed() { document.getElementById('seed').value = -1; }
function clearPrompt() { document.getElementById('prompt').value = ''; }
function clearNegPrompt() { document.getElementById('neg_prompt').value = ''; }
function setCheckboxValue(checkbox) { document.getElementById(checkbox).checked = !document.getElementById(checkbox).checked; }
function selectAllImg(imgType) { for (let image of document.getElementsByTagName('input')) { if (image['id'].includes(imgType)) { image.checked = !image.checked; } } }
function clearCheckboxes() { for (let image of document.getElementsByTagName('input')) { image.checked = false; } }

var coll = document.getElementsByClassName("collapsible");
var i;


for (i = 0; i < coll.length; i++) {
	console.log("Adding event listener")
	coll[i].addEventListener("click", function (event) {
		this.classList.toggle("active");
		var images = this.nextElementSibling.getElementsByClassName('content')

		if (this.classList.value.includes('active')) {
			this.innerHTML = "-&nbsp&nbsp" + this.innerHTML.substring(13);
		} else {
			this.innerHTML = "+&nbsp&nbsp" + this.innerHTML.substring(13);
		}

		//var images = event.path[0].nextElementSibling.getElementsByClassName('content')
		for (var idx in images) {
			if (idx < images.length) {
				images[idx].style.height = ""
				if (this.classList.value.includes('active')) {
					images[idx].style.maxHeight = `${images[idx].scrollHeight}px`
				} else {
					images[idx].style.maxHeight = '0px'
				}
			}
		}
	});
}

var el = document.getElementById('file');
if (el) {
	console.log("Adding event listeners");
	el.addEventListener('change', updateFilenames);
};


function updateFilenames(e) {
	var files = e.target.files;
	var num_files = files.length;
	var page = "";

	for (var idx in e.target.files) {
		if (idx < num_files) {
			page += createFileSelect(files[idx])
		}
	}
	document.getElementById('file-selections').innerHTML = page;
};

function adjustTextAreaHeight() {
	var tas = document.getElementsByTagName('textarea')
	for (var idx in tas) {
		if (idx < tas.length) {
			tas[idx].style.height = '';
			tas[idx].style.height = `${tas[idx].scrollHeight}px`;
		}
	}
};

function createFileSelect(file_info) {
	var page = "";
	var { name: filename, size } = file_info;
	var fileSize = (size / 1000).toFixed(2);
	page += "<div class='file-selection'>";
	page += "	<div class='file-name' id='file-name'>" + `${filename} - ${fileSize}KB` + "</div>";
	page += "</div>";

	return page;
};