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
        with open("../web/index.html", "r", encoding="utf-8") as f:
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
    return {"status": "healthy", "service": "ProductMaster", "features": ["upload", "download", "list"]}
