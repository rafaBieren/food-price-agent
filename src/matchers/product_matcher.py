import logging
from typing import Dict, List, Optional, Tuple

from Levenshtein import ratio
from sqlalchemy.orm import Session

from config.settings import MATCHING_THRESHOLD, UNIT_CONVERSION
from src.database.models import Product, ProductMatch

logger = logging.getLogger(__name__)

class ProductMatcher:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.matching_threshold = MATCHING_THRESHOLD

    def normalize_price(self, price: float, from_unit: str, to_unit: str) -> float:
        """Convert price to a common unit for comparison."""
        if from_unit == to_unit:
            return price

        if from_unit in UNIT_CONVERSION and to_unit in UNIT_CONVERSION[from_unit]:
            return price * UNIT_CONVERSION[from_unit][to_unit]
        
        return price  # Return original price if conversion not possible

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two product names."""
        return ratio(name1.lower(), name2.lower())

    def find_matches(self, product: Product) -> List[Tuple[Product, float]]:
        """Find matching products for a given product."""
        matches = []
        
        # Get all other products
        other_products = self.db_session.query(Product).filter(
            Product.id != product.id
        ).all()

        for other_product in other_products:
            similarity = self.calculate_similarity(
                product.name,
                other_product.name
            )

            if similarity >= self.matching_threshold:
                matches.append((other_product, similarity))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def create_match(self, source_product: Product, target_product: Product, similarity: float):
        """Create a product match record in the database."""
        match = ProductMatch(
            source_product_id=source_product.id,
            target_product_id=target_product.id,
            similarity_score=similarity
        )
        self.db_session.add(match)
        self.db_session.commit()

    def get_best_match(self, product: Product) -> Optional[Tuple[Product, float]]:
        """Get the best matching product for a given product."""
        matches = self.find_matches(product)
        return matches[0] if matches else None

    def match_all_products(self):
        """Match all products in the database."""
        products = self.db_session.query(Product).all()
        
        for product in products:
            matches = self.find_matches(product)
            
            for match_product, similarity in matches:
                # Check if match already exists
                existing_match = self.db_session.query(ProductMatch).filter(
                    ProductMatch.source_product_id == product.id,
                    ProductMatch.target_product_id == match_product.id
                ).first()

                if not existing_match:
                    self.create_match(product, match_product, similarity)
                    logger.info(
                        f"Created match between {product.name} and {match_product.name} "
                        f"with similarity {similarity:.2f}"
                    )

    def get_comparable_price(self, product1: Product, product2: Product) -> Tuple[float, float]:
        """Get comparable prices for two products by converting to common units."""
        # Convert both prices to the same unit (preferably the smaller unit)
        if product1.unit in UNIT_CONVERSION and product2.unit in UNIT_CONVERSION:
            # Convert to the smaller unit for more precise comparison
            if product1.unit in UNIT_CONVERSION[product2.unit]:
                price1 = self.normalize_price(1.0, product1.unit, product2.unit)
                price2 = 1.0
                unit = product2.unit
            else:
                price1 = 1.0
                price2 = self.normalize_price(1.0, product2.unit, product1.unit)
                unit = product1.unit
        else:
            # If units are not convertible, return original prices
            price1 = 1.0
            price2 = 1.0
            unit = "unit"

        return price1, price2 