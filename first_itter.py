import serial
import time

bluetooth = "/dev/rfcomm0"
baud_rate = 9600

def connect_to_arduino():
    return serial.Serial(bluetooth, baud_rate)

def send_data_to_arduino(ser, data):
    ser.write(data.encode('utf-8'))
    response = ser.readline().decode('utf-8')
    print(response)

while True:
    try:
        ser = connect_to_arduino()
        print(f"Connected to Arduino (Bluetooth device: {bluetooth})!")
        break
    except serial.SerialException as e:
        print(f"Error: Could not connect to Arduino. Please check Bluetooth pairing, device address, and baud rate.")
        print(e)
        time.sleep(5)

try:
    while True:
        input_data = input("Enter a command: ")
        send_data_to_arduino(ser, input_data)
except serial.SerialException as e:
    print("Error communicating with Arduino:", e)
finally:
    if 'ser' in globals():
        ser.close()
        print("Serial port closed.")


