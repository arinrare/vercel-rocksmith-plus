import os
import sys

# Add application directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import Flask app
from src.app import app as application