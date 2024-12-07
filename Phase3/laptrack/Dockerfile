# Use slim Python image as base
FROM python:3.11-slim

# Set environment variables to avoid interactive prompts during the build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget software-properties-common && \
    apt-get install -y openjdk-17-jdk libpq-dev python3-dev build-essential && \
    apt-get clean

# Create the Spark JARs directory (to avoid the error)
RUN mkdir -p /opt/spark/jars

# Download PostgreSQL JDBC Driver
RUN wget -O /opt/spark/jars/postgresql-42.5.0.jar https://jdbc.postgresql.org/download/postgresql-42.5.0.jar

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into container
COPY . /app

# Expose necessary ports
EXPOSE 8080

# Copy the startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Default command: Run the startup script
CMD ["/app/start.sh"]