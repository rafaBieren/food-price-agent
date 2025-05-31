import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import MAX_RETRIES, REQUEST_TIMEOUT, RETRY_DELAY

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, chain_id: str, base_url: str):
        self.chain_id = chain_id
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_DELAY,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make an HTTP request with error handling."""
        try:
            response = self.session.request(
                method,
                url,
                timeout=REQUEST_TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None

    def _parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """Parse HTML content into BeautifulSoup object."""
        try:
            return BeautifulSoup(html_content, "lxml")
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return None

    @abstractmethod
    def get_price_list_url(self) -> str:
        """Get the URL for the price list."""
        pass

    @abstractmethod
    def parse_price_list(self, html_content: str) -> List[Dict]:
        """Parse the price list HTML content into a list of products with prices."""
        pass

    @abstractmethod
    def normalize_product_name(self, name: str) -> str:
        """Normalize product name for consistent matching."""
        pass

    @abstractmethod
    def extract_product_size(self, name: str) -> tuple[float, str]:
        """Extract size and unit from product name."""
        pass

    def scrape(self) -> List[Dict]:
        """Main scraping method that orchestrates the scraping process."""
        logger.info(f"Starting to scrape {self.chain_id}")
        
        url = self.get_price_list_url()
        response = self._make_request(url)
        
        if not response:
            logger.error(f"Failed to fetch price list from {url}")
            return []

        products = self.parse_price_list(response.text)
        logger.info(f"Successfully scraped {len(products)} products from {self.chain_id}")
        
        return products

    def __repr__(self):
        return f"<{self.__class__.__name__}(chain_id='{self.chain_id}')>" 