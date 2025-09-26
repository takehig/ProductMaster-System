from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import io
import csv
import pandas as pd
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ProductMaster System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信
app.mount("/static", StaticFiles(directory="../web"), name="static")

# カテゴリ登録用モデル
class CategoryCreate(BaseModel):
    category_name: str
    category_code: str
    description: str = None
    display_order: int = 0
    is_active: bool = True

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "productmaster"),
        user=os.getenv("DB_USER", "productmaster_user"),
        password=os.getenv("DB_PASSWORD", "productmaster123")
    )

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("/home/ec2-user/ProductMaster/web/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>ProductMaster System</h1><p>Loading...</p>"

@app.get("/api/categories")
def get_categories():
    """カテゴリ一覧取得"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT category_id, category_name, category_code, description, 
                   display_order, is_active, created_at, updated_at
            FROM product_categories 
            ORDER BY display_order, category_name
        """)
        
        categories = []
        for row in cur.fetchall():
            categories.append({
                "category_id": row[0],
                "category_name": row[1],
                "category_code": row[2],
                "description": row[3],
                "display_order": row[4],
                "is_active": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None
            })
        
        cur.close()
        conn.close()
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"カテゴリ取得エラー: {str(e)}")

@app.post("/api/categories")
def create_category(category: CategoryCreate):
    """カテゴリ新規登録"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # カテゴリコードの重複チェック
        cur.execute("SELECT category_id FROM product_categories WHERE category_code = %s", (category.category_code,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="カテゴリコードが既に存在します")
        
        # カテゴリ登録
        cur.execute("""
            INSERT INTO product_categories (category_name, category_code, description, display_order, is_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING category_id
        """, (category.category_name, category.category_code, category.description, 
              category.display_order, category.is_active))
        
        category_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return {"message": "カテゴリが正常に登録されました", "category_id": category_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"カテゴリ登録エラー: {str(e)}")

@app.get("/api/categories/{category_id}")
def get_category_detail(category_id: int):
    """カテゴリ詳細取得"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT category_id, category_code, category_name, description, display_order, is_active FROM product_categories WHERE category_id = %s", (category_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return {
                "category_id": result[0],
                "category_code": result[1],
                "category_name": result[2],
                "description": result[3],
                "display_order": result[4],
                "is_active": result[5]
                "category_code": result[2],
                "description": result[3],
                "display_order": result[4],
                "is_active": result[5]
            }
        else:
            raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.put("/api/categories/{category_id}")
async def update_category(category_id: int, category_data: dict):
    """カテゴリ更新"""
    print(f"[DEBUG] update_category called: category_id={category_id}")
    print(f"[DEBUG] category_data type: {type(category_data)}")
    print(f"[DEBUG] category_data content: {category_data}")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # カテゴリの存在確認
        cur.execute("SELECT category_id FROM product_categories WHERE category_id = %s", (category_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
        
        # カテゴリ更新
        cur.execute("""
            UPDATE product_categories SET 
                category_name = %s, category_code = %s, description = %s, 
                display_order = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE category_id = %s
        """, (
            category_data.get('category_name'),
            category_data.get('category_code'),
            category_data.get('description'),
            category_data.get('display_order', 0),
            category_data.get('is_active', True),
            category_id
        ))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {"message": "カテゴリを更新しました", "category_id": category_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int):
    """カテゴリ削除"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # カテゴリの存在確認
        cur.execute("SELECT category_id FROM product_categories WHERE category_id = %s", (category_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
        
        # カテゴリ削除（論理削除）
        cur.execute("UPDATE product_categories SET is_active = false WHERE category_id = %s", (category_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {"message": "カテゴリを削除しました", "category_id": category_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/products")
def get_products():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT product_id, product_code, product_name, category_code, category_name,
                   currency, issuer, minimum_investment, risk_level, description
            FROM products_with_category 
            WHERE is_active = true
            ORDER BY product_id
        """)
        rows = cur.fetchall()
        
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "product_code": row[1],
                "product_name": row[2],
                "category_code": row[3],
                "category_name": row[4],
                "currency": row[5],
                "issuer": row[6],
                "minimum_investment": float(row[7]) if row[7] else 0,
                "risk_level": row[8],
                "description": row[9] or ""
            })
        
        cur.close()
        conn.close()
        
        return {"products": products, "total": len(products), "status": "success"}
    except Exception as e:
        return {"products": [], "total": 0, "status": "error", "message": str(e)}

@app.get("/api/products/{product_id}")
def get_product_detail(product_id: int):
    """商品詳細取得"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT product_id, product_code, product_name, category_code, category_name,
                   currency, issuer, minimum_investment, risk_level, description
            FROM products_with_category WHERE product_id = %s
        """, (product_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "product_code": result[1],
                "product_name": result[2],
                "category_code": result[3],
                "category_name": result[4],
                "currency": result[5],
                "issuer": result[6],
                "minimum_investment": float(result[7]) if result[7] else 0,
                "risk_level": result[8],
                "description": result[9] or ""
            }
        else:
            raise HTTPException(status_code=404, detail="商品が見つかりません")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/products/")
async def create_product(product_data: dict):
    """新規商品を追加"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 必須フィールドチェック
        if not product_data.get('product_code'):
            raise HTTPException(status_code=400, detail="商品コードは必須です")
        if not product_data.get('product_name'):
            raise HTTPException(status_code=400, detail="商品名は必須です")
        
        # 重複チェック
        cur.execute("SELECT product_id FROM products_with_category WHERE product_code = %s", (product_data['product_code'],))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="この商品コードは既に存在します")
        
        # 新規商品追加
        cur.execute("""
            INSERT INTO products (product_code, product_name, category_id, currency, issuer, 
                                minimum_investment, risk_level, description, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING product_id
        """, (
            product_data['product_code'],
            product_data['product_name'],
            product_data.get('category_id', 1),  # デフォルト: 債券
            product_data.get('currency', 'JPY'),
            product_data.get('issuer', ''),
            product_data.get('minimum_investment', 0),
            product_data.get('risk_level', 1),
            product_data.get('description', ''),
            product_data.get('is_active', True),
            datetime.now(),
            datetime.now()
        ))
        
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "product_id": product_id, "message": "商品を追加しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": f"商品追加エラー: {str(e)}"}

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, product_data: dict):
    """商品を更新"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 商品の存在確認
        cur.execute("SELECT product_id FROM products_with_category WHERE product_id = %s", (product_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        # 商品情報更新
        update_query = """
            UPDATE products SET 
                product_code = %s,
                product_name = %s,
                category_id = %s,
                currency = %s,
                issuer = %s,
                minimum_investment = %s,
                risk_level = %s,
                description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
        """
        
        cur.execute(update_query, (
            product_data.get("product_code"),
            product_data.get("product_name"),
            product_data.get("category_id", 1),  # デフォルト: 債券
            product_data.get("currency", "JPY"),
            product_data.get("issuer"),
            float(product_data.get("minimum_investment", 0)) if product_data.get("minimum_investment") else 0,
            product_data.get("risk_level", 1),
            product_data.get("description"),
            product_id
        ))
        
        conn.commit()
        
        # 更新後のデータを取得
        cur.execute("""
            SELECT product_id, product_code, product_name, category_code, category_name,
                   currency, issuer, minimum_investment, risk_level, description
            FROM products_with_category WHERE product_id = %s
        """, (product_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "product_code": result[1],
                "product_name": result[2],
                "category_code": result[3],
                "category_name": result[4],
                "currency": result[5],
                "issuer": result[6],
                "minimum_investment": float(result[7]) if result[7] else 0,
                "risk_level": result[8],
                "description": result[9] or "",
                "message": "Product updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Update failed")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/products/download")
def download_products():
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("""
            SELECT product_code, product_name, category_code, category_name, currency, issuer, 
                   minimum_investment, risk_level, description
            FROM products_with_category 
            WHERE is_active = true
            ORDER BY product_id
        """, conn)
        conn.close()
        
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=products.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    """商品削除"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 商品の存在確認
        cur.execute("SELECT product_id FROM products_with_category WHERE product_id = %s", (product_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="商品が見つかりません")
        
        # 商品削除（論理削除）
        cur.execute("UPDATE products SET is_active = false WHERE product_id = %s", (product_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {"message": "商品を削除しました", "product_id": product_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/products/upload")
async def upload_products(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        uploaded_count = 0
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO products (product_code, product_name, category_id, currency, issuer, 
                                    minimum_investment, risk_level, description, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true, %s)
                ON CONFLICT (product_code) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category_id = EXCLUDED.category_id,
                    currency = EXCLUDED.currency,
                    issuer = EXCLUDED.issuer,
                    minimum_investment = EXCLUDED.minimum_investment,
                    risk_level = EXCLUDED.risk_level,
                    description = EXCLUDED.description,
                    updated_at = %s
            """, (
                row.get('product_code', ''),
                row.get('product_name', ''),
                row.get('category_id', 1),  # デフォルト: 債券
                row.get('currency', 'JPY'),
                row.get('issuer', ''),
                row.get('minimum_investment', 0),
                row.get('risk_level', 1),
                row.get('description', ''),
                datetime.now(),
                datetime.now()
            ))
            uploaded_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "uploaded": uploaded_count, "message": f"{uploaded_count}件のデータをアップロードしました"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ProductMaster", "features": ["upload", "download", "list", "update"]}

@app.get("/api/version")
def get_version():
    """バージョン情報を取得"""
    import subprocess
    import os
    
    try:
        # Gitコミット情報を取得
        os.chdir("/home/ec2-user/ProductMaster")
        
        # 最新コミットハッシュ
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # 最新コミット日時
        commit_date = subprocess.check_output(
            ["git", "log", "-1", "--format=%ci"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # 最新コミットメッセージ
        commit_message = subprocess.check_output(
            ["git", "log", "-1", "--format=%s"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # ブランチ名
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {
            "version": f"v1.0.0-{commit_hash}",
            "commit_hash": commit_hash,
            "commit_date": commit_date,
            "commit_message": commit_message,
            "branch": branch,
            "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": "ProductMaster System"
        }
        
    except Exception as e:
        # Gitが利用できない場合のフォールバック
        return {
            "version": "v1.0.0-unknown",
            "commit_hash": "unknown",
            "commit_date": "unknown",
            "commit_message": "Git information not available",
            "branch": "unknown",
            "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": "ProductMaster System",
            "error": str(e)
        }

# アプリケーション起動時のルート一覧ログ
print("[DEBUG] ProductMaster API Routes:")
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        print(f"[DEBUG] {list(route.methods)} {route.path}")
print("[DEBUG] ProductMaster API initialization complete")
