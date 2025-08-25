"""
ProductMaster System - メインアプリケーション
商品情報管理システムのFastAPIアプリケーション
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database.connection import engine, get_db
from app.api import products, categories, prices, performance
from app.models.base import Base

# 環境変数の読み込み
load_dotenv()

# セキュリティ
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時
    print("ProductMaster System starting up...")
    yield
    # アプリケーション終了時
    print("ProductMaster System shutting down...")

# FastAPIアプリケーションの作成
app = FastAPI(
    title="ProductMaster System",
    description="商品情報管理システム API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証チェック（簡易版）
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # 本番環境では適切なJWT検証を実装
    if token != os.getenv("API_TOKEN", "demo-token-12345"):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

# ルーターの登録
app.include_router(
    products.router,
    prefix="/api/products",
    tags=["products"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    categories.router,
    prefix="/api/categories",
    tags=["categories"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    prices.router,
    prefix="/api/prices",
    tags=["prices"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    performance.router,
    prefix="/api/performance",
    tags=["performance"],
    dependencies=[Depends(verify_token)]
)

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ProductMaster System"}

# ルートエンドポイント
@app.get("/")
async def root():
    return {
        "message": "ProductMaster System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
