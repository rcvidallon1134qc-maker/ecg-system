import streamlit as st
import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit app title
st.title("Real-Time ECG Monitoring (Arduino AD8232)")

# Serial port configuration
SERIAL_PORT = st.text_input("Enter Serial Port (e.g., COM3 or /dev/ttyUSB0):", "COM3")
BAUD_RATE = 9600

# Number of data points to display
BUFFER_SIZE = st.slider("ECG Buffer Size (samples)", min_value=100, max_value=2000, value=500)

# Start/Stop button
start = st.button("Start Monitoring")
stop = st.button("Stop Monitoring")

# Placeholder for plot
plot_placeholder = st.empty()

# State to control loop
if 'running' not in st.session_state:
    st.session_state.running = False

if start:
    st.session_state.running = True
if stop:
    st.session_state.running = False

# Main loop for reading and plotting ECG data
if st.session_state.running:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        buffer = []
        st.info(f"Reading from {SERIAL_PORT} at {BAUD_RATE} baud...")
        while st.session_state.running:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                try:
                    value = float(line)
                    buffer.append(value)
                    if len(buffer) > BUFFER_SIZE:
                        buffer = buffer[-BUFFER_SIZE:]
                    # Plot
                    fig, ax = plt.subplots()
                    ax.plot(buffer)
                    ax.set_title("Real-Time ECG Signal")
                    ax.set_xlabel("Sample")
                    ax.set_ylabel("Amplitude")
                    plot_placeholder.pyplot(fig)
                except ValueError:
                    pass  # Ignore non-numeric lines
            time.sleep(0.01)
        ser.close()
    except serial.SerialException as e:
        st.error(f"Serial error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Click 'Start Monitoring' to begin.")
