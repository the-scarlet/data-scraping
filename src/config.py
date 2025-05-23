import os

LOG_LEVEL = "INFO"
HOME_PATH = os.environ.get("HOME") or os.environ.get(
    "USERPROFILE"
)  # Linux/macOS or Windows
ARTEFACTS_DIRECTORY = "data_scraping_artefacts"
GOOGLE_COOKIES_FILE = os.path.join(HOME_PATH, ARTEFACTS_DIRECTORY, "cookies.json")
# google alerts default values
DEFAULT_ENTRY = "DEFAULT"
FREQUENCY = "Quand le cas se présente"
SOURCE = "Automatique"
LANGUAGE = "Toutes les langues"
REGION = "Toutes les régions"
VOLUME = "Tous les résultats"
DELIVERY = DEFAULT_ENTRY
