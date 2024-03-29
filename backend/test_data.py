import pymongo
import random
import time
import datetime

myclient = pymongo.MongoClient(
  "mongodb://localhost:27017",
  username='root',
  password='example',
)

mydb = myclient["testing"]
mycol = mydb["readings"]

while True:
  random_value = random.randint(0, 100)
  mycol.insert_one({'reading': random_value, 'time': time.ctime()})
  print(f"value: {random_value}")
  time.sleep(1)


current_time = datetime.datetime.fromtimestamp(time.time())
print(current_time.strftime('%Y-%m-%d %H:%M:%S'))
print(time.get_clock_info('time'))
















