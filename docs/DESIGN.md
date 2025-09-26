# ProductMaster-System 設計書 v2.0.0

## 🎯 データベース正規化完了（2025-09-26）

### ✅ product_type 完全削除・category_code 統一設計

#### **正規化アーキテクチャ**
```
products テーブル (正規化済み)
├── category_id (外部キー) → product_categories.category_id
└── product_type カラム削除完了

products_with_category ビュー
├── category_code (product_categories.category_code)
├── category_name (product_categories.category_name)
└── 全商品情報 + カテゴリ情報統合
```

#### **API設計統一**
```python
# GET系API: ビュー使用（JOIN不要）
SELECT * FROM products_with_category

# 更新系API: 正規化テーブル操作
INSERT INTO products (..., category_id, ...)
UPDATE products SET category_id = ? WHERE ...
```

#### **レスポンス構造統一**
```json
{
  "product_code": "BOND001",
  "product_name": "国債10年",
  "category_code": "BOND",
  "category_name": "債券",
  "currency": "JPY"
}
```

## 📋 プロジェクト概要
**金融商品情報管理システム - 完全なCRUD機能・視覚的UI改善版**

### 🎯 システム目的
- 金融商品情報の包括的管理
- CSV インポート/エクスポート機能
- 商品更新・編集機能
- 視覚的に分かりやすい商品種別・リスクレベル表示

## 🏗️ システム構成

### 📊 基本情報
- **リポジトリ**: https://github.com/takehig/ProductMaster-System
- **サービスポート**: 8001
- **アクセスURL**: http://44.217.45.24/products/
- **技術スタック**: Python FastAPI, PostgreSQL, HTML5, Bootstrap 5

### 🔧 ファイル構造（簡素化済み）
```
ProductMaster-System/
├── backend/
│   ├── main.py              # 統一メインアプリケーション
│   ├── requirements.txt     # Python 依存関係
│   └── .env.example        # 環境変数例
├── web/
│   └── index.html          # フロントエンド（完全機能版）
└── DESIGN.md              # 本設計書
```

## 🔑 主要機能

### ✅ 完全実装済み機能
1. **商品管理機能（完全CRUD）**
   - ✅ CREATE: CSV アップロード機能
   - ✅ READ: 商品一覧表示・検索・フィルタリング
   - ✅ UPDATE: 商品編集・更新機能（PUT API）
   - ✅ DELETE: 論理削除対応

2. **CSV 処理機能**
   - ✅ CSV インポート（UTF-8 BOM対応）
   - ✅ CSV エクスポート（Excel互換）
   - ✅ 文字エンコーディング自動処理

3. **視覚的UI改善**
   - ✅ 商品種別色分けバッジ（6種類）
   - ✅ リスクレベルグラデーション（1-5段階）
   - ✅ レスポンシブデザイン

4. **商品種別対応**
   - ✅ 株式（青色）
   - ✅ 債券（緑色）
   - ✅ 投資信託（黄色）
   - ✅ 上場投資信託（水色）← 新規追加
   - ✅ REIT（グレー）
   - ✅ コモディティ（黒色）

### 🔧 API エンドポイント（完全版）
```
GET  /                      # HTML表示
GET  /api/products          # 商品一覧取得
PUT  /api/products/{id}     # 商品更新（新規実装）
GET  /api/products/download # CSV ダウンロード
POST /api/products/upload   # CSV アップロード
GET  /health               # ヘルスチェック
GET  /api/version          # バージョン情報
```

## 🗄️ データベース設計

### 📊 標準データベース設定
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=productmaster
DB_USER=productmaster_user
DB_PASSWORD=productmaster123
```

### 📋 テーブル構成
```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_name_en VARCHAR(200),
    product_type VARCHAR(50) NOT NULL,
    category_id INTEGER,
    currency VARCHAR(10) DEFAULT 'JPY',
    issuer VARCHAR(200),
    minimum_investment DECIMAL(15,2) DEFAULT 0,
    maximum_investment DECIMAL(15,2),
    commission_rate DECIMAL(5,4) DEFAULT 0,
    risk_level INTEGER DEFAULT 1 CHECK (risk_level BETWEEN 1 AND 5),
    maturity_date DATE,
    interest_rate DECIMAL(5,4),
    dividend_yield DECIMAL(5,4),
    description TEXT,
    features TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎨 UI/UX 設計

### 🌈 色分けシステム
```css
/* 商品種別バッジ */
.badge-type-stock { background-color: #0d6efd; }      /* 青 - 株式 */
.badge-type-bond { background-color: #198754; }       /* 緑 - 債券 */
.badge-type-fund { background-color: #ffc107; }       /* 黄 - 投資信託 */
.badge-type-etf { background-color: #0dcaf0; }        /* 水色 - 上場投資信託 */
.badge-type-reit { background-color: #6c757d; }       /* グレー - REIT */
.badge-type-commodity { background-color: #212529; }  /* 黒 - コモディティ */

/* リスクレベルグラデーション */
.badge-risk-1 { background-color: #d4edda; }  /* 薄い緑 - 最も安全 */
.badge-risk-2 { background-color: #b8daff; }  /* 青 - 安全 */
.badge-risk-3 { background-color: #fff3cd; }  /* 黄 - 中程度 */
.badge-risk-4 { background-color: #f8d7da; }  /* オレンジ - 高リスク */
.badge-risk-5 { background-color: #dc3545; }  /* 赤 - 最高リスク */
```

### 📱 レスポンシブ対応
- **デスクトップ**: テーブル表示
- **タブレット**: カード表示
- **モバイル**: 縦積みカード表示

## 🔧 商品更新機能（新規実装）

### 📝 更新フロー
```javascript
1. 編集ボタンクリック → 商品情報をモーダルに読み込み
2. フォーム編集 → 商品情報を変更
3. 更新ボタンクリック → PUT API で商品更新
4. 成功メッセージ → 一覧画面を再読み込み
```

### 🔧 PUT API 実装
```python
@app.put("/api/products/{product_id}")
def update_product(product_id: int, product_data: dict):
    """商品を更新"""
    # 商品存在確認 → データ更新 → 更新結果返却
```

## 🚀 デプロイ・運用

### 📦 systemd サービス（統一済み）
```ini
[Unit]
Description=ProductMaster Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/ProductMaster/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

### 🔄 運用コマンド
```bash
# サービス管理
sudo systemctl start productmaster
sudo systemctl stop productmaster
sudo systemctl restart productmaster
sudo systemctl status productmaster

# ログ確認
sudo journalctl -u productmaster -f
```

## 📈 パフォーマンス・監視

### 📊 監視項目
- **API レスポンス時間**: 商品取得・更新速度
- **データベース接続**: PostgreSQL 接続状態
- **CSV 処理性能**: インポート/エクスポート速度
- **UI 応答性**: フロントエンド操作性

## 🔮 今後の拡張予定

### 📋 計画中機能
1. **商品詳細画面**: 個別商品の詳細表示
2. **商品比較機能**: 複数商品の比較表示
3. **価格履歴管理**: 商品価格の時系列管理
4. **AIChat 連携**: MCP 経由での商品検索

## 📝 更新履歴
- **2025-09-13**: 設計書更新・PUT API実装・UI改善・上場投資信託追加
- **2025-09-12**: ゴミ削除・ファイル統一・構造簡素化
- **2025-08-30**: 基本CRUD機能実装完了
- **2025-08-28**: プロジェクト開始
