from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Autoriser les requêtes de toutes les origines
CORS(app, origins=["http://localhost:3000"])

items = []
resources = []
consumables = []

# Routes pour les items


@app.route('/items', methods=['POST'])
def add_item():
    data = request.json
    items.append(data)
    return jsonify(data), 201


@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)


@app.route('/items/clear', methods=['POST'])
def clear_items():
    global items
    items = []
    return jsonify({"message": "All items cleared"}), 200

# Routes pour les resources


@app.route('/resources', methods=['POST'])
def add_resource():
    data = request.json
    resources.append(data)
    return jsonify(data), 201


@app.route('/resources', methods=['GET'])
def get_resources():
    return jsonify(resources)


@app.route('/resources/clear', methods=['POST'])
def clear_resources():
    global resources
    resources = []
    return jsonify({"message": "All resources cleared"}), 200

# Routes pour les consumables


@app.route('/consumables', methods=['POST'])
def add_consumable():
    data = request.json
    consumables.append(data)
    return jsonify(data), 201


@app.route('/consumables', methods=['GET'])
def get_consumables():
    return jsonify(consumables)


@app.route('/consumables/clear', methods=['POST'])
def clear_consumables():
    global consumables
    consumables = []
    return jsonify({"message": "All consumables cleared"}), 200


if __name__ == '__main__':
    app.run(port=5000)
