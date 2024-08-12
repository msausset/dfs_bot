import pyautogui
import pytesseract
from constants import STOP_FLAG

# Configurez le chemin vers le binaire Tesseract-OCR si nécessaire
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def move_and_click(x, y):
    if STOP_FLAG:
        return
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()


def capture_price_area(x, y, width, height):
    if STOP_FLAG:
        return None
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
