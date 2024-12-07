from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load configuration from config.py
app.config.from_object('config.Config')

db = SQLAlchemy(app)

from routes.laptop_routes import *
from routes.recommendation_routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)