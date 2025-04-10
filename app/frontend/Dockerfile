# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the frontend application code into the container at /app
COPY streamlit_app.py .
# Note: We don't copy data here; it will be mounted as a volume

# Make port 8501 available
EXPOSE 8501

# Define environment variable (optional, good practice)
ENV PYTHONUNBUFFERED=1

# Run streamlit_app.py when the container launches
# --server.port and --server.address ensure it binds correctly inside the container
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]