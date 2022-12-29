#!/usr/bin/python

from math import ceil
from PIL import Image

def create_montage(save_name, file_names, num_cols, width, height, margin_left, margin_top, margin_right, margin_bottom, padding, constrain=False):
	"""\
	Make a contact sheet from a group of filenames and save the image:

	file_names       A list of names of the image files
	
	num_cols        Number of columns in the contact sheet
	num_rows        Number of rows in the contact sheet
	photo_width     The width of the photo thumbs in pixels
	photo_height    The height of the photo thumbs in pixels

	margin_left         The left margin in pixels
	margin_top          The top margin in pixels
	margin_right        The right margin in pixels
	margin_bottom       The bottom margin in pixels

	padding      The padding between images in pixels

	returns a PIL image object.
	"""

	# Read in all images and resize appropriately
	imgs = [ Image.open(fn) for fn in file_names ]

	# Figure out how many columns we have
	num_files = len(file_names)
	num_rows = ceil(num_files / num_cols)

	photo_width = width
	photo_height = height
	if (constrain):
		photo_width = ceil(width / num_cols)
		photo_height = ceil(height / num_rows)

	imgs = [ img.resize( (photo_width, photo_height)) for img in imgs ]

	# Calculate the size of the output image, based on the
	#  photo thumb sizes, margins, and padding
	marw = margin_left + margin_right
	marh = margin_top + margin_bottom

	padw = (num_cols-1) * padding
	padh = (num_rows-1) * padding
	isize = (num_cols * photo_width + marw + padw, num_rows * photo_height + marh + padh)

	# Create the new image. The background doesn't have to be white
	white = (10, 10, 10)
	inew = Image.new('RGB', isize, white)

	# Insert each thumb:
	for irow in range(num_rows):
		for icol in range(num_cols):
			left = margin_left + icol * (photo_width+padding)
			right = left + photo_width
			upper = margin_top + irow * (photo_height+padding)
			lower = upper + photo_height
			bbox = (left, upper, right, lower)
			try:
				img = imgs.pop(0)
			except:
				break
			inew.paste(img, bbox)
	if (constrain): 
		print(f"Resizing montage to ({width}, {height})")
		inew = inew.resize( (width, height) )
	inew.save(save_name)

	return inew
