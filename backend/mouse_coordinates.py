from pynput import mouse
import time


def on_move(x, y):
    # Capture la position de la souris une seule fois
    print(f"Coordonnées capturées - X: {x}, Y: {y}")
    # Stoppe l'écouteur après avoir capturé les coordonnées
    return False


def main():
    print("Vous avez 5 secondes pour positionner la souris...")
    # Attendre 5 secondes avant de commencer à capturer les coordonnées
    time.sleep(5)

    # Crée un écouteur de souris
    with mouse.Listener(on_move=on_move) as listener:
        print("Déplacez la souris pour capturer les coordonnées.")
        listener.join()  # Attendre que l'écouteur se termine (quand il retourne False)


if __name__ == "__main__":
    main()
