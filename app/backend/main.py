from fastapi import FastAPI, HTTPException, BackgroundTasks
import numpy as np
import pandas as pd
import pickle
import os
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences
from pydantic import BaseModel
import uvicorn 
import asyncio 

# --- Configuration ---
MODEL_DIR = '/app/models/'
DATA_DIR = '/app/data/processed_data/'
MAX_SEQ_LENGTHS = {
    'B0005': 371,
    'B0006': 381,
    'B0018': 328
}
SEQUENCE_FEATURES = [
    'voltage_measured_smooth',
    'current_measured_smooth',
    'temperature_measured_smooth',
    'measurement_time_relative'
]

models_cache = {}
scalers_cache = {}
data_cache = {}
loading_tasks = {} 

class PredictionRequest(BaseModel):
    cycle_number: int

class PredictionResponse(BaseModel):
    battery_id: str
    cycle_number: int
    predicted_soh: float

async def load_resources_async(battery_id: str):
    """Asynchronously loads resources if not already loaded."""
    if battery_id in models_cache:
        return True # Already loaded

    # Check if already loading
    if battery_id in loading_tasks and not loading_tasks[battery_id].done():
        print(f"Waiting for resources for {battery_id} to finish loading...")
        await loading_tasks[battery_id]
        return battery_id in models_cache # Check again if loading succeeded

    # Start loading task
    print(f"Initiating resource loading for {battery_id}...")
    task = asyncio.create_task(load_resources_sync(battery_id))
    loading_tasks[battery_id] = task
    await task

    # Check if loading succeeded after task completion
    if battery_id in models_cache:
        print(f"Resources successfully loaded for {battery_id}.")
        del loading_tasks[battery_id] # Remove completed task tracker
        return True
    else:
        print(f"Resource loading failed for {battery_id}.")
        del loading_tasks[battery_id] # Remove failed task tracker
        return False

def load_resources_sync(battery_id: str):
    """Synchronous part of resource loading (runs in background task)."""
    model_path = os.path.join(MODEL_DIR, f'lstm_final_{battery_id}_soh.keras')
    scaler_path = os.path.join(MODEL_DIR, f'scaler_lstm_{battery_id}_soh.pkl')
    data_path = os.path.join(DATA_DIR, f'optimized_nasa_battery_data_{battery_id}_preprocessed.csv')

    try:
        # Check if files exist before trying to load
        if not os.path.exists(model_path): raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(scaler_path): raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        if not os.path.exists(data_path): raise FileNotFoundError(f"Data file not found: {data_path}")

        model = keras.models.load_model(model_path)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        df_data = pd.read_csv(data_path)

        # Store in cache upon successful load
        models_cache[battery_id] = model
        scalers_cache[battery_id] = scaler
        data_cache[battery_id] = df_data

    except Exception as e:
        print(f"Error loading resources sync for {battery_id}: {e}")
        # Ensure partial loads are cleaned up if error occurs
        if battery_id in models_cache: del models_cache[battery_id]
        if battery_id in scalers_cache: del scalers_cache[battery_id]
        if battery_id in data_cache: del data_cache[battery_id]
        # Re-raise the exception so the async task knows it failed
        raise e


app = FastAPI(title="Battery SoH Prediction API")

@app.get("/", summary="API Root/Health Check")
def read_root():
    return {"message": "Welcome to the Battery SoH Prediction API"}

@app.post("/predict/soh/{battery_id}",
            response_model=PredictionResponse,
            summary="Predict SoH for a given cycle")
async def predict_soh(battery_id: str, request_body: PredictionRequest, background_tasks: BackgroundTasks):
    """
    Predicts the State of Health (SoH) for a specific discharge cycle
    of a given battery.

    - **battery_id**: ID of the battery (e.g., B0005, B0006, B0018).
    - **request_body**: JSON containing the `cycle_number`.
    """
    # Trigger resource loading if needed, wait if already loading
    loaded = await load_resources_async(battery_id)
    if not loaded:
        raise HTTPException(status_code=503, detail=f"Resources for battery {battery_id} are unavailable or failed to load.")

    # Retrieve data for the cycle
    cycle_number = request_body.cycle_number
    df_battery = data_cache[battery_id]
    cycle_data = df_battery[df_battery['cycle_number'] == cycle_number].copy()

    if cycle_data.empty:
        raise HTTPException(status_code=404, detail=f"No data found for cycle {cycle_number} of battery {battery_id}")

    sequence = cycle_data[SEQUENCE_FEATURES].values
    if sequence.shape[0] == 0:
         raise HTTPException(status_code=500, detail=f"Extracted sequence is empty for cycle {cycle_number}")

    # Preprocess: Scale and Pad
    try:
        scaler = scalers_cache[battery_id]
        model = models_cache[battery_id]
        max_len = MAX_SEQ_LENGTHS.get(battery_id)
        if max_len is None:
            raise ValueError(f"Max sequence length not configured for {battery_id}")

        sequence_scaled = scaler.transform(sequence)
        sequence_reshaped = sequence_scaled.reshape(1, sequence.shape[0], sequence.shape[1])
        sequence_padded = pad_sequences(sequence_reshaped, maxlen=max_len, padding='post', dtype='float32', value=0.0)

    except Exception as e:
        print(f"Preprocessing error for {battery_id}, cycle {cycle_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to preprocess sequence data: {e}")

    # Predict
    try:
        prediction = model.predict(sequence_padded)
        predicted_soh = float(prediction[0][0])
    except Exception as e:
        print(f"Prediction error for {battery_id}, cycle {cycle_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {e}")

    # Return result
    result = PredictionResponse(
        battery_id=battery_id,
        cycle_number=cycle_number,
        predicted_soh=round(predicted_soh, 4)
    )
    print(f"Prediction result: {result}")
    return result

if __name__ == "__main__":
    print("Starting API server with uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=5000)