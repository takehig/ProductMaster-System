"""
商品関連のデータモデル
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, Date, Time, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ProductCategory(Base):
    __tablename__ = "product_categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String(20), unique=True, nullable=False)
    category_name = Column(String(100), nullable=False)
    parent_category_id = Column(Integer, ForeignKey("product_categories.category_id"))
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # リレーション
    products = relationship("Product", back_populates="category")
    parent = relationship("ProductCategory", remote_side=[category_id])

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    product_name_en = Column(String(200))
    product_type = Column(String(50), nullable=False)
    category_id = Column(Integer, ForeignKey("product_categories.category_id"))
    currency = Column(String(10), default="JPY")
    issuer = Column(String(100))
    issuer_rating = Column(String(10))
    maturity_date = Column(Date)
    interest_rate = Column(DECIMAL(5, 4))
    coupon_frequency = Column(Integer)
    risk_level = Column(Integer)
    minimum_investment = Column(Integer)
    investment_unit = Column(Integer, default=1)
    commission_rate = Column(DECIMAL(5, 4))
    management_fee_rate = Column(DECIMAL(5, 4))
    early_redemption_fee = Column(DECIMAL(5, 4))
    description = Column(Text)
    features = Column(ARRAY(Text))
    target_customer_type = Column(String(50))
    tax_treatment = Column(String(50))
    liquidity_level = Column(String(20))
    benchmark_index = Column(String(100))
    inception_date = Column(Date)
    is_esg = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # リレーション
    category = relationship("ProductCategory", back_populates="products")
    prices = relationship("ProductPrice", back_populates="product")
    performance = relationship("ProductPerformance", back_populates="product")
    documents = relationship("ProductDocument", back_populates="product")

class ProductPrice(Base):
    __tablename__ = "product_prices"
    
    price_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    price = Column(DECIMAL(15, 2), nullable=False)
    price_date = Column(Date, nullable=False)
    price_time = Column(Time)
    price_type = Column(String(20), default="current")
    bid_price = Column(DECIMAL(15, 2))
    ask_price = Column(DECIMAL(15, 2))
    volume = Column(Integer)
    source = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    
    # リレーション
    product = relationship("Product", back_populates="prices")

class ProductPerformance(Base):
    __tablename__ = "product_performance"
    
    performance_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    period_type = Column(String(20), nullable=False)
    return_rate = Column(DECIMAL(8, 4))
    volatility = Column(DECIMAL(8, 4))
    sharpe_ratio = Column(DECIMAL(8, 4))
    max_drawdown = Column(DECIMAL(8, 4))
    benchmark_return = Column(DECIMAL(8, 4))
    alpha = Column(DECIMAL(8, 4))
    beta = Column(DECIMAL(8, 4))
    calculated_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # リレーション
    product = relationship("Product", back_populates="performance")

class ProductDocument(Base):
    __tablename__ = "product_documents"
    
    document_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    document_type = Column(String(50), nullable=False)
    document_name = Column(String(200), nullable=False)
    file_path = Column(String(500))
    file_url = Column(String(500))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    language = Column(String(10), default="ja")
    publish_date = Column(Date)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # リレーション
    product = relationship("Product", back_populates="documents")
