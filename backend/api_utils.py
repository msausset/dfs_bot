import requests
import json
import os
from constants import CONFIG_FILE


def clear_prices_from_api(api_route):
    url = f"https://dfs-bot-4338ac8851d5.herokuapp.com/{api_route}/clear"
    try:
        response = requests.post(url)
        response.raise_for_status()
        print(f"API {api_route} vidée")
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP : {http_err}")
    except Exception as err:
        print(f"Erreur : {err}")


def fetch_items_from_api(hdv_option):
    url = "https://api.dofusdb.fr/items"
    items = []
    skip = 0
    limit = 50

    if hdv_option == 'typeId=167&typeId=104&typeId=40&typeId=38&typeId=108&typeId=107&typeId=34&typeId=119&typeId=111&typeId=56&typeId=35&typeId=152&typeId=60&typeId=57&typeId=228&typeId=71&typeId=39&typeId=106&typeId=47&typeId=103&typeId=59&typeId=105&typeId=109&typeId=51&typeId=50&typeId=36&typeId=53&typeId=54&typeId=41&typeId=48&typeId=65&typeId=98&typeId=229&typeId=219&typeId=15&typeId=183&typeId=164&level[$gt]=159':
        extra_ids = [14635, 15219, 15271]
        for item_id in extra_ids:
            response = requests.get(
                f"{url}?$limit={limit}&$skip={skip}&id={item_id}")
            data = response.json()
            items.extend(data['data'])

    while True:
        response = requests.get(
            f"{url}?$limit={limit}&$skip={skip}&{hdv_option}")
        data = response.json()
        items.extend(data['data'])

        if len(data['data']) < limit:
            break

        skip += limit

    return items


def fetch_recipes_from_api(item_id):
    url = f"https://api.dofusdb.fr/recipes?resultId={item_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        recipe_data = response.json().get('data', [])

        if not recipe_data:
            print(f"Aucune recette trouvée pour l'item ID: {item_id}")
            return []

        first_recipe = recipe_data[0]
        ingredient_ids = first_recipe.get('ingredientIds', [])

        ingredients = []
        for ingredient_id in ingredient_ids:
            ingredient_response = requests.get(
                f"https://api.dofusdb.fr/items/{ingredient_id}")
            ingredient_response.raise_for_status()
            ingredients.append(ingredient_response.json())

        return ingredients
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP lors de la récupération des recettes : {http_err}")
        return []
    except Exception as err:
        print(f"Erreur lors de la récupération des recettes : {err}")
        return []


def resource_exists(resource_id):
    try:
        response = requests.get(
            "https://dfs-bot-4338ac8851d5.herokuapp.com/resources")
        response.raise_for_status()
        resources = response.json()
        return any(resource['id'] == resource_id for resource in resources)
    except requests.exceptions.RequestException as e:
        print(
            f"Erreur lors de la vérification de l'existence de la ressource : {e}")
        return False
