# Use slim Python image as base
FROM python:3.11-slim

# Set environment variables to avoid interactive prompts during the build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget software-properties-common && \
    apt-get install -y openjdk-17-jdk libpq-dev python3-dev&& \
    apt-get clean

# Install build-essential (gcc and related build tools) to compile psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into container
COPY . /app

# Expose necessary ports
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]