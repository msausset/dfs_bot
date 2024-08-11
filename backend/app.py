from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

items = []
resources = []

# Fonction pour vérifier si une ressource existe déjà


def resource_exists(resource_id):
    return any(resource['id'] == resource_id for resource in resources)

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
    resource_id = data.get('id')

    if resource_exists(resource_id):
        return jsonify({"message": "Resource already exists"}), 409

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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
