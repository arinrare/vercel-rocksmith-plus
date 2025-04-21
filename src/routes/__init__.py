from flask import Blueprint

# Create a blueprint for the routes
routes_bp = Blueprint('routes', __name__)

# Import the individual route modules
from . import some_route  # Replace with actual route module names as needed
# Add more imports as necessary for additional routes

# Register the blueprint with the main app in src/app.py
# app.register_blueprint(routes_bp)  # Uncomment this line in app.py to register the blueprint