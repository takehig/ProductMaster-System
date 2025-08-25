# ProductMaster System

金融商品の包括的な情報管理とAPI提供プラットフォーム

## 機能

- 商品情報管理
- CSV アップロード/ダウンロード
- 商品検索・フィルタリング
- リアルタイムデータ更新
- RESTful API提供

## 技術スタック

- **Backend**: FastAPI + psycopg2
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5 + JavaScript
- **File Processing**: pandas
- **Deployment**: GitHub + SSH

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# データベース設定
# PostgreSQL設定とサンプルデータ投入

# アプリケーション起動
python backend/fixed_main.py
```

## API エンドポイント

- `GET /` - Web UI
- `GET /api/products` - 商品一覧取得
- `GET /api/products/download` - CSV ダウンロード
- `POST /api/products/upload` - CSV アップロード
- `GET /health` - ヘルスチェック

## データ形式

### CSV アップロード形式
```csv
product_code,product_name,product_type,currency,issuer,minimum_investment,risk_level,description
JGB394-10Y,第394回10年国債,bond,JPY,日本国,10000,1,安全性の高い国債
```

## デプロイ

```bash
# ローカル開発後
git add .
git commit -m "機能追加"
git push origin main

# EC2で更新
./deploy/update.sh
```
