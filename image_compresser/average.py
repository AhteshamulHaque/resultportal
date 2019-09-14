import os
import threading
import shutil

################### This file just compressed file having size > 10KB ####################
FROM_DIR = 'images'
TO_DIR = 'image_compressed'

if not os.path.exists(TO_DIR):
	os.mkdir(TO_DIR)



def average_count(file2read, resize, message):
	with open(file2read, 'r') as fp:
		for lines in fp:
			os.system("convert -resize {resize} {FROM}/{file} {TO}/{file}".format(
				FROM=FROM_DIR,
				TO=TO_DIR,
				file=lines.strip(),
				resize=resize
			))

		size = 0
		count = 0

		fp.seek(0)

		for lines in fp:
			size += os.path.getsize(TO_DIR+"/"+lines.strip())
			count += 1

		print("Average size for {message} : {avg} KB".format(
			message=message,
			avg=(size/count)/1024
		))

_10_20 = threading.Thread(target=average_count, args=('_10_20.txt', '90%', "10 and 20"))
_20_30 = threading.Thread(target=average_count, args=('_20_30.txt', '80%', "20 and 30"))
_30_40 = threading.Thread(target=average_count, args=('_30_40.txt', '70%', "30 and 40"))
_40_50 = threading.Thread(target=average_count, args=('_40_50.txt', '65%', "40 and 50"))
_50_100 = threading.Thread(target=average_count, args=('_50_100.txt', '40%', "50 and 100"))
_100_above = threading.Thread(target=average_count, args=('_100_above.txt', '20%', "100 and above"))


_10_20.start()
_20_30.start()
_30_40.start()
_40_50.start()
_50_100.start()
_100_above.start()

for filename in ['_0_5.txt', '_5_10.txt']:
	with open(filename) as fp:
		for line in fp:
			shutil.copyfile(FROM_DIR+"/"+line.strip(), TO_DIR+"/"+line.strip())
