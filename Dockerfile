# Use the official Python 3.11 slim image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install ffmpeg (required by pydub)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency definitions first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Expose the FastAPI application port
EXPOSE 8000

# Start the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]