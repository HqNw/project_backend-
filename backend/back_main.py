from flask import Flask, jsonify, request
import pymongo
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import socket
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eTUgV7e4MZqDdgxYplRDbA=='
CORS(app, cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")


myclient = pymongo.MongoClient(
  "mongodb://localhost:27017",
  username='root',
  password='example',
)

mydb = myclient["testing"]
mycol = mydb["readings"]


@socketio.on('connect')
def handle_connect():
  """event listener when client connects to the server"""
  print(request.sid)
  print("client has connected")
  emit("connect",{"data":f"id: {request.sid} is connected"})



@socketio.on('disconnect')
def handle_disconnect():
  print('Client disconnected')

@socketio.on('message')
def handle_message(message):
  print('Received message:', message)
  emit('message', message, broadcast=True)

def echo(ws, path):
  while True:
    message = ws.recv()
    ws.send(message)



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


@app.route('/api/data', methods=['POST'])
def add_data():
    # new_data = {
    #     'name': request.json['name'],
    #     'value': request.json['value']
    # }
    
    # mongo.db.collection.insert_one(new_data)
    socketio.emit('data_added', {'message': 'Data added successfully'})
    return jsonify({'message': 'Data added successfully'})

@app.route('/api/addreadingdata', methods=['POST'])
def add_reading_data():
  reading = request.json.get('reading')
  if reading is None:
    return jsonify({'error': 'Reading value is missing'}), 400
  print(f"got value: {reading}")
  mycol.insert_one({'reading': reading, 'time': time.ctime()})
  return jsonify({'message': 'Reading added successfully'})


if __name__ == '__main__':

  # Get the IP address of the network interface
  network_ip = socket.gethostbyname(socket.getfqdn())
  socketio.run(app, debug=True, host="0.0.0.0", port=5000)







