from flask import Flask, render_template
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)