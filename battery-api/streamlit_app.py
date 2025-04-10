# streamlit_app.py
import streamlit as st
import requests
import pandas as pd # Used just to structure the input easily

st.set_page_config(layout="wide") # Use wide layout

st.title("🔋 Lithium-Ion Battery SoH & SoC Prediction")

# --- Configuration ---
# Use the SERVICE NAME defined in docker-compose.yml for the backend URL
# Docker networking will resolve 'backend_api' to the correct container IP
BACKEND_URL = "http://backend_api:8000" # Ensure 'backend_api' matches your service name
SOH_ENDPOINT = f"{BACKEND_URL}/predict/soh"
SOC_ENDPOINT = f"{BACKEND_URL}/predict/soc"

# --- Sidebar for Input ---
st.sidebar.header("Input Features")

# == SoH Prediction Input ==
st.sidebar.subheader("State of Health (SoH) Prediction")
st.sidebar.info("Provide summary features for a complete discharge cycle.")

# Use columns for better layout in sidebar
col1_soh, col2_soh = st.sidebar.columns(2)

# Get example values from your features JSON or use defaults
# Make sure keys match SoHInputFeatures schema
soh_input = {
    "cycle": col1_soh.number_input("Cycle Number", min_value=1, value=100, step=1, key="soh_cycle"),
    "discharge_time": col2_soh.number_input("Discharge Time (s)", min_value=0.0, value=2950.0, step=10.0, format="%.1f", key="soh_discharge_time"),
    "start_voltage": col1_soh.number_input("Start Voltage (V)", min_value=2.0, max_value=5.0, value=4.17, format="%.3f", key="soh_start_v"),
    "mean_voltage": col2_soh.number_input("Mean Voltage (V)", min_value=2.0, max_value=5.0, value=3.42, format="%.3f", key="soh_mean_v"),
    "min_voltage": col1_soh.number_input("Min Voltage (V)", min_value=2.0, max_value=5.0, value=2.65, format="%.3f", key="soh_min_v"),
    "delta_voltage": col2_soh.number_input("Delta Voltage (V)", min_value=0.0, max_value=3.0, value=1.52, format="%.3f", key="soh_delta_v"),
    "start_temperature": col1_soh.number_input("Start Temperature (°C)", min_value=0.0, max_value=60.0, value=24.8, format="%.2f", key="soh_start_t"),
    "mean_temperature": col2_soh.number_input("Mean Temperature (°C)", min_value=0.0, max_value=60.0, value=34.1, format="%.2f", key="soh_mean_t"),
    "max_temperature": col1_soh.number_input("Max Temperature (°C)", min_value=0.0, max_value=60.0, value=41.2, format="%.2f", key="soh_max_t"),
    "delta_temperature": col2_soh.number_input("Delta Temperature (°C)", min_value=0.0, max_value=30.0, value=16.4, format="%.2f", key="soh_delta_t"),
}

predict_soh_button = st.sidebar.button("Predict SoH", key="predict_soh")

# == SoC Prediction Input ==
st.sidebar.subheader("State of Charge (SoC) Prediction")
st.sidebar.info("Provide instantaneous measurements from a time-step.")

# Use columns for better layout
col1_soc, col2_soc = st.sidebar.columns(2)

# Make sure keys match SoCInputFeatures schema
soc_input = {
    "time": col1_soc.number_input("Time in Cycle (s)", min_value=0.0, value=1200.0, step=10.0, format="%.1f", key="soc_time"),
    "voltage_measured": col2_soc.number_input("Voltage Measured (V)", min_value=2.0, max_value=5.0, value=3.61, format="%.3f", key="soc_volt"),
    "current_measured": col1_soc.number_input("Current Measured (A)", min_value=-5.0, max_value=1.0, value=-2.009, format="%.3f", key="soc_curr"),
    "temperature_measured": col2_soc.number_input("Temperature Measured (°C)", min_value=0.0, max_value=60.0, value=32.5, format="%.2f", key="soc_temp"),
    # Critical: SoC prediction needs SoH as input
    "SoH": col1_soc.number_input("Current SoH (%)", min_value=0.0, max_value=110.0, value=90.0, step=1.0, format="%.1f", key="soc_soh_input"),
}

predict_soc_button = st.sidebar.button("Predict SoC", key="predict_soc")


# --- Main Area for Output ---
st.header("Prediction Results")

# Placeholder for results
soh_result_area = st.empty()
soc_result_area = st.empty()

if predict_soh_button:
    soh_result_area.info("Sending request to SoH prediction API...")
    try:
        response = requests.post(SOH_ENDPOINT, json=soh_input, timeout=10) # Add timeout
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

        if response.status_code == 200:
            result = response.json()
            predicted_soh = result.get("predicted_SoH")
            soh_result_area.metric(label="Predicted State of Health (SoH)", value=f"{predicted_soh:.2f} %")
            # Optionally update the default SoH input for the SoC section
            # st.session_state.soc_soh_input = predicted_soh
        else:
             soh_result_area.error(f"Error from API: Status {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        soh_result_area.error(f"Connection Error: Could not connect to the backend API at {BACKEND_URL}. Is it running?")
    except requests.exceptions.Timeout:
         soh_result_area.error("Request timed out. The backend API might be slow or unresponsive.")
    except requests.exceptions.RequestException as e:
        soh_result_area.error(f"An error occurred during the API request: {e}")


if predict_soc_button:
    soc_result_area.info("Sending request to SoC prediction API...")
    try:
        response = requests.post(SOC_ENDPOINT, json=soc_input, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()
            predicted_soc = result.get("predicted_SoC")
            soc_result_area.metric(label="Predicted State of Charge (SoC)", value=f"{predicted_soc:.2f} %")
        else:
             soc_result_area.error(f"Error from API: Status {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        soc_result_area.error(f"Connection Error: Could not connect to the backend API at {BACKEND_URL}. Is it running?")
    except requests.exceptions.Timeout:
        soc_result_area.error("Request timed out. The backend API might be slow or unresponsive.")
    except requests.exceptions.RequestException as e:
        soc_result_area.error(f"An error occurred during the API request: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Enter battery parameters and click predict.")