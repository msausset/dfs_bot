# item_processing.py

import time
import pyautogui
import requests
from api_utils import fetch_recipes_from_api, resource_exists
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
                for ingredient in ingredients:
                    ingredient_id = ingredient['id']
                    if not resource_exists(ingredient_id):
                        resource_data = {
                            "id": ingredient_id,
                            "item_name": ingredient['name']['fr'],
                            "item_slug": ingredient['slug']['fr'],
                            "price_1": "",
                            "price_10": "",
                            "price_100": ""
                        }
                        requests.post(
                            "https://dfs-bot-4338ac8851d5.herokuapp.com/resources", json=resource_data)

            break
        except Exception as e:
            print(f"Une erreur s'est produite sur la fonction 'processing item' {
                  item_number} : {e}")
            attempt += 1
            time.sleep(1)
