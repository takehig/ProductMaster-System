#!/bin/bash

# ProductMaster System AWS デプロイスクリプト
# EC2: 57.183.66.123 (WealthAI-Server)

set -e

echo "=== ProductMaster System AWS デプロイ開始 ==="

# 変数設定
EC2_IP="57.183.66.123"
KEY_PATH="~/.ssh/wealthai-keypair.pem"
PROJECT_DIR="/home/ubuntu/ProductMaster"
RDS_ENDPOINT="productmaster-db.cqw3ao43tg2y.ap-northeast-1.rds.amazonaws.com"

echo "1. EC2への接続確認..."
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ubuntu@$EC2_IP "echo 'EC2接続成功'"

echo "2. 必要なパッケージのインストール..."
ssh -i $KEY_PATH ubuntu@$EC2_IP << 'EOF'
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql-client git nginx
sudo systemctl enable nginx
sudo systemctl start nginx
EOF

echo "3. ProductMasterディレクトリ作成..."
ssh -i $KEY_PATH ubuntu@$EC2_IP "mkdir -p $PROJECT_DIR"

echo "4. ProductMaster Systemファイルのアップロード..."
# ローカルのProductMasterプロジェクトをEC2にアップロード
scp -i $KEY_PATH -r /mnt/c/Users/takehig/QCHAT/.qchat_projects/ProductMaster/backend ubuntu@$EC2_IP:$PROJECT_DIR/
scp -i $KEY_PATH -r /mnt/c/Users/takehig/QCHAT/.qchat_projects/ProductMaster/database ubuntu@$EC2_IP:$PROJECT_DIR/

echo "5. Python仮想環境の作成..."
ssh -i $KEY_PATH ubuntu@$EC2_IP << EOF
cd $PROJECT_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF

echo "6. 環境設定ファイルの作成..."
ssh -i $KEY_PATH ubuntu@$EC2_IP << EOF
cat > $PROJECT_DIR/backend/.env << 'ENVEOF'
# ProductMaster System AWS環境設定
DATABASE_URL=postgresql://productmaster_admin:ProductMaster2025!@$RDS_ENDPOINT/productmaster
API_TOKEN=aws-productmaster-token-2025
APP_NAME=ProductMaster System
APP_VERSION=1.0.0
DEBUG=False
ALLOWED_ORIGINS=http://57.183.66.123,https://57.183.66.123
ENVEOF
EOF

echo "7. systemdサービスファイルの作成..."
ssh -i $KEY_PATH ubuntu@$EC2_IP << 'EOF'
sudo tee /etc/systemd/system/productmaster.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=ProductMaster System API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ProductMaster/backend
Environment=PATH=/home/ubuntu/ProductMaster/backend/venv/bin
ExecStart=/home/ubuntu/ProductMaster/backend/venv/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo systemctl daemon-reload
sudo systemctl enable productmaster
EOF

echo "8. Nginxの設定..."
ssh -i $KEY_PATH ubuntu@$EC2_IP << 'EOF'
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

echo "=== デプロイスクリプト作成完了 ==="
echo "RDSが利用可能になったら、以下を実行してください："
echo "1. RDS_ENDPOINTを実際のエンドポイントに更新"
echo "2. ./deploy_to_aws.sh を実行"
echo "3. データベース初期化とサービス開始"
