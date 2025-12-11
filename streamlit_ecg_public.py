import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt

FIREBASE_URL = 'https://YOUR_PROJECT_ID.firebaseio.com/ecg.json'  # Replace with your Firebase Realtime Database URL

st.title("Public Real-Time ECG Monitoring")

refresh_rate = st.slider("Refresh rate (seconds)", 1, 10, 2)
max_points = st.slider("Max points to display", 100, 2000, 500)

plot_placeholder = st.empty()

while True:
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200 and response.json():
            data = response.json()
            df = pd.DataFrame(list(data.values()))
            df = df.sort_values('timestamp')
            if len(df) > max_points:
                df = df.iloc[-max_points:]
            fig, ax = plt.subplots()
            ax.plot(df['value'].values)
            ax.set_title("ECG Signal (Live)")
            ax.set_xlabel("Sample")
            ax.set_ylabel("Amplitude")
            plot_placeholder.pyplot(fig)
        else:
            st.warning("No data received yet.")
    except Exception as e:
        st.error(f"Error: {e}")
    time.sleep(refresh_rate)
