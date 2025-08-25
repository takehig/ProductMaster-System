# ProductMaster System AWS デプロイ完了手順

## 現在の状況
- ✅ EC2 (57.183.66.123) にProductMaster Systemファイル配置完了
- ✅ Python環境・ライブラリインストール完了
- 🔄 RDS PostgreSQL (productmaster-db-v2) 作成中

## RDS作成完了後の手順

### 1. RDSエンドポイント確認
```bash
aws rds describe-db-instances --db-instance-identifier productmaster-db-v2 --region ap-northeast-1 --query 'DBInstances[0].Endpoint.Address'
```

### 2. 環境設定ファイル更新
```bash
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 << 'EOF'
cat > /home/ubuntu/ProductMaster/backend/.env << 'ENVEOF'
DATABASE_URL=postgresql://productmaster_admin:ProductMaster2025!@[RDS_ENDPOINT]/productmaster
API_TOKEN=aws-productmaster-token-2025
APP_NAME=ProductMaster System
APP_VERSION=1.0.0
DEBUG=False
ALLOWED_ORIGINS=http://57.183.66.123,https://57.183.66.123
ENVEOF
EOF
```

### 3. データベース初期化
```bash
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 << 'EOF'
export PGPASSWORD="ProductMaster2025!"
psql -h [RDS_ENDPOINT] -U productmaster_admin -d postgres -c "CREATE DATABASE productmaster;"

cd /home/ubuntu/ProductMaster/backend
source venv/bin/activate
python -c "
from database.database import engine
from database.models import Base
Base.metadata.create_all(bind=engine)
print('Database schema created successfully')
"

python database/sample_data.py
EOF
```

### 4. systemdサービス設定
```bash
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 << 'EOF'
sudo tee /etc/systemd/system/productmaster.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=ProductMaster System API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ProductMaster/backend
Environment=PATH=/home/ubuntu/ProductMaster/backend/venv/bin
ExecStart=/home/ubuntu/ProductMaster/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo systemctl daemon-reload
sudo systemctl enable productmaster
sudo systemctl start productmaster
EOF
```

### 5. Nginx設定
```bash
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 << 'EOF'
sudo tee /etc/nginx/sites-available/productmaster > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name 57.183.66.123;
    
    # ProductMaster API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # ProductMaster Web UI
    location /products/ {
        alias /home/ubuntu/ProductMaster/web/;
        index index.html;
        try_files $uri $uri/ /products/index.html;
    }
    
    # WealthAI CRM (既存)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/productmaster /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
EOF
```

### 6. 動作確認
```bash
# API確認
curl -H "Authorization: Bearer aws-productmaster-token-2025" http://57.183.66.123/api/products/

# Webページ確認
curl http://57.183.66.123/products/
```

### 7. API Gateway設定
- AWS コンソールでAPI Gateway作成
- ProductMaster APIエンドポイントを統合
- 認証・CORS設定

## アクセスURL
- **CRM**: http://57.183.66.123/
- **ProductMaster Web**: http://57.183.66.123/products/
- **ProductMaster API**: http://57.183.66.123/api/
- **API仕様**: http://57.183.66.123/api/docs

作成日時: 2025-08-21 18:20 UTC
