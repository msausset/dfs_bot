from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

list_items = []
items_prices = []
list_resources = []
resources_prices = []

# Fonction pour vérifier si une ressource existe déjà


def resource_exists(resource_id, resource_list):
    return any(resource['id'] == resource_id for resource in resource_list)

# Routes pour list-items


@app.route('/list-items', methods=['POST'])
def add_list_item():
    data = request.json
    list_items.append(data)
    return jsonify(data), 201


@app.route('/list-items', methods=['GET'])
def get_list_items():
    return jsonify(list_items)


@app.route('/list-items/clear', methods=['POST'])
def clear_list_items():
    global list_items
    list_items = []
    return jsonify({"message": "All list items cleared"}), 200

# Routes pour items-prices


@app.route('/items-prices', methods=['POST'])
def add_item_price():
    data = request.json
    items_prices.append(data)
    return jsonify(data), 201


@app.route('/items-prices', methods=['GET'])
def get_items_prices():
    return jsonify(items_prices)


@app.route('/items-prices/clear', methods=['POST'])
def clear_items_prices():
    global items_prices
    items_prices = []
    return jsonify({"message": "All items prices cleared"}), 200

# Routes pour list-resources


@app.route('/list-resources', methods=['POST'])
def add_list_resource():
    data = request.json
    if resource_exists(data.get('id'), list_resources):
        return jsonify({"message": "Resource already exists"}), 409

    list_resources.append(data)
    return jsonify(data), 201


@app.route('/list-resources', methods=['GET'])
def get_list_resources():
    return jsonify(list_resources)

# Routes pour resources-prices


@app.route('/resources-prices', methods=['POST'])
def add_resource_price():
    data = request.json
    if resource_exists(data.get('id'), resources_prices):
        return jsonify({"message": "Resource price already exists"}), 409

    resources_prices.append(data)
    return jsonify(data), 201


@app.route('/resources-prices', methods=['GET'])
def get_resources_prices():
    return jsonify(resources_prices)


@app.route('/resources-prices/clear', methods=['POST'])
def clear_resources_prices():
    global resources_prices
    resources_prices = []
    return jsonify({"message": "All resources prices cleared"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
