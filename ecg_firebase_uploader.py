import serial
import time
import requests
import json

# === CONFIGURATION ===
SERIAL_PORT = 'COM3'  # Change to your Arduino port
BAUD_RATE = 9600
FIREBASE_URL = 'https://YOUR_PROJECT_ID.firebaseio.com/ecg.json'  # Replace with your Firebase Realtime Database URL

print("Starting ECG data uploader...")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            try:
                value = float(line)
                # Upload to Firebase
                data = {"timestamp": time.time(), "value": value}
                requests.post(FIREBASE_URL, data=json.dumps(data))
                print(f"Uploaded: {data}")
            except ValueError:
                pass  # Ignore non-numeric lines
        time.sleep(0.01)
except serial.SerialException as e:
    print(f"Serial error: {e}")
except Exception as e:
    print(f"Error: {e}")
