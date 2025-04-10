# app/routers/prediction.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
# Import BOTH SoH and SoC schemas
from ..schemas.prediction import (
    SoHInputFeatures, SoHPredictionResponse,
    SoCInputFeatures, SoCPredictionResponse
)
# Import BOTH model modules
from ..models import soh_model, soc_model

router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]
)

# --- Optional: Combined Dependency ---
# You could create a dependency that tries to load both models
async def load_all_models():
     try:
         soh_model.load_model()
         soc_model.load_soc_model()
     except Exception as e:
         print(f"FATAL: Could not load one or more models on startup. Error: {e}")
         # Decide how to handle failure (e.g., log and continue, or raise)


# --- SoH Endpoint (Existing) ---
@router.post("/soh", response_model=SoHPredictionResponse #, dependencies=[Depends(load_all_models)] # Add dependency if using
            )
async def predict_single_soh(input_data: SoHInputFeatures):
    """
    Predicts the State of Health (SoH) for a single battery cycle summary.
    Input should be a JSON object matching the `SoHInputFeatures` schema.
    """
    try:
        predicted_value = soh_model.predict_soh(input_data)
        return SoHPredictionResponse(predicted_SoH=predicted_value)
    except FileNotFoundError as e:
         raise HTTPException(status_code=500, detail=f"Model file error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {e}")
    except Exception as e:
        print(f"Unexpected error during SoH prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during SoH prediction.")


# --- NEW SoC Endpoint ---
@router.post("/soc", response_model=SoCPredictionResponse #, dependencies=[Depends(load_all_models)] # Add dependency if using
            )
async def predict_single_soc(input_data: SoCInputFeatures):
    """
    Predicts the State of Charge (SoC) for a single time-step measurement.

    Input should be a JSON object matching the `SoCInputFeatures` schema,
    including the battery's current estimated SoH.
    """
    try:
        predicted_value = soc_model.predict_soc(input_data)
        # Clamp prediction between 0 and 100 as SoC cannot go outside this range
        predicted_value = max(0.0, min(100.0, predicted_value))
        return SoCPredictionResponse(predicted_SoC=predicted_value)
    except FileNotFoundError as e:
         raise HTTPException(status_code=500, detail=f"Model file error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {e}")
    except Exception as e:
        print(f"Unexpected error during SoC prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during SoC prediction.")