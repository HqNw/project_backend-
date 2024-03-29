import asyncio
import websockets
import json
import netifaces

import serial
import time
import os


controls = {
  "forward": "f",
  "backward": "b",
  "left": "l",
  "right": "r",
  "stop": "s"
}

# bluetooth = "/dev/rfcomm0"
baud_rate = 9600


def send_data_to_arduino(ser, data):
  ser.write(data.encode('utf-8'))
  response = ser.read().decode('utf-8')
  print(response)

def check_serial_connection_and_send(data):
  while True:
    try:
      for i in range(5):
        bluetooth = f"/dev/rfcomm{i}"
        if os.path.exists(bluetooth):
          print(f"Serial connection is available: {bluetooth}")
          ser = serial.Serial(bluetooth, baud_rate)
          if ser.isOpen():
            print("Sending data to Arduino")
            ser.write(data.encode('utf-8'))
            response = ser.read().decode('utf-8')
            print(response)
            ser.close()
            break  # Exit the while loop after sending the data
        else:
          print("Error: Could not find the specified device.")
          break  # Exit the while loop if the device does not exist
      break
      
    except serial.SerialException:
      print("Error: Could not connect to Arduino. Please check Bluetooth pairing, device address, and baud rate.")
      break  # Exit the while loop if there is an error
  
async def handle_client(websocket, path):
  # Log when a client connects
  print(f"Client connected: {websocket.remote_address}")

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
          check_serial_connection_and_send(controls[data['direction']])
        except Exception as e:
          print(f"something went wrong with the control command: {e}")
          
      await websocket.send(message)
  finally:
    # Log when a client disconnects
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
  for interface in interfaces[:2]:
    addrs = netifaces.ifaddresses(interface)
    # print(f"Interface: {interface}")
    print(f"Listening on: ws://{list(addrs.values())[1][0]['addr']}:5002")
  print("Press Ctrl+C to stop the server")

  main()





