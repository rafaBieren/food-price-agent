"""
Configuration settings for the supermarket price tracking system.

This module contains all the configuration settings used throughout the application.
Settings are loaded from environment variables with fallback to default values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SHOPPING_LISTS_DIR = DATA_DIR / "shopping_lists"
RAW_DATA_DIR = DATA_DIR / "raw"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/supermarket_prices.db")

# Scraping settings
SCRAPING_INTERVAL = int(os.getenv("SCRAPING_INTERVAL", "3600"))  # Default: 1 hour
REQUEST_TIMEOUT = 30
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

# Supported supermarket chains
SUPERMARKET_CHAINS = {
    "rami_levy": {
        "name": "רמי לוי",
        "base_url": "https://www.rami-levy.co.il",
        "price_list_url": "https://www.rami-levy.co.il/files/price_list.pdf",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    },
    "shufersal": {
        "name": "שופרסל",
        "base_url": "https://www.shufersal.co.il",
        "price_list_url": "https://www.shufersal.co.il/online/he/A/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    },
    "yochananof": {
        "name": "יוחננוף",
        "base_url": "https://www.yochananof.co.il",
        "price_list_url": "https://www.yochananof.co.il/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    },
    "tiv_taam": {
        "name": "טיב טעם",
        "base_url": "https://www.tivtaam.co.il",
        "price_list_url": "https://www.tivtaam.co.il/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    },
    "victory": {
        "name": "ויקטורי",
        "base_url": "https://www.victory.co.il",
        "price_list_url": "https://www.victory.co.il/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    },
}

# Product matching settings
MATCHING_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))
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
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "supermarket_prices.log"))

# Create necessary directories
for directory in [DATA_DIR, SHOPPING_LISTS_DIR, RAW_DATA_DIR, BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True) 