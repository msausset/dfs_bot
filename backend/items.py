import requests
import pyautogui
import time
from PIL import Image
import pytesseract
import keyboard
import threading
import queue
import json
import os
import aiohttp
import asyncio

# Configurez le chemin vers le binaire Tesseract-OCR si nécessaire
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CONFIG_FILE = 'ItemsTotal.json'

# Variable globale pour contrôler l'exécution
stop_flag = False

# Définir les coordonnées globales
price_x, price_y = 1208, 328
price_width, price_height = 160, 38

first_x, first_y = 555, 256
second_x, second_y = 956, 288
third_x, third_y = 726, 255

# Queue pour stocker les données à envoyer à l'API
api_queue = queue.Queue()

# Définir les types d'items en fonction de l'HDV choisi
HDV_OPTIONS = {
    # Ressources
    '1': 'typeId=167&typeId=104&typeId=40&typeId=38&typeId=108&typeId=107&typeId=34&typeId=119&typeId=111&typeId=56&typeId=35&typeId=152&typeId=60&typeId=57&typeId=228&typeId=71&typeId=39&typeId=106&typeId=47&typeId=103&typeId=59&typeId=105&typeId=109&typeId=51&typeId=50&typeId=36&typeId=53&typeId=54&typeId=41&typeId=48&typeId=65&typeId=98&typeId=229&typeId=219&typeId=15&typeId=183&typeId=164&level[$gt]=159',
    '2': 'id=16944&id=11504&id=11507',  # Consommables
    # Équipements
    '3': '&typeId=82&typeId=1&typeId=9&typeId=10&typeId=11&typeId=16&typeId=17&level[$gt]=199',
}

# Définir les routes API en fonction de l'HDV choisi
API_ROUTES = {
    '1': 'list-resources',
    '2': 'list-resources',
    '3': 'items-prices',
}


def choose_hdv():
    print("Choisissez l'Hôtel de Vente (HDV) :")
    print("1. Ressources")
    print("2. Consommables")
    print("3. Équipements")
    choice = input("Entrez le numéro correspondant à votre choix: ")
    return choice, HDV_OPTIONS.get(choice, None), API_ROUTES.get(choice, 'items')


def fetch_items_from_api(hdv_option):
    if not hdv_option:
        print("Option HDV invalide. Utilisation de l'option par défaut.")
        hdv_option = 'typeId=82'  # Utilisation d'une valeur par défaut en cas de choix invalide

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


async def fetch_recipes_from_api_async(session, item_id):
    url = f"https://api.dofusdb.fr/recipes?resultId={item_id}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            recipe_data = (await response.json()).get('data', [])

            if not recipe_data:
                print(f"Aucune recette trouvée pour l'item ID: {item_id}")
                return []

            # On suppose que la première recette est la bonne
            first_recipe = recipe_data[0]
            ingredient_ids = first_recipe.get('ingredientIds', [])

            ingredients = []
            tasks = []
            for ingredient_id in ingredient_ids:
                tasks.append(fetch_ingredient(session, ingredient_id))

            # Attendre la fin de toutes les tâches de récupération des ingrédients
            ingredients = await asyncio.gather(*tasks)
            return [ingredient for sublist in ingredients for ingredient in sublist]

    except aiohttp.ClientResponseError as http_err:
        print(f"Erreur HTTP lors de la récupération des recettes : {http_err}")
        return []
    except Exception as err:
        print(f"Erreur lors de la récupération des recettes : {err}")
        return []


async def fetch_ingredient(session, ingredient_id):
    url = f"https://api.dofusdb.fr/items/{ingredient_id}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return [await response.json()]
    except aiohttp.ClientResponseError as http_err:
        print(f"Erreur HTTP lors de la récupération de l'ingrédient {
              ingredient_id} : {http_err}")
        return []
    except Exception as err:
        print(f"Erreur lors de la récupération de l'ingrédient {
              ingredient_id} : {err}")
        return []


async def handle_resource_retrieval(item_id):
    async with aiohttp.ClientSession() as session:
        ingredients = await fetch_recipes_from_api_async(session, item_id)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if not await resource_exists_async(session, ingredient_id):
                resource_data = {
                    "id": ingredient_id,
                    "item_name": ingredient['name']['fr'],
                    "item_slug": ingredient['slug']['fr'],
                }
                await send_resource_to_api_async(session, resource_data)


async def resource_exists_async(session, resource_id):
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/list-resources"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            resources = await response.json()
            return any(resource['id'] == resource_id for resource in resources)
    except aiohttp.ClientResponseError as e:
        print(
            f"Erreur lors de la vérification de l'existence de la ressource : {e}")
        return False


async def send_resource_to_api_async(session, resource_data):
    url = "https://dfs-bot-4338ac8851d5.herokuapp.com/list-resources"
    try:
        async with session.post(url, json=resource_data) as response:
            response.raise_for_status()
            print(f"Ressource {resource_data['item_name']} ajoutée.")
    except aiohttp.ClientResponseError as e:
        print(f"Erreur HTTP lors de l'ajout de la ressource {
              resource_data['item_name']} : {e}")
    except Exception as e:
        print(f"Erreur lors de l'ajout de la ressource {
              resource_data['item_name']} : {e}")


def is_resources_empty():
    try:
        response = requests.get(
            "https://dfs-bot-4338ac8851d5.herokuapp.com/list-resources")
        response.raise_for_status()
        resources = response.json()
        return len(resources) == 0
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la vérification des ressources : {e}")
        return False


def get_total_items():
    url = "https://api.dofusdb.fr/items?$limit=50&$skip=50&typeId=82&typeId=1&typeId=9&typeId=10&typeId=11&typeId=16&typeId=17&level[$gt]=199"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie que la requête a réussi

        data = response.json()
        total_items = data['total']  # Récupère le nombre total d'items

        return total_items
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des items : {e}")
        return None


def read_total_items_from_config():
    if not os.path.exists(CONFIG_FILE):
        # Créer le fichier avec une valeur par défaut si le fichier n'existe pas
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"total_items": 299}, f)
        return 299

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config.get("total_items", 299)


def write_total_items_to_config(total_items):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"total_items": total_items}, f)


def move_and_click(x, y):
    if stop_flag:
        return
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()


def capture_price_area(x, y, width, height):
    if stop_flag:
        return None  # Retourner None si stop_flag est True
    try:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    except Exception as e:
        print(f"Erreur lors de la capture de l'écran : {e}")
        return None


def extract_text_from_image(image):
    if image is None:
        return ""
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte : {e}")
        return ""


def clean_price(price_text):
    return price_text.replace(" ", "")


def send_price_to_api(item_id, item_name, price_text, item_number, api_route):
    url = f"https://dfs-bot-4338ac8851d5.herokuapp.com/{api_route}"
    data = {
        "id": item_id,
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


def process_item(item, item_number, api_route):
    if stop_flag:
        return

    item_name = item['name']['fr']
    item_slug = item['slug']['fr']
    item_id = item['id']

    attempt = 0
    max_attempts = 3

    while attempt < max_attempts:
        if stop_flag:
            print("Programme arrêté pendant le traitement des items.")
            return

        try:
            move_and_click(third_x, third_y)
            time.sleep(0.1)

            move_and_click(first_x, first_y)
            time.sleep(0.1)

            pyautogui.typewrite(item_slug, interval=0.01)
            time.sleep(0.5)

            move_and_click(second_x, second_y)
            time.sleep(0.5)

            price_image = capture_price_area(
                price_x, price_y, price_width, price_height)
            time.sleep(0.5)

            price_text = extract_text_from_image(price_image)

            if not price_text.strip():
                raise ValueError("Le texte du prix est vide ou invalide")

            api_queue.put(
                (item_id, item_name, price_text, item_number, api_route))
            time.sleep(0.2)

            move_and_click(third_x, third_y)
            time.sleep(0.1)

            if api_route == 'items-prices':
                asyncio.run(handle_resource_retrieval(item_id))

            break
        except Exception as e:
            print(f"Une erreur s'est produite sur la fonction 'processing item' {
                  item_number} : {e}")
            attempt += 1
            time.sleep(1)


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


async def send_item_to_list(session, url, item):
    # Préparer les données pour la route list-items
    list_item_data = {
        "id": item['id'],
        "item_name": item['name']['fr'],
        "item_slug": item['slug']['fr']
    }
    try:
        async with session.post(url, json=list_item_data) as response:
            response.raise_for_status()
            print(f"Item ajouté à list-items: {item['name']['fr']}")
    except aiohttp.ClientResponseError as http_err:
        print(f"Erreur HTTP lors de l'ajout de l'item {
              item['name']['fr']} : {http_err}")
    except Exception as err:
        print(f"Erreur lors de l'ajout de l'item {item['name']['fr']} : {err}")


async def send_items_to_list_async(items):
    list_items_url = "https://dfs-bot-4338ac8851d5.herokuapp.com/list-items"
    async with aiohttp.ClientSession() as session:
        tasks = [send_item_to_list(session, list_items_url, item)
                 for item in items]
        await asyncio.gather(*tasks)


def send_items_to_list(items):
    # Exécuter la fonction asynchrone
    asyncio.run(send_items_to_list_async(items))


def is_list_items_empty():
    try:
        response = requests.get(
            "https://dfs-bot-4338ac8851d5.herokuapp.com/list-items")
        response.raise_for_status()
        items = response.json()
        return len(items) == 0
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la vérification des items : {e}")
        return False


def api_worker():
    while True:
        try:
            item = api_queue.get(timeout=1)
            if item[0] is None:  # Vérifiez que le signal de fin est bien reçu
                break
            item_id, item_name, price_text, item_number, api_route = item
            send_price_to_api(item_id, item_name, price_text,
                              item_number, api_route)
        except queue.Empty:
            continue
        except Exception as e:
            print(
                f"Une erreur s'est produite lors de l'envoi vers l'API : {e}")


def monitor_stop_key():
    global stop_flag
    keyboard.wait('num 0')
    stop_flag = True


def main():
    global stop_flag

    # Enregistrer le temps de début
    start_time = time.time()

    hdv_choice, hdv_option, api_route = choose_hdv()

    stop_thread = threading.Thread(target=monitor_stop_key)
    stop_thread.start()

    clear_prices_from_api(api_route)  # Clear the API before adding new prices

    if hdv_choice == '1':  # Ajouter un clic supplémentaire pour l'option Ressources
        move_and_click(1380, 231)
        time.sleep(0.2)

    if is_list_items_empty():
        print("La liste d'items est vide. Récupération des items depuis l'API...")
        items = fetch_items_from_api(hdv_option)
        send_items_to_list(items)
    else:
        print("La liste d'items n'est pas vide. Aucun ajout nécessaire.")

    items = fetch_items_from_api(hdv_option)

    # Thread pour envoyer les données à l'API
    api_thread = threading.Thread(target=api_worker)
    api_thread.start()

    # Traiter chaque item avec un compteur
    for index, item in enumerate(items, start=1):
        if stop_flag:
            print("Arrêt du script demandé ...")
            break
        process_item(item, index, api_route)

    # Envoyer le signal de fin au worker API
    # Assurez-vous de correspondre au format attendu
    api_queue.put((None, None, None, None, None))

    # Attendre que le worker API termine avant de quitter
    api_thread.join()
    print("API thread terminé.")

    # Attendre que le thread de surveillance du clavier se termine avant de quitter
    stop_thread.join()
    print("Stop thread terminé.")

    print("Programme terminé !")

    # Enregistrer le temps de fin
    end_time = time.time()

    # Calculer le temps total
    elapsed_time = end_time - start_time

    # Afficher le temps total
    print(f"Temps d'exécution total : {elapsed_time:.2f} secondes")


if __name__ == "__main__":
    main()
