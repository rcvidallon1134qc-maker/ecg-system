
import streamlit as st
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# Streamlit app title
st.title("Real-Time ECG Monitoring (Arduino AD8232)")

# Mode selection
mode = st.radio("Select Mode:", ["Real Serial Port", "Simulated ECG Data"])

# Serial port configuration
def get_serial_ports():
    if SERIAL_AVAILABLE:
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    return []

if mode == "Real Serial Port":
    available_ports = get_serial_ports()
    default_port = "COM5"
    if available_ports:
        # If COM5 is available, set it as the default selection
        default_index = 0
        if default_port in available_ports:
            default_index = available_ports.index(default_port)
        SERIAL_PORT = st.selectbox("Select Serial Port:", available_ports, index=default_index)
    else:
        SERIAL_PORT = st.text_input("Enter Serial Port (e.g., COM5 or /dev/ttyUSB0):", default_port)
else:
    SERIAL_PORT = None
    
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

# Function to generate simulated ECG data
def generate_simulated_ecg(t):
    """Generate a simulated ECG waveform"""
    # Simple ECG simulation with P, QRS, and T waves
    heart_rate = 75  # bpm
    frequency = heart_rate / 60  # Hz
    
    # Create a synthetic ECG pattern
    ecg = 0
    ecg += 0.3 * np.sin(2 * np.pi * frequency * t)  # P wave
    ecg += 1.5 * np.sin(2 * np.pi * frequency * 5 * t) * np.exp(-10 * ((t % (1/frequency)) - 0.15)**2)  # QRS complex
    ecg += 0.4 * np.sin(2 * np.pi * frequency * 2 * t)  # T wave
    ecg += np.random.normal(0, 0.05)  # Add some noise
    
    # Scale to ADC range (0-1023 for 10-bit ADC like Arduino)
    ecg_value = int(512 + ecg * 100)
    return max(0, min(1023, ecg_value))

# Main loop for reading and plotting ECG data
if st.session_state.running:
    try:
        buffer = []
        
        if mode == "Real Serial Port":
            if not SERIAL_AVAILABLE:
                st.error("Serial library not available. Please install pyserial: pip install pyserial")
                st.stop()
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            st.info(f"Reading from {SERIAL_PORT} at {BAUD_RATE} baud...")
        else:
            ser = None
            st.info("Simulating ECG data (75 bpm with realistic waveform)...")
            
        t = 0
        while st.session_state.running:
            if mode == "Real Serial Port":
                # Read from serial port
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    try:
                        value = float(line)
                        buffer.append(value)
                        if len(buffer) > BUFFER_SIZE:
                            buffer = buffer[-BUFFER_SIZE:]
                    except ValueError:
                        pass  # Ignore non-numeric lines
            else:
                # Generate simulated data
                value = generate_simulated_ecg(t)
                buffer.append(value)
                if len(buffer) > BUFFER_SIZE:
                    buffer = buffer[-BUFFER_SIZE:]
                t += 0.01
                
            # Plot
            if len(buffer) > 0:
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(buffer, color='red', linewidth=1)
                ax.set_title("Real-Time ECG Signal")
                ax.set_xlabel("Sample")
                ax.set_ylabel("Amplitude")
                ax.grid(True, alpha=0.3)
                plot_placeholder.pyplot(fig)
                plt.close(fig)
                
            time.sleep(0.01)
            
        if ser:
            ser.close()
    except serial.SerialException as e:
        st.error(f"Serial error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Click 'Start Monitoring' to begin.")
