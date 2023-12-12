from PIL import Image
from PIL import ImageFile
import sys
import os
import minio_api

ImageFile.LOAD_TRUNCATED_IMAGES = True


def resize_image_width_ratio(filename, max_width=800):
	image = Image.open(filename)
	width, height = image.size
	ratio = 1
	
	if width > max_width:
		ratio = float(width) / float(max_width)
	
	new_width = int(float(width) / ratio)
	new_height = int(float(height) / ratio)
	img = image.resize((new_width, new_height), Image.ANTIALIAS)
	# fname, extention = os.path.splitext(filename)
	x = filename.split('/')
	strr = ''
	for z in x[:-2]:
		strr += z + '/'
	new_filename = ''
	# print strr
	# print x[-1]
	if max_width == 320:
		y = 'minio_files/320px/' + "320_" + x[-1]
		y_bucket = '320px/' + "320_" + x[-1]
		new_filename = strr + y
		out = file(new_filename, "w")
	elif max_width == 640:
		y = 'minio_files/640px/' + "640_" + x[-1]
		y_bucket = '640px/' + "640_" + x[-1]
		new_filename = strr + y
		out = file(new_filename, "w")
	else:
		y = 'minio_files/1280px/' + "1280_" + x[-1]
		y_bucket = '1280px/' + "1280_" + x[-1]
		new_filename = strr + y
		out = file(new_filename, "w")
		
	# print new_filename
	# print y
	try:
		img.convert('RGB').save(out, "PNG", optimize=True)
		minio_api.Uploadfiles('image-bucket', y_bucket, new_filename,
		                      'image/png')
	finally:
		out.close()
	os.remove(new_filename)
	
	return 'Done'

def compress_without_resize(file_path):
	file_name = file_path.split('/')
	root_path = ''
	for z in file_name[:-2]:
		root_path += z + '/'
	image = Image.open(file_path)
	original_path = root_path + 'minio_files/' + file_name[-1]
	original_path_bucket = 'original/' + file_name[-1]
	image.save(original_path, "PNG", optimize=True, quality=85)
	minio_api.Uploadfiles('image-bucket', original_path_bucket, original_path,
	                      'image/png')
	os.remove(original_path)
	
def compress_without_resize_new_portal(file_path):
	file_name = file_path.split('/')
	image = Image.open(file_path)
	original_path = file_path
	original_path_bucket = 'original/' + file_name[-1]
	image.save(original_path, "PNG", optimize=True, quality=85)
	minio_api.Uploadfiles('image-bucket', original_path_bucket, original_path,
	                      'image/png')
	os.remove(original_path)
	