import os

########### sort images on basis of size and write then to files #############3

_0_5 = open('_0_5.txt', 'w')
_5_10 = open('_5_10.txt', 'w')
_10_20 = open('_10_20.txt', 'w')
_20_30 = open('_20_30.txt', 'w')
_30_40 = open('_30_40.txt', 'w')
_40_50 = open('_40_50.txt', 'w')
_50_100 = open('_50_100.txt', 'w')
_100_above = open('_100_above.txt', 'w')

BASE_DIR = "images"

for file in os.listdir(BASE_DIR):

	size = os.path.getsize(BASE_DIR+"/"+file)

	data = "{}\n".format(file)

	if size < 5000:
		_0_5.write(data)

	elif size > 5000 and size < 10000:
		_5_10.write(data)

	elif size > 10000 and size < 20000:
		_10_20.write(data)

	elif size > 20000 and size < 30000:
		_20_30.write(data)

	elif size > 30000 and size < 40000:
		_30_40.write(data)

	elif size > 40000 and size < 50000:
		_40_50.write(data)

	elif size > 50000 and size < 100000:
		_50_100.write(data)

	else:
		_100_above.write(data)


_0_5.close()
_5_10.close()
_10_20.close()
_20_30.close()
_30_40.close()
_40_50.close()
_50_100.close()
_100_above.close()
