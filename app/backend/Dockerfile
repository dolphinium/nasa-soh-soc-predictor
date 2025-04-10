# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size, --trusted-host is sometimes needed in network-restricted environments
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the backend application code into the container at /app
COPY main.py .
# Note: We don't copy models/data here; they will be mounted as volumes

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable (optional, good practice)
ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches using uvicorn
# Use 0.0.0.0 to ensure it's accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]