from flask import Flask, jsonify, request
import pymongo
from flask_cors import CORS
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eTUgV7e4MZqDdgxYplRDbA=='
CORS(app, cors_allowed_origins="*")


myclient = pymongo.MongoClient(
  "mongodb://localhost:27017",
  username='root',
  password='example',
)

mydb = myclient["testing"]
mycol = mydb["readings"]


@app.route('/api/getreadingdata', methods=['GET'])
def get_data():
  
  n = request.args.get('n', default=10, type=int)
  data = mycol.find().sort('time', pymongo.DESCENDING).limit(n)

  result = [[], {
    'name' : "water level", 
    'data' : []  
    },
  ]

  for item in data:
    result[1]['data'].append(item['reading'])
    result[0].append(item['time'])

  result[1]['data'].reverse()
  result[0].reverse()
  print(result)
  return jsonify(result)


@app.route('/api/addreadingdata', methods=['POST'])
def add_reading_data():
  reading = request.json.get('reading')
  if reading is None:
    return jsonify({'error': 'Reading value is missing'}), 400
  print(f"got value: {reading}")
  mycol.insert_one({'reading': reading, 'time': time.ctime()})
  return jsonify({'message': 'Reading added successfully'})


if __name__ == '__main__':

  app.run(debug=True, host="0.0.0.0", port=5000)







