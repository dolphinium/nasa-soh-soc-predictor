# NASA Battery State of Health (SoH) Predictor

This application predicts the State of Health (SoH) of NASA batteries using LSTM neural networks. It features a FastAPI backend for predictions and a Streamlit frontend for visualization.

## Features

- SoH prediction for specific battery cycles
- Interactive visualization of battery health trends
- Support for multiple NASA batteries (B0005, B0006, B0018)
- Optimized data processing for efficient performance

## Data Optimization

The application uses optimized battery cycle data that has been preprocessed to:
- Keep only essential features used by the model
- Remove redundant measurements
- Filter for discharge cycles only
- Achieve ~95% reduction in file size while maintaining all necessary information

Essential features retained:
- cycle_number
- measurement_time_relative
- voltage_measured_smooth
- current_measured_smooth
- temperature_measured_smooth
- soh

## Prerequisites

- Docker and Docker Compose
- At least 4GB of available RAM
- Internet connection (for pulling Docker images)

## Quick Start

1. Clone the repository:
```bash
git clone [repository-url]
cd nasa-battery-soh-soc-predictor/app/
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend (Streamlit): http://localhost:8501
- Backend API (FastAPI): http://localhost:5000
- API Documentation: http://localhost:5000/docs

## Usage

1. Open the Streamlit interface in your browser
2. Select a battery ID from the sidebar (B0005, B0006, or B0018)
3. Choose a cycle number from the available range
4. Click "Predict SoH" to get the prediction
5. View the prediction plotted against historical data

## Project Structure

```
nasa-battery-soh-soc-predictor/
├── app/
│   ├── backend/
│   │   └── main.py           # FastAPI backend server
│   │   └── requirements.txt  # Backend dependencies
│   │   └── Dockerfile  # Backend Dockerfile
│   ├── frontend/
│   │   └── streamlit_app.py  # Streamlit frontend interface
│   │   └── requirements.txt  # Frontend dependencies
│   │   └── Dockerfile  # Frontend Dockerfile
│   ├── data/
│   │   └── processed_data/   # Optimized battery cycle data
│   └── models/              # Trained LSTM models
│   └── docker-compose.yml              # Docker Compose file
```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /predict/soh/{battery_id}`: Get SoH prediction for a specific battery cycle
  - Parameters:
    - `battery_id`: Battery identifier (B0005, B0006, B0018)
    - `cycle_number`: The cycle number to predict

## Development

To run the application in development mode:

1. Backend:
```bash
cd app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

2. Frontend:
```bash
cd app/frontend
streamlit run streamlit_app.py
```



