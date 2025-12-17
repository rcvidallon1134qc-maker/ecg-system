
import streamlit as st
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

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

# Detect if running in a cloud environment (e.g., Streamlit Cloud, Vercel, etc.)
def is_cloud():
    # Check for common environment variables in cloud deployments
    return (
        os.environ.get("STREAMLIT_SERVER_HEADLESS") == "1" or
        os.environ.get("VERCEL") == "1" or
        os.environ.get("DYNO") is not None or
        os.environ.get("RENDER") == "true" or
        os.environ.get("STREAMPOD") == "1"
    )

if st.session_state.running:
    if is_cloud() or not SERIAL_AVAILABLE:
        st.warning("Serial port access is not available in this environment.\n\nIf you are running this app in the cloud, real-time ECG monitoring from Arduino is only available when running locally.\n\nBelow is a simulated ECG signal for demo purposes.")
        # Simulate ECG data
        t = np.linspace(0, 2*np.pi, BUFFER_SIZE)
        # Simulate a noisy ECG-like signal
        buffer = 1.5 * np.sin(5 * t) + 0.5 * np.sin(15 * t) + 0.2 * np.random.randn(BUFFER_SIZE)
        fig, ax = plt.subplots()
        ax.plot(buffer)
        ax.set_title("Simulated Real-Time ECG Signal")
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude")
        plot_placeholder.pyplot(fig)
    else:
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
        except Exception as e:
            st.error(f"Serial error: {e}")
