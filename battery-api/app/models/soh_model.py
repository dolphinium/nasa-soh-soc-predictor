# app/models/soh_model.py
import joblib
import pandas as pd
import os
import json
from ..schemas.prediction import SoHInputFeatures # Import the input schema

MODEL_DIR = 'saved_models' # Or read from environment variable
MODEL_PATH = os.path.join(MODEL_DIR, 'soh_random_forest_model.joblib')
FEATURES_PATH = os.path.join(MODEL_DIR, 'soh_model_features.json')

# --- Load Model and Features ---
_model = None
_features = None

def load_model():
    """Loads the model and features if not already loaded."""
    global _model, _features
    if _model is None:
        try:
            print(f"Loading SoH model from: {MODEL_PATH}")
            _model = joblib.load(MODEL_PATH)
            print("SoH model loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Model file not found at {MODEL_PATH}")
            # Handle error appropriately - raise exception or return None
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e # Re-raise the exception

    if _features is None:
        try:
            print(f"Loading model features from: {FEATURES_PATH}")
            with open(FEATURES_PATH, 'r') as f:
                _features = json.load(f)
            print("Model features loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Features file not found at {FEATURES_PATH}")
            raise FileNotFoundError(f"Features file not found at {FEATURES_PATH}")
        except Exception as e:
            print(f"Error loading features: {e}")
            raise e
    return _model, _features


def predict_soh(input_data: SoHInputFeatures) -> float:
    """Predicts SoH for a single input instance."""
    model, features = load_model() # Ensure model is loaded

    if model is None or features is None:
        # Handle case where loading failed (e.g., raise an exception)
        raise ValueError("SoH Model or features not loaded properly.")

    # Convert Pydantic model to DataFrame row in the correct feature order
    input_df = pd.DataFrame([input_data.model_dump()], columns=features)
    # For Pydantic v1 use: input_df = pd.DataFrame([input_data.dict()], columns=features)


    # Make prediction
    prediction = model.predict(input_df)

    # Prediction is likely a numpy array, get the first element
    return float(prediction[0])

# Optional: Add a batch prediction function if needed
# def predict_soh_batch(input_list: List[SoHInputFeatures]) -> List[float]:
#     ...