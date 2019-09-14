import requests
import logging
import sys
import json
import os
import  argparse
from progress.bar import IncrementalBar

parser = argparse.ArgumentParser()

parser.add_argument('infile', type=argparse.FileType('r'))
args = parser.parse_args()

logger = logging.getLogger()

if not os.path.exists('images'):
	os.mkdir('images')

file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.WARNING)

logger.addHandler(file_handler)

URL = "http://10.51.11.42/feedback/showimage.aspx?id={}&type=student"

image_data = json.load(args.infile)

with IncrementalBar('Downloading',suffix='%(percent).1f%% - %(eta)ds', max=len(image_data)) as bar:

	for roll, image_id in image_data.items():

		try:
			req = requests.get(URL.format(image_id))

			with open('images/'+roll+'.jpg', 'wb') as file:
				file.write(req.content)

		except Exception as e:
			logger.warning(roll+' failed. REASON: ', e.__str__())

		bar.next()
