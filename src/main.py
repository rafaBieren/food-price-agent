"""
Main application module for the supermarket price tracking system.

This module orchestrates the price collection process, including:
- Scraping prices from different supermarkets
- Matching similar products
- Storing data in the database
- Running on a scheduled basis
"""

import logging
import time
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Optional

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from config.settings import SCRAPING_INTERVAL, SUPERMARKET_CHAINS
from src.database.models import Product, Price, Supermarket, get_session
from src.scrapers.rami_levy_scraper import RamiLevyScraper
from src.scrapers.shufersal_scraper import ShufersalScraper
from src.scrapers.yochananof_scraper import YochananofScraper
from src.scrapers.tiv_taam_scraper import TivTaamScraper
from src.scrapers.victory_scraper import VictoryScraper
from src.matchers.product_matcher import ProductMatcher

# Configure logging
logger = logging.getLogger(__name__)

class SupermarketPriceTracker:
    """
    Main class for tracking supermarket prices.
    
    This class manages the entire price tracking process, including:
    - Initializing scrapers for each supermarket chain
    - Collecting prices from all supermarkets
    - Matching similar products
    - Storing data in the database
    
    Attributes:
        scrapers (Dict): Dictionary of scrapers for each supermarket chain
        session: Database session
        matcher: Product matcher instance
    """

    def __init__(self):
        """Initialize the price tracker with scrapers and database connection."""
        self.scrapers = {
            'rami_levy': RamiLevyScraper(),
            'shufersal': ShufersalScraper(),
            'yochananof': YochananofScraper(),
            'tiv_taam': TivTaamScraper(),
            'victory': VictoryScraper()
        }
        self.session = get_session()
        self.matcher = ProductMatcher(self.session)

    def collect_prices(self) -> List[Dict]:
        """
        Collect prices from all supermarkets.
        
        Returns:
            List[Dict]: List of collected price data
        """
        all_prices = []
        
        for chain_id, scraper in self.scrapers.items():
            try:
                logger.info(f"Collecting prices from {chain_id}")
                prices = scraper.scrape()
                all_prices.extend(prices)
                logger.info(f"Successfully collected {len(prices)} prices from {chain_id}")
            except Exception as e:
                logger.error(f"Error collecting prices from {chain_id}: {str(e)}")
        
        return all_prices

    def save_prices(self, prices: List[Dict]):
        """
        Save collected prices to the database.
        
        Args:
            prices: List of price data dictionaries
        """
        for price_data in prices:
            try:
                # Get or create product
                product = self.session.query(Product).filter_by(
                    name=price_data['name'],
                    size=price_data['size'],
                    unit=price_data['unit']
                ).first()
                
                if not product:
                    product = Product(
                        name=price_data['name'],
                        size=price_data['size'],
                        unit=price_data['unit']
                    )
                    self.session.add(product)
                
                # Get or create supermarket
                supermarket = self.session.query(Supermarket).filter_by(
                    chain_id=price_data['chain_id'],
                    branch_id=price_data['branch_id']
                ).first()
                
                if not supermarket:
                    supermarket = Supermarket(
                        name=price_data['chain_name'],
                        chain_id=price_data['chain_id'],
                        branch_id=price_data['branch_id'],
                        branch_name=price_data['branch_name'],
                        address=price_data['address']
                    )
                    self.session.add(supermarket)
                
                # Create price record
                price = Price(
                    product=product,
                    supermarket=supermarket,
                    price=price_data['price'],
                    original_price=price_data.get('original_price'),
                    discount_price=price_data.get('discount_price')
                )
                self.session.add(price)
                
            except Exception as e:
                logger.error(f"Error saving price data: {str(e)}")
                continue
        
        self.session.commit()

    def match_products(self):
        """Match similar products across different supermarkets."""
        try:
            logger.info("Starting product matching")
            matches = self.matcher.match_all_products()
            logger.info(f"Successfully created {len(matches)} product matches")
        except Exception as e:
            logger.error(f"Error matching products: {str(e)}")

    def run(self):
        """
        Run the price tracking process.
        
        This method runs in an infinite loop, collecting prices and matching
        products at regular intervals defined in the settings.
        """
        logger.info("Starting price tracking service")
        
        while True:
            try:
                # Collect prices
                prices = self.collect_prices()
                
                # Save prices to database
                self.save_prices(prices)
                
                # Match products
                self.match_products()
                
                # Wait for next interval
                logger.info(f"Waiting {SCRAPING_INTERVAL} seconds until next collection")
                time.sleep(SCRAPING_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    """Main entry point for the application."""
    try:
        tracker = SupermarketPriceTracker()
        tracker.run()
    except KeyboardInterrupt:
        logger.info("Price tracking service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == '__main__':
    main() 