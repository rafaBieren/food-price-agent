from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from config.settings import DATABASE_URL

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    size = Column(Float)
    unit = Column(String)  # kg, l, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prices = relationship("Price", back_populates="product")

    def __repr__(self):
        return f"<Product(name='{self.name}', size={self.size} {self.unit})>"


class Supermarket(Base):
    __tablename__ = "supermarkets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    chain_id = Column(String, nullable=False)  # e.g., "rami_levy"
    branch_id = Column(String, nullable=False)
    branch_name = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prices = relationship("Price", back_populates="supermarket")

    def __repr__(self):
        return f"<Supermarket(name='{self.name}', branch='{self.branch_name}')>"


class Price(Base):
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
        return f"<Price(product_id={self.product_id}, price={self.price})>"


class ProductMatch(Base):
    __tablename__ = "product_matches"

    id = Column(Integer, primary_key=True)
    source_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    target_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProductMatch(source={self.source_product_id}, target={self.target_product_id}, score={self.similarity_score})>"


def init_db():
    """Initialize the database and create all tables."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine 