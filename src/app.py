from flask import Flask

app = Flask(__name__)

# Configuration settings
app.config['DEBUG'] = True

# Import routes
from src.routes import *

if __name__ == '__main__':
    app.run()