#!/bin/bash

# Run the ETL script first
python ./etl/etl_script.py

# Start the Flask app
python ./flask_app/app.py