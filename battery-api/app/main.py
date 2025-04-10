# app/main.py
from fastapi import FastAPI
from .routers import prediction # Import the prediction router

# Optional: Add metadata for API docs
description = """
Battery SoH Prediction API 🚀

Predicts the State of Health (SoH) of Lithium-Ion batteries
based on cycle summary features.
"""

app = FastAPI(
    title="Battery Prediction API",
    description=description,
    version="0.1.0",
    # Optional: Add contact info, license, etc.
    # contact={
    #     "name": "Your Name",
    #     "email": "your.email@example.com",
    # },
)

# Include the router from routers/prediction.py
app.include_router(prediction.router)

# A simple root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Battery Prediction API!"}

# Add more global configurations or middleware if needed