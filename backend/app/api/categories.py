"""
商品カテゴリAPI エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.connection import get_db
from ..models.product import ProductCategory
from ..schemas.product import (
    ProductCategory as ProductCategorySchema,
    ProductCategoryCreate,
    ProductCategoryUpdate
)

router = APIRouter()

@router.get("/", response_model=List[ProductCategorySchema])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """カテゴリ一覧を取得"""
    query = db.query(ProductCategory)
    
    if is_active is not None:
        query = query.filter(ProductCategory.is_active == is_active)
    
    categories = query.order_by(ProductCategory.display_order, ProductCategory.category_name).offset(skip).limit(limit).all()
    return categories

@router.get("/{category_id}", response_model=ProductCategorySchema)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """カテゴリ詳細を取得"""
    category = db.query(ProductCategory).filter(ProductCategory.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=ProductCategorySchema)
async def create_category(category: ProductCategoryCreate, db: Session = Depends(get_db)):
    """カテゴリを作成"""
    # カテゴリコードの重複チェック
    existing = db.query(ProductCategory).filter(ProductCategory.category_code == category.category_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists")
    
    # 親カテゴリの存在チェック
    if category.parent_category_id:
        parent = db.query(ProductCategory).filter(ProductCategory.category_id == category.parent_category_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    db_category = ProductCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=ProductCategorySchema)
async def update_category(
    category_id: int,
    category_update: ProductCategoryUpdate,
    db: Session = Depends(get_db)
):
    """カテゴリを更新"""
    category = db.query(ProductCategory).filter(ProductCategory.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 親カテゴリの存在チェック
    if category_update.parent_category_id:
        parent = db.query(ProductCategory).filter(ProductCategory.category_id == category_update.parent_category_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
        
        # 自分自身を親にしようとしていないかチェック
        if category_update.parent_category_id == category_id:
            raise HTTPException(status_code=400, detail="Cannot set self as parent category")
    
    # 更新データの適用
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """カテゴリを削除（論理削除）"""
    category = db.query(ProductCategory).filter(ProductCategory.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.is_active = False
    db.commit()
    return {"message": "Category deleted successfully"}
