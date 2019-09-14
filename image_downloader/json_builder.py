import pymysql
import json

conn = pymysql.connect("localhost", "root", "root")
cursor = conn.cursor()

cursor.execute("SELECT roll , image_id FROM ADMIN.USERS")

data = {}
for roll, image in cursor:
	data[roll] = image.replace('.jpg', '')

json.dump(data, open('images.json', 'w'), indent=2)

conn.close()
