import requests


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
            "https://dfs-bot-4338ac8851d5.herokuapp.com/list-resources")
        response.raise_for_status()
        resources = response.json()
        return any(resource['id'] == resource_id for resource in resources)
    except requests.exceptions.RequestException as e:
        print(
            f"Erreur lors de la vérification de l'existence de la ressource : {e}")
        return False


def check_list_items_empty():
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/list-items"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return len(data) == 0
    except requests.exceptions.HTTPError as http_err:
        print(
            f"Erreur HTTP lors de la vérification des list-items : {http_err}")
        return False
    except Exception as err:
        print(f"Erreur lors de la vérification des list-items : {err}")
        return False


def check_items_prices_empty():
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/items-prices"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return len(data) == 0
    except requests.exceptions.HTTPError as http_err:
        print(
            f"Erreur HTTP lors de la vérification des items-prices : {http_err}")
        return False
    except Exception as err:
        print(f"Erreur lors de la vérification des items-prices : {err}")
        return False


def check_list_resources_empty():
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/list-resources"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return len(data) == 0
    except requests.exceptions.HTTPError as http_err:
        print(
            f"Erreur HTTP lors de la vérification des list-resources : {http_err}")
        return False
    except Exception as err:
        print(f"Erreur lors de la vérification des list-resources : {err}")
        return False


def check_resources_prices_empty():
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/resources-prices"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return len(data) == 0
    except requests.exceptions.HTTPError as http_err:
        print(
            f"Erreur HTTP lors de la vérification des resources-prices : {http_err}")
        return False
    except Exception as err:
        print(f"Erreur lors de la vérification des resources-prices : {err}")
        return False


def check_and_clear_prices():
    # Vérifiez si les prix des items ne sont pas vides
    if not check_items_prices_empty():
        print("La liste des prix des items n'est pas vide. Vidage de l'API ...")
        # Appel de la fonction pour vider l'API
        clear_prices_from_api("items-prices")
    elif not check_resources_prices_empty():
        print("La liste des prix des ressources n'est pas vide. Vidage de l'API ...")
        # Appel de la fonction pour vider l'API
        clear_prices_from_api("resources-prices")
    else:
        print("La liste des prix des items et des ressources sont vides. Aucun vidage nécessaire.")


def add_items_to_list(items):
    # URL pour ajouter les items à la liste
    list_items_url = "https://dfs-bot-4338ac8851d5.herokuapp.com/list-items"
    # URL pour ajouter les items aux prix des items
    items_prices_url = "https://dfs-bot-4338ac8851d5.herokuapp.com/items-prices"

    for item in items:
        # Préparer les données pour la route list-items
        list_item_data = {
            "id": item['id'],
            "item_name": item['name']['fr'],
            "item_slug": item['slug']['fr']
        }

        # Préparer les données pour la route items-prices
        items_prices_data = {
            "id": item['id'],
            "price_1": "",
            "price_10": "",
            "price_100": ""
        }

        try:
            # Ajouter l'item à la liste d'items
            response = requests.post(list_items_url, json=list_item_data)
            response.raise_for_status()
            print(f"Item ajouté à list-items: {item['name']['fr']}")

            # Ajouter les données de l'item aux prix des items
            response = requests.post(items_prices_url, json=items_prices_data)
            response.raise_for_status()
            print(f"Prix initialisé pour l'item {
                  item['name']['fr']} dans items-prices")

        except requests.exceptions.HTTPError as http_err:
            print(f"Erreur HTTP lors de l'ajout de l'item {
                  item['name']['fr']} : {http_err}")
        except Exception as err:
            print(f"Erreur lors de l'ajout de l'item {
                  item['name']['fr']} : {err}")


def send_price_to_api(item_id, item_name, price_text, item_number, api_route):
    url = f"https://dfs-bot-4338ac8851d5.herokuapp.com/{api_route}"
    data = {
        "id": item_id,
        "item_name": item_name,
        "price": clean_price(price_text.strip())
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print(f"Item {item_number}: {item_name.upper(
        )} - {clean_price(price_text.strip())} - Enregistré avec succès")
    except requests.exceptions.HTTPError as http_err:
        print(f"Item {item_number}: Erreur HTTP : {http_err}")
    except Exception as err:
        print(f"Item {item_number}: Erreur : {err}")


def clean_price(price_text):
    return price_text.replace(" ", "")
