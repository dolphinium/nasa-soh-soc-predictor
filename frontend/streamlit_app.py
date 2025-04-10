import streamlit as st
import requests # To make requests to the FastAPI backend
import pandas as pd
import os
import plotly.graph_objects as go # For plotting

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000" # URL of your running FastAPI app
DATA_DIR = '../data/processed_data/' # Path to preprocessed battery CSVs relative to streamlit_app.py

# --- Helper function to load battery cycle info ---
@st.cache_data # Cache data to avoid reloading on every interaction
def load_battery_data(battery_id):
    """Loads cycle number and SoH for plotting."""
    filename = os.path.join(DATA_DIR, f'nasa_battery_data_{battery_id}_preprocessed.csv')
    if not os.path.exists(filename):
        st.error(f"Data file not found for {battery_id}: {filename}")
        return None
    try:
        df = pd.read_csv(filename)
        # Get unique cycle/SoH pairs, focusing on discharge for SoH value
        df_soh = df[df['cycle_type'] == 'discharge'].dropna(subset=['soh'])
        if df_soh.empty:
             st.warning(f"No discharge cycles with SoH found for {battery_id}")
             return df[['cycle_number']].drop_duplicates().sort_values('cycle_number') # Return cycles only
        return df_soh[['cycle_number', 'soh']].drop_duplicates().sort_values('cycle_number')
    except Exception as e:
        st.error(f"Error loading data for {battery_id}: {e}")
        return None

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("🔋 Battery State of Health (SoH) Predictor")

st.sidebar.header("Select Battery and Cycle")
available_batteries = ["B0005", "B0006", "B0018"] # Or detect from data dir
selected_battery = st.sidebar.selectbox("Battery ID:", available_batteries)

# Load data for the selected battery to get cycle range
battery_cycle_data = load_battery_data(selected_battery)

if battery_cycle_data is not None and not battery_cycle_data.empty:
    min_cycle = int(battery_cycle_data['cycle_number'].min())
    max_cycle = int(battery_cycle_data['cycle_number'].max())

    # Select cycle (only show discharge cycles if SoH exists)
    valid_cycles = battery_cycle_data['cycle_number'].unique()
    selected_cycle = st.sidebar.selectbox(f"Discharge Cycle Number ({min_cycle}-{max_cycle}):", valid_cycles)

    # --- Display Actual SoH Trend ---
    st.subheader(f"Actual SoH Trend for {selected_battery}")
    if 'soh' in battery_cycle_data.columns:
        fig_actual = go.Figure()
        fig_actual.add_trace(go.Scatter(x=battery_cycle_data['cycle_number'], y=battery_cycle_data['soh'],
                                      mode='lines+markers', name='Actual SoH'))
        fig_actual.update_layout(xaxis_title="Cycle Number", yaxis_title="SoH", yaxis_range=[0.5,1.1]) # Adjust range if needed
        st.plotly_chart(fig_actual, use_container_width=True)
    else:
        st.info("Actual SoH data not available for plotting.")


    # --- Prediction Section ---
    st.sidebar.markdown("---")
    if st.sidebar.button("Predict SoH"):
        predict_url = f"{API_BASE_URL}/predict/soh/{selected_battery}"
        payload = {"cycle_number": selected_cycle}

        st.subheader("Prediction Result")
        try:
            with st.spinner(f"Getting prediction for {selected_battery}, cycle {selected_cycle}..."):
                response = requests.post(predict_url, json=payload)
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            result = response.json()
            predicted_soh = result.get("predicted_soh")

            st.metric(label=f"Predicted SoH for Cycle {selected_cycle}", value=f"{predicted_soh:.4f}")

            # Optionally add prediction point to the plot
            if 'soh' in battery_cycle_data.columns:
                 fig_actual.add_trace(go.Scatter(x=[selected_cycle], y=[predicted_soh],
                                               mode='markers', name='Prediction', marker=dict(color='red', size=12, symbol='x')))
                 st.plotly_chart(fig_actual, use_container_width=True) # Re-display plot with prediction


        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            st.error(f"Is the FastAPI server running at {API_BASE_URL}?")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            # Try to show detail from API error if available
            try:
                error_detail = response.json().get('detail')
                if error_detail: st.error(f"API Error Detail: {error_detail}")
            except:
                pass # Ignore if response isn't JSON or detail key doesn't exist

elif battery_cycle_data is not None and battery_cycle_data.empty:
     st.warning(f"No valid cycles found for {selected_battery}")
else:
     st.error(f"Could not load data for {selected_battery}")

st.sidebar.markdown("---")
st.sidebar.info("Select a battery and a discharge cycle, then click 'Predict SoH'.")