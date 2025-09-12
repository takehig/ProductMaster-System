from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
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

@app.get("/api/products")
def get_products():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT product_id, product_code, product_name, product_type, 
                   currency, issuer, minimum_investment, risk_level, description
            FROM products 
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
                "product_type": row[3],
                "currency": row[4],
                "issuer": row[5],
                "minimum_investment": float(row[6]) if row[6] else 0,
                "risk_level": row[7],
                "description": row[8] or ""
            })
        
        cur.close()
        conn.close()
        
        return {"products": products, "total": len(products), "status": "success"}
    except Exception as e:
        return {"products": [], "total": 0, "status": "error", "message": str(e)}

@app.put("/api/products/{product_id}")
def update_product(product_id: int, product_data: dict):
    """商品を更新"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 商品の存在確認
        cur.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        # 商品情報更新
        update_query = """
            UPDATE products SET 
                product_code = %s,
                product_name = %s,
                product_type = %s,
                currency = %s,
                issuer = %s,
                risk_level = %s,
                description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
        """
        
        cur.execute(update_query, (
            product_data.get("product_code"),
            product_data.get("product_name"),
            product_data.get("product_type"),
            product_data.get("currency", "JPY"),
            product_data.get("issuer"),
            product_data.get("risk_level", 1),
            product_data.get("description"),
            product_id
        ))
        
        conn.commit()
        
        # 更新後のデータを取得
        cur.execute("""
            SELECT product_id, product_code, product_name, product_type, 
                   currency, issuer, minimum_investment, risk_level, description
            FROM products WHERE product_id = %s
        """, (product_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "product_code": result[1],
                "product_name": result[2],
                "product_type": result[3],
                "currency": result[4],
                "issuer": result[5],
                "minimum_investment": float(result[6]) if result[6] else 0,
                "risk_level": result[7],
                "description": result[8] or "",
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
            SELECT product_code, product_name, product_type, currency, issuer, 
                   minimum_investment, risk_level, description
            FROM products 
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
                INSERT INTO products (product_code, product_name, product_type, currency, issuer, 
                                    minimum_investment, risk_level, description, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true, %s)
                ON CONFLICT (product_code) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_type = EXCLUDED.product_type,
                    currency = EXCLUDED.currency,
                    issuer = EXCLUDED.issuer,
                    minimum_investment = EXCLUDED.minimum_investment,
                    risk_level = EXCLUDED.risk_level,
                    description = EXCLUDED.description,
                    updated_at = %s
            """, (
                row.get('product_code', ''),
                row.get('product_name', ''),
                row.get('product_type', ''),
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
