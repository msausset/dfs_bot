import requests
import pyautogui
import time
from PIL import Image
import pytesseract
import keyboard
import threading
import queue

# Configurez le chemin vers le binaire Tesseract-OCR si nécessaire
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
    '1': 'resources',
    '2': 'consumables',
    '3': 'items',
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

    # Ajouter les requêtes supplémentaires si HDV Ressources est choisi
    if hdv_option == HDV_OPTIONS['1']:
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
    url = f"http://localhost:5000/{api_route}"
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
            time.sleep(0.1)  # Augmenter légèrement le temps de pause

            move_and_click(first_x, first_y)
            time.sleep(0.1)  # Augmenter légèrement le temps de pause

            pyautogui.typewrite(item_slug, interval=0.01)
            time.sleep(0.5)  # Augmenter légèrement le temps de pause

            move_and_click(second_x, second_y)
            time.sleep(0.5)  # Augmenter légèrement le temps de pause

            price_image = capture_price_area(
                price_x, price_y, price_width, price_height)
            time.sleep(0.5)  # Augmenter légèrement le temps de pause

            price_text = extract_text_from_image(price_image)

            if not price_text.strip():
                raise ValueError("Le texte du prix est vide ou invalide")

            # Ajoutez les données à la queue avec le numéro d'item et la route API
            api_queue.put(
                (item_id, item_name, price_text, item_number, api_route))
            time.sleep(0.2)  # Augmenter légèrement le temps de pause

            move_and_click(third_x, third_y)
            time.sleep(0.1)  # Augmenter légèrement le temps de pause

            break  # Sortir de la boucle en cas de succès
        except Exception as e:
            print(f"Une erreur s'est produite sur la fonction 'processing item' {
                  item_number} : {e}")
            attempt += 1
            time.sleep(1)  # Attendre avant de réessayer


def clear_prices_from_api(api_route):
    url = f"http://localhost:5000/{api_route}/clear"
    try:
        response = requests.post(url)
        response.raise_for_status()
        print(f"API {api_route} vidée")
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP : {http_err}")
    except Exception as err:
        print(f"Erreur : {err}")


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

    hdv_choice, hdv_option, api_route = choose_hdv()

    stop_thread = threading.Thread(target=monitor_stop_key)
    stop_thread.start()

    clear_prices_from_api(api_route)  # Clear the API before adding new prices

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


if __name__ == "__main__":
    main()
