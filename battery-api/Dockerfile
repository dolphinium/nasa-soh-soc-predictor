# Dockerfile

# Use an official Python runtime as a parent image
# Choose a version compatible with your development environment (e.g., 3.10)
# Using slim variant for smaller image size
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install system dependencies if needed (e.g., for certain ML libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /code
COPY requirements.txt .

# Install Python dependencies specified in requirements.txt
# --no-cache-dir reduces image size, --upgrade ensures pip is up-to-date
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code (app directory) and saved models into the container at /code
# Ensure saved_models is relative to the Dockerfile location (project root)
COPY ./app /code/app
COPY ./saved_models /code/saved_models

# Expose the port the app runs on (default Uvicorn port)
EXPOSE 8000

# Define the command to run the application using Uvicorn
# Use 0.0.0.0 to make it accessible from outside the container
# Remove --reload for production-like image
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]