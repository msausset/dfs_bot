import threading
import keyboard
import requests
import time
import queue
from api_utils import fetch_items_from_api, is_resources_empty, clear_prices_from_api
from item_processing import process_item, choose_hdv
from image_utils import move_and_click
from constants import API_QUEUE, STOP_FLAG


def monitor_stop_key():
    global STOP_FLAG
    keyboard.wait('num 0')
    STOP_FLAG = True


def api_worker():
    while True:
        try:
            item = API_QUEUE.get(timeout=1)
            if item[0] is None:
                break
            item_id, item_name, price_text, item_number, api_route = item
            send_price_to_api(item_id, item_name, price_text,
                              item_number, api_route)
        except queue.Empty:
            continue
        except Exception as e:
            print(
                f"Une erreur s'est produite lors de l'envoi vers l'API : {e}")


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


def main():
    global STOP_FLAG

    hdv_choice, hdv_option, api_route = choose_hdv()

    stop_thread = threading.Thread(target=monitor_stop_key)
    stop_thread.start()

    clear_prices_from_api(api_route)

    if hdv_choice == '1':
        move_and_click(1380, 231)
        time.sleep(0.2)

    items = fetch_items_from_api(hdv_option)

    api_thread = threading.Thread(target=api_worker)
    api_thread.start()

    for index, item in enumerate(items, start=1):
        if STOP_FLAG:
            print("Arrêt du script demandé ...")
            break
        process_item(item, index, api_route)

    API_QUEUE.put((None, None, None, None, None))

    api_thread.join()
    print("API thread terminé.")

    stop_thread.join()
    print("Stop thread terminé.")

    print("Programme terminé !")


if __name__ == "__main__":
    main()
