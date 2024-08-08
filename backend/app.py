from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Autoriser les requêtes de toutes les origines
CORS(app, origins=["http://localhost:3000"])

prices = []


@app.route('/prices', methods=['POST'])
def add_price():
    data = request.json
    prices.append(data)
    return jsonify(data), 201


@app.route('/prices', methods=['GET'])
def get_prices():
    return jsonify(prices)


@app.route('/prices/clear', methods=['POST'])
def clear_prices():
    global prices
    prices = []
    return jsonify({"message": "All prices cleared"}), 200


if __name__ == '__main__':
    app.run(port=5000)
