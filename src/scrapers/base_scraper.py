"""
Base scraper class for supermarket price tracking.

This module provides the base class that all supermarket scrapers must inherit from.
It implements common functionality for web scraping and price data collection.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for all supermarket scrapers.
    
    This class provides common functionality for web scraping and price data collection.
    Each supermarket chain should implement its own scraper class that inherits from this base class.
    
    Attributes:
        chain_id (str): Unique identifier for the supermarket chain
        chain_name (str): Display name of the supermarket chain
        base_url (str): Base URL of the supermarket's website
        price_list_url (str): URL of the price list page
        headers (Dict[str, str]): HTTP headers to use for requests
    """

    def __init__(self, chain_id: str, chain_name: str, base_url: str, price_list_url: str, headers: Dict[str, str]):
        """
        Initialize the scraper with chain-specific information.
        
        Args:
            chain_id: Unique identifier for the supermarket chain
            chain_name: Display name of the supermarket chain
            base_url: Base URL of the supermarket's website
            price_list_url: URL of the price list page
            headers: HTTP headers to use for requests
        """
        self.chain_id = chain_id
        self.chain_name = chain_name
        self.base_url = base_url
        self.price_list_url = price_list_url
        self.headers = headers
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_DELAY,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_price_list_url(self) -> str:
        """
        Get the URL of the price list page.
        
        Returns:
            str: URL of the price list page
        """
        return self.price_list_url

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page with retry logic and error handling.
        
        Args:
            url: URL of the page to fetch
            
        Returns:
            Optional[str]: HTML content of the page if successful, None otherwise
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None

    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content into a BeautifulSoup object.
        
        Args:
            html: HTML content to parse
            
        Returns:
            Optional[BeautifulSoup]: Parsed HTML if successful, None otherwise
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            return None

    @abstractmethod
    def parse_price_list(self, html: str) -> List[Dict]:
        """
        Parse the price list page and extract product information.
        
        This method must be implemented by each supermarket-specific scraper.
        
        Args:
            html: HTML content of the price list page
            
        Returns:
            List[Dict]: List of dictionaries containing product information
        """
        pass

    @abstractmethod
    def normalize_product_name(self, name: str) -> str:
        """
        Normalize a product name for consistent matching.
        
        This method must be implemented by each supermarket-specific scraper.
        
        Args:
            name: Original product name
            
        Returns:
            str: Normalized product name
        """
        pass

    @abstractmethod
    def extract_product_size(self, name: str) -> Tuple[float, str]:
        """
        Extract size and unit information from a product name.
        
        This method must be implemented by each supermarket-specific scraper.
        
        Args:
            name: Product name containing size information
            
        Returns:
            Tuple[float, str]: Size value and unit
        """
        pass

    def scrape(self) -> List[Dict]:
        """
        Main method to scrape price data from the supermarket.
        
        Returns:
            List[Dict]: List of dictionaries containing product information
        """
        url = self.get_price_list_url()
        html = self.fetch_page(url)
        if not html:
            return []
        
        return self.parse_price_list(html)

    def __repr__(self):
        return f"<{self.__class__.__name__}(chain_id='{self.chain_id}')>" 