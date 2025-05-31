import logging
import schedule
import time
from datetime import datetime
from typing import Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import (
    DATABASE_URL,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_FILE,
    SCRAPING_INTERVAL,
    SUPERMARKET_CHAINS,
)
from src.database.models import Base, Product, Price, Supermarket
from src.matchers.product_matcher import ProductMatcher
from src.scrapers.rami_levy_scraper import RamiLevyScraper

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SupermarketPriceTracker:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize scrapers
        self.scrapers = {
            "rami_levy": RamiLevyScraper(),
            # Add other scrapers here as they are implemented
        }

    def collect_prices(self):
        """Collect prices from all supermarket chains."""
        logger.info("Starting price collection")
        session = self.Session()

        try:
            for chain_id, scraper in self.scrapers.items():
                logger.info(f"Collecting prices from {chain_id}")
                
                # Get products from scraper
                products = scraper.scrape()
                
                for product_data in products:
                    # Create or update product
                    product = session.query(Product).filter_by(
                        name=product_data["name"]
                    ).first()
                    
                    if not product:
                        product = Product(
                            name=product_data["name"],
                            size=product_data["size"],
                            unit=product_data["unit"]
                        )
                        session.add(product)
                        session.flush()  # Get the product ID
                    
                    # Create or update supermarket
                    supermarket = session.query(Supermarket).filter_by(
                        chain_id=chain_id,
                        branch_id="main"  # For now, we're only tracking main branches
                    ).first()
                    
                    if not supermarket:
                        supermarket = Supermarket(
                            name=SUPERMARKET_CHAINS[chain_id]["name"],
                            chain_id=chain_id,
                            branch_id="main",
                            branch_name="Main Branch"
                        )
                        session.add(supermarket)
                        session.flush()
                    
                    # Create price record
                    price = Price(
                        product_id=product.id,
                        supermarket_id=supermarket.id,
                        price=product_data["price"],
                        collected_at=datetime.fromisoformat(product_data["collected_at"])
                    )
                    session.add(price)
                
                session.commit()
                logger.info(f"Successfully collected prices from {chain_id}")
                
        except Exception as e:
            logger.error(f"Error collecting prices: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def match_products(self):
        """Match products across different chains."""
        logger.info("Starting product matching")
        session = self.Session()
        
        try:
            matcher = ProductMatcher(session)
            matcher.match_all_products()
            logger.info("Successfully matched products")
        except Exception as e:
            logger.error(f"Error matching products: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def run(self):
        """Run the price collection and matching process."""
        logger.info("Starting Supermarket Price Tracker")
        
        # Run initial collection
        self.collect_prices()
        self.match_products()
        
        # Schedule regular collection
        schedule.every(SCRAPING_INTERVAL).seconds.do(self.collect_prices)
        schedule.every(SCRAPING_INTERVAL).seconds.do(self.match_products)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    tracker = SupermarketPriceTracker()
    tracker.run() 