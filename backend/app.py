from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

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
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/items-prices"

    try:
        # Récupérer les données actuelles des prix des ressources
        response = requests.get(url)
        response.raise_for_status()
        items_prices = response.json()

        # Réinitialiser les prix
        updated_prices = []
        for item in items_prices:
            updated_prices.append({
                "id": item["id"],
                "price": "",
            })

        # Mettre à jour les prix des ressources
        for price in updated_prices:
            try:
                response = requests.post(url, json=price)
                response.raise_for_status()
                print(f"Prix réinitialisé pour l'ID {price['id']}")
            except requests.exceptions.HTTPError as http_err:
                print(f"Erreur HTTP lors de la réinitialisation des prix pour l'ID {
                      price['id']} : {http_err}")
            except Exception as err:
                print(f"Erreur lors de la réinitialisation des prix pour l'ID {
                      price['id']} : {err}")

        return jsonify({"message": "Prices for resources have been cleared"}), 200

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"Erreur HTTP lors de la récupération des prix des ressources : {http_err}"}), 500
    except Exception as err:
        return jsonify({"error": f"Erreur lors de la récupération des prix des ressources : {err}"}), 500


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
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/resources-prices"

    try:
        # Récupérer les données actuelles des prix des ressources
        response = requests.get(url)
        response.raise_for_status()
        resources_prices = response.json()

        # Réinitialiser les prix
        updated_prices = []
        for resource in resources_prices:
            updated_prices.append({
                "id": resource["id"],
                "price_1": "",
                "price_10": "",
                "price_100": ""
            })

        # Mettre à jour les prix des ressources
        for price in updated_prices:
            try:
                response = requests.post(url, json=price)
                response.raise_for_status()
                print(f"Prix réinitialisé pour l'ID {price['id']}")
            except requests.exceptions.HTTPError as http_err:
                print(f"Erreur HTTP lors de la réinitialisation des prix pour l'ID {
                      price['id']} : {http_err}")
            except Exception as err:
                print(f"Erreur lors de la réinitialisation des prix pour l'ID {
                      price['id']} : {err}")

        return jsonify({"message": "Prices for resources have been cleared"}), 200

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"Erreur HTTP lors de la récupération des prix des ressources : {http_err}"}), 500
    except Exception as err:
        return jsonify({"error": f"Erreur lors de la récupération des prix des ressources : {err}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
