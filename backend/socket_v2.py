import asyncio
import websockets
import json
import netifaces

import serial
import time
import os
import re

import requests

controls = {
  "forward": "f",
  "backward": "b",
  "left": "l",
  "right": "r",
  "stop": "s",
  "mesure": "m",
}

# generates usb and bluetooth interfaces to try (linux only)
connection_points = [f"/dev/ttyUSB{i}" for i in range(5, -1, -1)]
blue_connection_points = [f"/dev/rfcomm{i}" for i in range(5, -1, -1)]
connection_points.extend(blue_connection_points)

print(connection_points)
baud_rate = 9600


def send_data_to_arduino(ser, data):
  ser.write(data.encode('utf-8'))
  response = ser.read().decode('utf-8')
  print(response)

def check_serial_connection_and_send(ser, data):


  try:
      for bluetooth in connection_points:
        if os.path.exists(bluetooth):
          print(f"working on Serial connection: {bluetooth}")

          if ser.isOpen():
            print(f"Sending data to Arduino: {data}")
            ser.write(data.encode('utf-8'))
            if data == "m":
              print("sending measure command")
              time.sleep(6)
              print("reading data")
            
              response = ser.read_all().decode()
              response = re.search(r'\d+', response).group(0)

              
              print(response)
              try:
                res = requests.post("http://localhost:5000/api/addreadingdata", json={"reading": response})
                print(res.text)
              except Exception as e:
                print(f"Error: Could not send data to the server: {e}")

            print(response)

        else:
          print("Error: Could not find the specified device.")
          # break  # Exit the while loop if the device does not exist
      
  except Exception as e:
      print(f"Error: Could not connect to Arduino. Please check Bluetooth pairing, device address, and baud rate: {e}")
  
async def handle_client(websocket, path):
  # Log when a client connects
  print(f"Client connected: {websocket.remote_address}")

  for bluetooth in connection_points:
    if os.path.exists(bluetooth):
      print(f"Serial connection is available: {bluetooth}")
      ser = serial.Serial(bluetooth, baud_rate)
      time.sleep(2)
      print(f"Serial connection is connected: {bluetooth}")

  try:
    # Handle incoming messages from the client
    async for message in websocket:
      # Echo the received message back to the client
      print(f"Received message: {message}")
      print(f"\ntype: {type(message)}")
      data = json.loads(message)
      print(f"\njson: {data}")
      if data['type'] == 'control_override':

        print(f"Sending control command: {data['direction']}")
        try:

          check_serial_connection_and_send(ser, controls[data['direction']])
        except Exception as e:
          print(f"something went wrong with the control command: {e}")
          
      await websocket.send(message)
  finally:
    # Log when a client disconnects
    ser.close()
    print(f"Client disconnected: {websocket.remote_address}")


def main():
  # Create a WebSocket server
  start_server = websockets.serve(handle_client, "0.0.0.0", 5002)

  # Start the server
  asyncio.get_event_loop().run_until_complete(start_server)
  asyncio.get_event_loop().run_forever()



if __name__ == "__main__":
  print("Starting WebSocket server...")
  print("Listening on ws://localhost:5002")
  # Get all interfaces of the device
  interfaces = netifaces.interfaces()
  for interface in interfaces[:-3]:
    addrs = netifaces.ifaddresses(interface)
    # print(f"Interface: {interface}")
    # print(list(addrs.values()))
    try:
      print(f"Listening on: ws://{list(addrs.values())[1][0]['addr']}:5002")
    except:
      print(f"Listening on: ws://{list(addrs.values())[0][0]['addr']}:5002")
  print("Press Ctrl+C to stop the server")

  main()





