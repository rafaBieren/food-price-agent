import re
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup

from config.settings import SUPERMARKET_CHAINS
from src.scrapers.base_scraper import BaseScraper

class RamiLevyScraper(BaseScraper):
    def __init__(self):
        chain_info = SUPERMARKET_CHAINS["rami_levy"]
        super().__init__("rami_levy", chain_info["base_url"])

    def get_price_list_url(self) -> str:
        """Get the URL for Rami Levy's price list."""
        return SUPERMARKET_CHAINS["rami_levy"]["price_list_url"]

    def normalize_product_name(self, name: str) -> str:
        """Normalize product name for consistent matching."""
        # Remove common prefixes/suffixes
        name = re.sub(r'^רמי לוי\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*רמי לוי$', '', name, flags=re.IGNORECASE)
        
        # Remove size information
        name = re.sub(r'\d+(?:\.\d+)?\s*(?:ק"ג|ליטר|גרם|מ"ל|יחידה)', '', name)
        
        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()

    def extract_product_size(self, name: str) -> Tuple[float, str]:
        """Extract size and unit from product name."""
        # Common size patterns in Hebrew
        size_patterns = {
            r'(\d+(?:\.\d+)?)\s*ק"ג': ('kg', 1.0),
            r'(\d+(?:\.\d+)?)\s*גרם': ('g', 0.001),
            r'(\d+(?:\.\d+)?)\s*ליטר': ('l', 1.0),
            r'(\d+(?:\.\d+)?)\s*מ"ל': ('ml', 0.001),
            r'(\d+(?:\.\d+)?)\s*יחידה': ('unit', 1.0),
        }

        for pattern, (unit, multiplier) in size_patterns.items():
            match = re.search(pattern, name)
            if match:
                size = float(match.group(1)) * multiplier
                return size, unit

        return 1.0, 'unit'  # Default to 1 unit if no size found

    def parse_price_list(self, html_content: str) -> List[Dict]:
        """Parse the price list HTML content into a list of products with prices."""
        soup = self._parse_html(html_content)
        if not soup:
            return []

        products = []
        # Note: This is a placeholder implementation. The actual parsing logic
        # will need to be adapted based on the actual HTML structure of the price list
        try:
            # Example parsing logic (needs to be updated based on actual HTML structure)
            product_rows = soup.find_all('tr', class_='product-row')
            
            for row in product_rows:
                try:
                    name_cell = row.find('td', class_='product-name')
                    price_cell = row.find('td', class_='product-price')
                    
                    if name_cell and price_cell:
                        name = name_cell.text.strip()
                        price = float(price_cell.text.strip().replace('₪', '').replace(',', ''))
                        
                        normalized_name = self.normalize_product_name(name)
                        size, unit = self.extract_product_size(name)
                        
                        products.append({
                            'name': name,
                            'normalized_name': normalized_name,
                            'price': price,
                            'size': size,
                            'unit': unit,
                            'chain_id': self.chain_id,
                            'collected_at': datetime.utcnow().isoformat()
                        })
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error parsing product row: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing price list: {str(e)}")
            
        return products 