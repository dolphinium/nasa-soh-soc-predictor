# app/models/soc_model.py
import joblib
import pandas as pd
import os
import json
from ..schemas.prediction import SoCInputFeatures # Import the SoC input schema

MODEL_DIR = 'saved_models'
MODEL_PATH = os.path.join(MODEL_DIR, 'soc_random_forest_model.joblib')
FEATURES_PATH = os.path.join(MODEL_DIR, 'soc_model_features.json')

# --- Load Model and Features ---
_soc_model = None
_soc_features = None

def load_soc_model():
    """Loads the SoC model and features if not already loaded."""
    global _soc_model, _soc_features
    if _soc_model is None:
        try:
            print(f"Loading SoC model from: {MODEL_PATH}")
            _soc_model = joblib.load(MODEL_PATH)
            print("SoC model loaded successfully.")
        except FileNotFoundError:
            print(f"Error: SoC Model file not found at {MODEL_PATH}")
            raise FileNotFoundError(f"SoC Model file not found at {MODEL_PATH}")
        except Exception as e:
            print(f"Error loading SoC model: {e}")
            raise e

    if _soc_features is None:
        try:
            print(f"Loading SoC model features from: {FEATURES_PATH}")
            with open(FEATURES_PATH, 'r') as f:
                _soc_features = json.load(f)
            print("SoC Model features loaded successfully.")
        except FileNotFoundError:
            print(f"Error: SoC Features file not found at {FEATURES_PATH}")
            raise FileNotFoundError(f"SoC Features file not found at {FEATURES_PATH}")
        except Exception as e:
            print(f"Error loading SoC features: {e}")
            raise e
    return _soc_model, _soc_features


def predict_soc(input_data: SoCInputFeatures) -> float:
    """Predicts SoC for a single input instance."""
    model, features = load_soc_model() # Ensure model is loaded

    if model is None or features is None:
        raise ValueError("SoC Model or features not loaded properly.")

    # Convert Pydantic model to DataFrame row in the correct feature order
    input_df = pd.DataFrame([input_data.model_dump()], columns=features)
    # For Pydantic v1 use: input_df = pd.DataFrame([input_data.dict()], columns=features)


    # Make prediction
    prediction = model.predict(input_df)

    # Return the single prediction value
    return float(prediction[0])