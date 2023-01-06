import requests
import base64
from dreamflask.dream_consts import *
from dreamflask.libs.sd_logger import SD_Logger, logger_levels

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

log = SD_Logger("DreamUtils", logger_levels.INFO)

def clean_name(name, replace='_'):
	return ''.join( [ c if c.isalnum() or c == "_" or c == "-"  else replace for c in name ] )[:36]

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_rsa_keys():
	key = RSA.generate(2048)
	private_key = key.export_key()
	file_out = open(PRIVATE_KEY, "wb")
	file_out.write(private_key)
	file_out.close()

	public_key = key.publickey().export_key()
	file_out = open(PUBLIC_KEY, "wb")
	file_out.write(public_key)
	file_out.close()

def encrypt_text(plain_text, public_key):
	session_key = get_random_bytes(16)

	# Encrypt the session key with the public RSA key
	cipher_rsa = PKCS1_OAEP.new(public_key)
	enc_session_key = cipher_rsa.encrypt(session_key)

	# Encrypt the data with the AES session key
	cipher_aes = AES.new(session_key, AES.MODE_EAX)
	ciphertext, tag = cipher_aes.encrypt_and_digest(plain_text.encode("utf-8"))
	return [ x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]

def decrypt_text(enc_obj, private_key):
	# log.info([ x for x in  enc_obj.split(' ') ])
	enc_session_key, nonce, tag, ciphertext = [ base64.b64decode(x) for x in  enc_obj.split(' ') ]
	# Decrypt the session key with the private RSA key
	cipher_rsa = PKCS1_OAEP.new(private_key)
	session_key = cipher_rsa.decrypt(enc_session_key)

	# Decrypt the data with the AES session key
	cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
	data = cipher_aes.decrypt_and_verify(ciphertext, tag)
	return data.decode("utf-8")

def convert_bytes(bytes_number):
	tags = [ "Bytes", "Kb", "Mb", "Gb", "Tb" ]
	i = 0
	bytes_number = double_bytes = int(bytes_number)
	while (i < len(tags) and bytes_number >= 1024):
			double_bytes = bytes_number / 1024.0
			i = i + 1
			bytes_number = bytes_number / 1024
	return str(round(double_bytes, 2)) + " " + tags[i]

def generate_progress(session_id):
	resp = requests.get(PROGRESS_API_URL)
	return resp.json()

def generate_options(page_info):
	options_request = {
		"sd_model_checkpoint": page_info.get('model'),
		"sd_checkpoint_cache": 0
	}
	resp = requests.post(OPTIONS_API_URL, json=options_request)
	return resp.json()

def generate_upscaling(page_info, image_b64):
	upscale_request = {
		"resize_mode": 0,
		"show_extras_results": True,
		"gfpgan_visibility": 0,
		"codeformer_visibility": 0,
		"codeformer_weight": 0,
		"upscaling_resize": page_info.get('scale', 2),
		"upscaling_resize_w": page_info.get('width', 512),
		"upscaling_resize_h": page_info.get('height', 512),
		"upscaling_crop": False,
		"upscaler_1": page_info.get('upscaler'),
		"upscaler_2": "None",
		"extras_upscaler_2_visibility": 0,
		"upscale_first": True,
		"image": f"{image_b64}"
		}

	resp = requests.post(UPSCALE_API_URL, json=upscale_request)
	return resp.json()

def generate_txt2img(page_info):
	txt2img_request = {
		"enable_hr": False,
		"denoising_strength": page_info.get('strength', ''),
		"firstphase_width": 0,
		"firstphase_height": 0,
		"prompt": page_info.get('prompt', ''),
		"styles": [],
		"seed": page_info.get('seed', -1),
		"subseed": -1,
		"subseed_strength": 0,
		"seed_resize_from_h": -1,
		"seed_resize_from_w": -1,
		"sampler_name": page_info.get('sampler', 'sd-v1-5-pruned.ckpt'),
		"batch_size": page_info.get('batch_size', 1),
		"n_iter": page_info.get('batches', 1),
		"steps": page_info.get('steps', 25),
		"cfg_scale": page_info.get('cfg_scale', .5),
		"width": page_info.get('width', 512),
		"height": page_info.get('height', 512),
		"restore_faces": False,
		"tiling": False,
		"negative_prompt": page_info.get('neg_prompt', ''),
		"eta": 0,
		"s_churn": 0,
		"s_tmax": 0,
		"s_tmin": 0,
		"s_noise": 1,
		"override_settings": {},
		"sampler_index": page_info.get('sampler', '')
	}

	resp = requests.post(TXT2IMG_API_URL, json=txt2img_request)
	return resp.json()

def generate_img2img(page_info, init_image_b64):
	img2img_request = {
		"init_images": [ init_image_b64 ],
		"resize_mode": 0,
		"denoising_strength": 1.0 - float(page_info.get('strength', 0.75)),
		"mask": None,
		"mask_blur": 4,
		"inpainting_fill": 0,
		"inpaint_full_res": True,
		"inpaint_full_res_padding": 0,
		"inpainting_mask_invert": 0,
		"prompt": "",
		"styles": [],
		"seed": -1,
		"subseed": -1,
		"subseed_strength": 0,
		"seed_resize_from_h": -1,
		"seed_resize_from_w": -1,
		"sampler_name": page_info.get('sampler', ''),
		"batch_size": page_info.get('batch_size', 1),
		"n_iter": page_info.get('batches', 1),
		"steps": page_info.get('steps', 25),
		"cfg_scale": page_info.get('cfg_scale', .5),
		"width": page_info.get('width', 512),
		"height": page_info.get('height', 512),
		"restore_faces": False,
		"tiling": False,
		"negative_prompt": page_info.get('neg_prompt', ''),
		"eta": 0,
		"s_churn": 0,
		"s_tmax": 0,
		"s_tmin": 0,
		"s_noise": 1,
		"override_settings": {},
		"sampler_index": page_info.get('sampler', ''),
		"include_init_images": True
		}

	resp = requests.post(IMG2IMG_API_URL, json=img2img_request)
	return resp.json()
