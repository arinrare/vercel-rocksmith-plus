from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Flask API!"})

@app.route('/api/data', methods=['POST'])
def get_data():
    data = request.json
    return jsonify({"received": data}), 201

if __name__ == '__main__':
    app.run(debug=True)