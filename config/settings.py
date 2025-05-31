import os
from pathlib import Path
from typing import Dict, List

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SHOPPING_LISTS_DIR = DATA_DIR / "shopping_lists"
RAW_DATA_DIR = DATA_DIR / "raw"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/supermarket_prices.db")

# Scraping settings
SCRAPING_INTERVAL = int(os.getenv("SCRAPING_INTERVAL", "86400"))  # Default: daily
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# Supported supermarket chains
SUPERMARKET_CHAINS = {
    "rami_levy": {
        "name": "Rami Levy",
        "base_url": "https://www.rami-levy.co.il",
        "price_list_url": "https://www.gov.il/he/pages/cpfta_prices_regulations",
    },
    "shufersal": {
        "name": "Shufersal",
        "base_url": "https://www.shufersal.co.il",
        "price_list_url": "https://www.gov.il/he/pages/cpfta_prices_regulations",
    },
    "yochananof": {
        "name": "Yochananof",
        "base_url": "https://www.yochananof.co.il",
        "price_list_url": "https://www.gov.il/he/pages/cpfta_prices_regulations",
    },
    "tiv_taam": {
        "name": "Tiv Taam",
        "base_url": "https://www.tivtaam.co.il",
        "price_list_url": "https://www.gov.il/he/pages/cpfta_prices_regulations",
    },
    "victory": {
        "name": "Victory",
        "base_url": "https://www.victory.co.il",
        "price_list_url": "https://www.gov.il/he/pages/cpfta_prices_regulations",
    },
}

# Product matching settings
MATCHING_THRESHOLD = 0.8  # Minimum similarity score for product matching
UNIT_CONVERSION = {
    "ml": {"l": 0.001},
    "g": {"kg": 0.001},
    "kg": {"g": 1000},
    "l": {"ml": 1000},
}

# Dashboard settings
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "localhost")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8050"))
DASHBOARD_DEBUG = os.getenv("DASHBOARD_DEBUG", "False").lower() == "true"

# API settings
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs" / "supermarket_prices.log"

# Create necessary directories
for directory in [DATA_DIR, SHOPPING_LISTS_DIR, RAW_DATA_DIR, BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True) 