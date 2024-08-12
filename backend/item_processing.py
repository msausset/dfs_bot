# item_processing.py

import time
import pyautogui
import requests
from api_utils import fetch_recipes_from_api, resource_exists, check_resources_prices_empty, check_list_resources_empty
from image_utils import move_and_click, capture_price_area, extract_text_from_image
from constants import THIRD_X, THIRD_Y, FIRST_X, FIRST_Y, SECOND_X, SECOND_Y, PRICE_X, PRICE_Y, PRICE_WIDTH, PRICE_HEIGHT, HDV_OPTIONS, API_ROUTES, STOP_FLAG, API_QUEUE


def choose_hdv():
    print("Choisissez l'Hôtel de Vente (HDV) :")
    print("1. Ressources")
    print("2. Consommables")
    print("3. Équipements")
    choice = input("Entrez le numéro correspondant à votre choix: ")
    return choice, HDV_OPTIONS.get(choice, None), API_ROUTES.get(choice, 'items')


def process_item(item, item_number, api_route):
    if STOP_FLAG:
        return

    item_name = item['name']['fr']
    item_slug = item['slug']['fr']
    item_id = item['id']

    attempt = 0
    max_attempts = 3

    while attempt < max_attempts:
        if STOP_FLAG:
            print("Programme arrêté pendant le traitement des items.")
            return

        try:
            move_and_click(THIRD_X, THIRD_Y)
            time.sleep(0.1)
            move_and_click(FIRST_X, FIRST_Y)
            time.sleep(0.1)
            pyautogui.typewrite(item_slug, interval=0.01)
            time.sleep(0.5)
            move_and_click(SECOND_X, SECOND_Y)
            time.sleep(0.5)

            price_image = capture_price_area(
                PRICE_X, PRICE_Y, PRICE_WIDTH, PRICE_HEIGHT)
            time.sleep(0.5)

            price_text = extract_text_from_image(price_image)

            if not price_text.strip():
                raise ValueError("Le texte du prix est vide ou invalide")

            API_QUEUE.put(
                (item_id, item_name, price_text, item_number, api_route))
            time.sleep(0.2)

            move_and_click(THIRD_X, THIRD_Y)
            time.sleep(0.1)

            if api_route == 'items':
                ingredients = fetch_recipes_from_api(item_id)

                # Vérifiez si list-resources est vide
                if check_list_resources_empty():
                    print("List-resources est vide. Ajout des ingrédients...")

                    for ingredient in ingredients:
                        ingredient_id = ingredient['id']
                        ingredient_name = ingredient['name']['fr']
                        ingredient_slug = ingredient['slug']['fr']

                        # Vérifiez si la ressource existe déjà dans list-resources
                        if not resource_exists(ingredient_id, "list-resources"):
                            # Ajoutez les ingrédients à list-resources
                            resource_data = {
                                "id": ingredient_id,
                                "item_name": ingredient_name,
                                "item_slug": ingredient_slug
                            }
                            try:
                                response = requests.post(
                                    "https://dfs-bot-4338ac8851d5.herokuapp.com/list-resources", json=resource_data)
                                response.raise_for_status()
                                print(
                                    f"Ingrédient ajouté à list-resources: {ingredient_name}")
                            except requests.exceptions.HTTPError as http_err:
                                print(f"Erreur HTTP lors de l'ajout de l'ingrédient {
                                      ingredient_name} : {http_err}")
                            except Exception as err:
                                print(f"Erreur lors de l'ajout de l'ingrédient {
                                      ingredient_name} : {err}")

                        # Vérifiez si resources-prices est vide et ajoutez les prix si nécessaire
                        if check_resources_prices_empty():
                            print(
                                f"Resources-prices est vide. Initialisation des prix pour l'ingrédient ID {ingredient_id}...")

                            price_data = {
                                "id": ingredient_id,
                                "price_1": "",
                                "price_10": "",
                                "price_100": ""
                            }
                            try:
                                response = requests.post(
                                    "https://dfs-bot-4338ac8851d5.herokuapp.com/resources-prices", json=price_data)
                                response.raise_for_status()
                                print(f"Prix initialisé pour l'ingrédient {
                                      ingredient_name} dans resources-prices")
                            except requests.exceptions.HTTPError as http_err:
                                print(f"Erreur HTTP lors de l'initialisation des prix de l'ingrédient {
                                      ingredient_name} : {http_err}")
                            except Exception as err:
                                print(f"Erreur lors de l'initialisation des prix de l'ingrédient {
                                      ingredient_name} : {err}")

            break
        except Exception as e:
            print(f"Une erreur s'est produite sur la fonction 'processing item' {
                  item_number} : {e}")
            attempt += 1
            time.sleep(1)
