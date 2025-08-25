"""
商品関連のPydanticスキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# 商品カテゴリスキーマ
class ProductCategoryBase(BaseModel):
    category_code: str = Field(..., max_length=20)
    category_name: str = Field(..., max_length=100)
    parent_category_id: Optional[int] = None
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, max_length=100)
    parent_category_id: Optional[int] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class ProductCategory(ProductCategoryBase):
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 商品スキーマ
class ProductBase(BaseModel):
    product_code: str = Field(..., max_length=50)
    product_name: str = Field(..., max_length=200)
    product_name_en: Optional[str] = Field(None, max_length=200)
    product_type: str = Field(..., max_length=50)
    category_id: Optional[int] = None
    currency: str = Field(default="JPY", max_length=10)
    issuer: Optional[str] = Field(None, max_length=100)
    issuer_rating: Optional[str] = Field(None, max_length=10)
    maturity_date: Optional[date] = None
    interest_rate: Optional[Decimal] = None
    coupon_frequency: Optional[int] = None
    risk_level: Optional[int] = Field(None, ge=1, le=5)
    minimum_investment: Optional[int] = None
    investment_unit: int = 1
    commission_rate: Optional[Decimal] = None
    management_fee_rate: Optional[Decimal] = None
    early_redemption_fee: Optional[Decimal] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    target_customer_type: Optional[str] = Field(None, max_length=50)
    tax_treatment: Optional[str] = Field(None, max_length=50)
    liquidity_level: Optional[str] = Field(None, max_length=20)
    benchmark_index: Optional[str] = Field(None, max_length=100)
    inception_date: Optional[date] = None
    is_esg: bool = False
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=200)
    product_name_en: Optional[str] = Field(None, max_length=200)
    product_type: Optional[str] = Field(None, max_length=50)
    category_id: Optional[int] = None
    currency: Optional[str] = Field(None, max_length=10)
    issuer: Optional[str] = Field(None, max_length=100)
    issuer_rating: Optional[str] = Field(None, max_length=10)
    maturity_date: Optional[date] = None
    interest_rate: Optional[Decimal] = None
    coupon_frequency: Optional[int] = None
    risk_level: Optional[int] = Field(None, ge=1, le=5)
    minimum_investment: Optional[int] = None
    investment_unit: Optional[int] = None
    commission_rate: Optional[Decimal] = None
    management_fee_rate: Optional[Decimal] = None
    early_redemption_fee: Optional[Decimal] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    target_customer_type: Optional[str] = Field(None, max_length=50)
    tax_treatment: Optional[str] = Field(None, max_length=50)
    liquidity_level: Optional[str] = Field(None, max_length=20)
    benchmark_index: Optional[str] = Field(None, max_length=100)
    inception_date: Optional[date] = None
    is_esg: Optional[bool] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[ProductCategory] = None
    
    class Config:
        from_attributes = True

# 商品価格スキーマ
class ProductPriceBase(BaseModel):
    product_id: int
    price: Decimal = Field(...)
    price_date: date
    price_type: str = "current"
    bid_price: Optional[Decimal] = None
    ask_price: Optional[Decimal] = None
    volume: Optional[int] = None
    source: Optional[str] = Field(None, max_length=50)

class ProductPriceCreate(ProductPriceBase):
    pass

class ProductPrice(ProductPriceBase):
    price_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 商品検索スキーマ
class ProductSearchParams(BaseModel):
    q: Optional[str] = None  # 検索キーワード
    product_type: Optional[str] = None
    category_id: Optional[int] = None
    risk_level: Optional[int] = None
    currency: Optional[str] = None
    issuer: Optional[str] = None
    is_active: Optional[bool] = True
    min_investment: Optional[int] = None
    max_investment: Optional[int] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

class ProductSearchResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    size: int
    pages: int
