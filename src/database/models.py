"""
Database models for the supermarket price tracking system.

This module defines the SQLAlchemy models used to store and manage data in the system.
The models represent products, supermarkets, prices, and product matches.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config.settings import DATABASE_URL

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy base class
Base = declarative_base()

class Product(Base):
    """
    Represents a product in the system.
    
    Attributes:
        id (int): Unique identifier for the product
        name (str): Name of the product
        size (float): Size/quantity of the product
        unit (str): Unit of measurement (e.g., kg, g, l, ml)
        created_at (datetime): When the product was first added
        updated_at (datetime): When the product was last updated
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    size = Column(Float)
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prices = relationship("Price", back_populates="product")
    source_matches = relationship("ProductMatch", foreign_keys="ProductMatch.source_product_id", back_populates="source_product")
    target_matches = relationship("ProductMatch", foreign_keys="ProductMatch.target_product_id", back_populates="target_product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', size={self.size} {self.unit})>"


class Supermarket(Base):
    """
    Represents a supermarket branch in the system.
    
    Attributes:
        id (int): Unique identifier for the supermarket
        name (str): Name of the supermarket chain
        chain_id (str): Identifier for the supermarket chain
        branch_id (str): Identifier for the specific branch
        branch_name (str): Name of the branch
        address (str): Physical address of the branch
    """
    __tablename__ = "supermarkets"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    chain_id = Column(String(50), nullable=False)  # e.g., "rami_levy"
    branch_id = Column(String(50))
    branch_name = Column(String(255))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prices = relationship("Price", back_populates="supermarket")

    def __repr__(self):
        return f"<Supermarket(id={self.id}, name='{self.name}', branch='{self.branch_name}')>"


class Price(Base):
    """
    Represents a price record for a product at a specific supermarket.
    
    Attributes:
        id (int): Unique identifier for the price record
        product_id (int): Foreign key to the Product table
        supermarket_id (int): Foreign key to the Supermarket table
        price (float): Current price of the product
        original_price (float): Original price before any discounts
        discount_price (float): Discounted price if applicable
        collected_at (datetime): When the price was collected
    """
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # Price before any discounts
    discount_price = Column(Float)  # Price during promotions
    discount_description = Column(String)
    collected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="prices")
    supermarket = relationship("Supermarket", back_populates="prices")

    def __repr__(self):
        return f"<Price(id={self.id}, product_id={self.product_id}, price={self.price})>"


class ProductMatch(Base):
    """
    Represents a match between similar products.
    
    Attributes:
        id (int): Unique identifier for the match
        source_product_id (int): Foreign key to the source Product
        target_product_id (int): Foreign key to the target Product
        similarity_score (float): Score indicating how similar the products are
    """
    __tablename__ = "product_matches"

    id = Column(Integer, primary_key=True)
    source_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    target_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source_product = relationship("Product", foreign_keys=[source_product_id], back_populates="source_matches")
    target_product = relationship("Product", foreign_keys=[target_product_id], back_populates="target_matches")

    def __repr__(self):
        return f"<ProductMatch(id={self.id}, score={self.similarity_score})>"


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function creates the database engine and all tables defined in the models.
    It should be called when setting up the application for the first time.
    """
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def get_session():
    """
    Create and return a new database session.
    
    Returns:
        Session: A new SQLAlchemy session object
    """
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session() 