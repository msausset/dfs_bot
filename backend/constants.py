import queue
from threading import Event

# Variable globale pour contrôler l'exécution
STOP_FLAG = False

STOP_EVENT = Event()

# Queue pour stocker les données à envoyer à l'API
API_QUEUE = queue.Queue()

# Coordonnées globales
PRICE_X, PRICE_Y = 1208, 328
PRICE_WIDTH, PRICE_HEIGHT = 160, 38

FIRST_X, FIRST_Y = 555, 256
SECOND_X, SECOND_Y = 956, 288
THIRD_X, THIRD_Y = 726, 255

# HDV Options
HDV_OPTIONS = {
    # Ressources
    '1': 'typeId=167&typeId=104&typeId=40&typeId=38&typeId=108&typeId=107&typeId=34&typeId=119&typeId=111&typeId=56&typeId=35&typeId=152&typeId=60&typeId=57&typeId=228&typeId=71&typeId=39&typeId=106&typeId=47&typeId=103&typeId=59&typeId=105&typeId=109&typeId=51&typeId=50&typeId=36&typeId=53&typeId=54&typeId=41&typeId=48&typeId=65&typeId=98&typeId=229&typeId=219&typeId=15&typeId=183&typeId=164&level[$gt]=159',
    '2': 'id=16944&id=11504&id=11507',  # Consommables
    # Équipements
    '3': '&typeId=82&typeId=1&typeId=9&typeId=10&typeId=11&typeId=16&typeId=17&level[$gt]=199',
}

# API Routes
API_ROUTES = {
    '1': 'resources-prices',
    '2': 'resources-prices',
    '3': 'items-prices',
}
