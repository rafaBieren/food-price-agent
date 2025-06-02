"""
Product matching module for the supermarket price tracking system.

This module provides functionality for matching similar products across different supermarkets.
It uses string similarity and unit conversion to identify equivalent products.
"""

import logging
from typing import Dict, List, Optional, Tuple

from Levenshtein import ratio
from sqlalchemy.orm import Session

from config.settings import PRODUCT_MATCHING
from src.database.models import Product, ProductMatch

logger = logging.getLogger(__name__)

class ProductMatcher:
    """
    Handles matching of similar products across different supermarkets.
    
    This class provides methods for:
    - Calculating similarity between product names
    - Finding matches for products
    - Normalizing prices to comparable units
    - Creating and managing product matches in the database
    
    Attributes:
        similarity_threshold (float): Minimum similarity score for considering products as matches
        max_matches (int): Maximum number of matches to find for each product
        unit_conversion (Dict): Dictionary of unit conversion factors
    """

    def __init__(self, session: Session):
        """
        Initialize the product matcher.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.similarity_threshold = PRODUCT_MATCHING['similarity_threshold']
        self.max_matches = PRODUCT_MATCHING['max_matches']
        self.unit_conversion = PRODUCT_MATCHING['unit_conversion']

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity score between two product names.
        
        Uses Levenshtein distance to calculate string similarity.
        
        Args:
            name1: First product name
            name2: Second product name
            
        Returns:
            float: Similarity score between 0 and 1
        """
        return ratio(name1.lower(), name2.lower())

    def find_matches(self, product: Product) -> List[Tuple[Product, float]]:
        """
        Find matching products for a given product.
        
        Args:
            product: Product to find matches for
            
        Returns:
            List[Tuple[Product, float]]: List of (product, similarity_score) tuples
        """
        all_products = self.session.query(Product).filter(Product.id != product.id).all()
        matches = []
        
        for other_product in all_products:
            similarity = self.calculate_similarity(product.name, other_product.name)
            if similarity >= self.similarity_threshold:
                matches.append((other_product, similarity))
        
        # Sort by similarity score and limit to max_matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:self.max_matches]

    def normalize_price(self, price: float, from_unit: str, to_unit: str) -> Optional[float]:
        """
        Convert price from one unit to another.
        
        Args:
            price: Original price
            from_unit: Original unit
            to_unit: Target unit
            
        Returns:
            Optional[float]: Converted price if conversion is possible, None otherwise
        """
        if from_unit == to_unit:
            return price
            
        try:
            conversion = self.unit_conversion[from_unit][to_unit]
            return price * conversion
        except KeyError:
            logger.warning(f"Cannot convert from {from_unit} to {to_unit}")
            return None

    def create_match(self, source_product: Product, target_product: Product, similarity_score: float) -> ProductMatch:
        """
        Create a new product match in the database.
        
        Args:
            source_product: Source product
            target_product: Target product
            similarity_score: Similarity score between the products
            
        Returns:
            ProductMatch: Created product match
        """
        match = ProductMatch(
            source_product_id=source_product.id,
            target_product_id=target_product.id,
            similarity_score=similarity_score
        )
        self.session.add(match)
        return match

    def match_all_products(self) -> List[ProductMatch]:
        """
        Find and create matches for all products in the database.
        
        Returns:
            List[ProductMatch]: List of created product matches
        """
        products = self.session.query(Product).all()
        matches = []
        
        for product in products:
            product_matches = self.find_matches(product)
            for matched_product, similarity in product_matches:
                match = self.create_match(product, matched_product, similarity)
                matches.append(match)
        
        self.session.commit()
        return matches

    def get_matches_for_product(self, product_id: int) -> List[ProductMatch]:
        """
        Get all matches for a specific product.
        
        Args:
            product_id: ID of the product to find matches for
            
        Returns:
            List[ProductMatch]: List of product matches
        """
        return self.session.query(ProductMatch).filter(
            (ProductMatch.source_product_id == product_id) |
            (ProductMatch.target_product_id == product_id)
        ).all() 