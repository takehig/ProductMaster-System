"""
商品API エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import math

from ..database.connection import get_db
from ..models.product import Product, ProductCategory
from ..schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductSearchParams,
    ProductSearchResponse
)

router = APIRouter()

@router.get("/", response_model=List[ProductSchema])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    product_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """商品一覧を取得"""
    query = db.query(Product)
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    q: Optional[str] = None,
    product_type: Optional[str] = None,
    category_id: Optional[int] = None,
    risk_level: Optional[int] = None,
    currency: Optional[str] = None,
    issuer: Optional[str] = None,
    is_active: Optional[bool] = True,
    min_investment: Optional[int] = None,
    max_investment: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """商品検索"""
    query = db.query(Product)
    
    # 検索条件の適用
    conditions = []
    
    if q:
        # 商品名または説明での検索
        conditions.append(
            or_(
                Product.product_name.ilike(f"%{q}%"),
                Product.product_name_en.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%"),
                Product.issuer.ilike(f"%{q}%")
            )
        )
    
    if product_type:
        conditions.append(Product.product_type == product_type)
    
    if category_id:
        conditions.append(Product.category_id == category_id)
    
    if risk_level:
        conditions.append(Product.risk_level == risk_level)
    
    if currency:
        conditions.append(Product.currency == currency)
    
    if issuer:
        conditions.append(Product.issuer.ilike(f"%{issuer}%"))
    
    if is_active is not None:
        conditions.append(Product.is_active == is_active)
    
    if min_investment:
        conditions.append(Product.minimum_investment >= min_investment)
    
    if max_investment:
        conditions.append(Product.minimum_investment <= max_investment)
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    # 総件数を取得
    total = query.count()
    
    # ページネーション
    offset = (page - 1) * size
    products = query.offset(offset).limit(size).all()
    
    pages = math.ceil(total / size)
    
    return ProductSearchResponse(
        products=products,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """商品詳細を取得"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductSchema)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """商品を作成"""
    # 商品コードの重複チェック
    existing = db.query(Product).filter(Product.product_code == product.product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    
    # カテゴリの存在チェック
    if product.category_id:
        category = db.query(ProductCategory).filter(ProductCategory.category_id == product.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """商品を更新"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # カテゴリの存在チェック
    if product_update.category_id:
        category = db.query(ProductCategory).filter(ProductCategory.category_id == product_update.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # 更新データの適用
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """商品を削除（論理削除）"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    return {"message": "Product deleted successfully"}

@router.get("/{product_id}/similar", response_model=List[ProductSchema])
async def get_similar_products(
    product_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """類似商品を取得"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 同じタイプ・カテゴリの商品を検索
    similar_products = db.query(Product).filter(
        and_(
            Product.product_id != product_id,
            Product.product_type == product.product_type,
            Product.is_active == True
        )
    ).limit(limit).all()
    
    return similar_products
