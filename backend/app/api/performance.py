"""
商品パフォーマンスAPI エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.connection import get_db
from ..models.product import Product, ProductPerformance

router = APIRouter()

@router.get("/{product_id}")
async def get_product_performance(
    product_id: int,
    period_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """商品のパフォーマンスデータを取得"""
    # 商品の存在確認
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    query = db.query(ProductPerformance).filter(ProductPerformance.product_id == product_id)
    
    if period_type:
        query = query.filter(ProductPerformance.period_type == period_type)
    
    performance = query.order_by(ProductPerformance.calculated_date.desc()).all()
    return performance
