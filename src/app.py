from flask import Flask, render_template
from .api.get_songs_by_weighted import api_songs_weighted
from .api.get_songs_by_band_selection import api_songs_bands
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.debug = True
app.secret_key=os.getenv('SECRET_KEY')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs')
def songs():
    return render_template('songs.html')


@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register the API blueprint
app.register_blueprint(api_songs_weighted)
app.register_blueprint(api_songs_bands)

if __name__ == '__main__':
    app.run(debug=True)