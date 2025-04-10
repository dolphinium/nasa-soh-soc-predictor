# app/schemas/prediction.py
from pydantic import BaseModel, Field
from typing import List

# Define the input features based on your soh_model_features.json
# Use descriptive names and example values for documentation
class SoHInputFeatures(BaseModel):
    cycle: int = Field(..., example=100)
    discharge_time: float = Field(..., example=3000.5)
    start_voltage: float = Field(..., example=4.18)
    mean_voltage: float = Field(..., example=3.45)
    min_voltage: float = Field(..., example=2.7)
    delta_voltage: float = Field(..., example=1.48)
    start_temperature: float = Field(..., example=25.5)
    mean_temperature: float = Field(..., example=33.0)
    max_temperature: float = Field(..., example=40.1)
    delta_temperature: float = Field(..., example=14.6)
    # Add ambient_temperature if you included it in the model features
    # ambient_temperature: float = Field(..., example=24.0)

    # Example for Pydantic v1/v2 compatibility if needed
    class Config:
        # For Pydantic v2:
        json_schema_extra = {
             "example": {
                "cycle": 110,
                "discharge_time": 2950.0,
                "start_voltage": 4.17,
                "mean_voltage": 3.42,
                "min_voltage": 2.65,
                "delta_voltage": 1.52,
                "start_temperature": 24.8,
                "mean_temperature": 34.1,
                "max_temperature": 41.2,
                "delta_temperature": 16.4
            }
        }
        # For Pydantic v1:
        # schema_extra = { ... } # Put example inside schema_extra
        
        
# Define input features based on soc_model_features.json
class SoCInputFeatures(BaseModel):
    time: float = Field(..., example=1500.0)
    voltage_measured: float = Field(..., example=3.5)
    current_measured: float = Field(..., example=-2.0)
    temperature_measured: float = Field(..., example=35.0)
    SoH: float = Field(..., example=85.0) # Add SoH as context
    # Add cycle if you included it in training
    # cycle: int = Field(..., example=50)

    class Config:
         json_schema_extra = {
             "example": {
                "time": 1200.5,
                "voltage_measured": 3.61,
                "current_measured": -2.009,
                "temperature_measured": 32.5,
                "SoH": 90.1
            }
        }

# Define the response model for SoC
class SoCPredictionResponse(BaseModel):
    predicted_SoC: float = Field(..., example=55.2)

# Define the response model
class SoHPredictionResponse(BaseModel):
    predicted_SoH: float = Field(..., example=75.5)

# Optional: Allow batch prediction
class SoHBatchInput(BaseModel):
    predictions: List[SoHInputFeatures]

class SoHBatchResponse(BaseModel):
    predictions: List[SoHPredictionResponse]