"""
商品価格API エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database.connection import get_db
from ..models.product import Product, ProductPrice
from ..schemas.product import (
    ProductPrice as ProductPriceSchema,
    ProductPriceCreate
)

router = APIRouter()

@router.get("/{product_id}", response_model=List[ProductPriceSchema])
async def get_product_prices(
    product_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    price_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """商品の価格履歴を取得"""
    # 商品の存在確認
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    query = db.query(ProductPrice).filter(ProductPrice.product_id == product_id)
    
    if start_date:
        query = query.filter(ProductPrice.price_date >= start_date)
    
    if end_date:
        query = query.filter(ProductPrice.price_date <= end_date)
    
    if price_type:
        query = query.filter(ProductPrice.price_type == price_type)
    
    prices = query.order_by(ProductPrice.price_date.desc()).limit(limit).all()
    return prices

@router.get("/{product_id}/latest", response_model=ProductPriceSchema)
async def get_latest_price(product_id: int, db: Session = Depends(get_db)):
    """商品の最新価格を取得"""
    # 商品の存在確認
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    latest_price = db.query(ProductPrice).filter(
        ProductPrice.product_id == product_id
    ).order_by(ProductPrice.price_date.desc(), ProductPrice.created_at.desc()).first()
    
    if not latest_price:
        raise HTTPException(status_code=404, detail="No price data found")
    
    return latest_price

@router.post("/{product_id}", response_model=ProductPriceSchema)
async def create_product_price(
    product_id: int,
    price_data: ProductPriceCreate,
    db: Session = Depends(get_db)
):
    """商品価格を登録"""
    # 商品の存在確認
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 価格データの作成
    price_dict = price_data.model_dump()
    price_dict["product_id"] = product_id
    
    db_price = ProductPrice(**price_dict)
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price
