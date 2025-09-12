# ProductMaster System 設計書

## 📋 システム概要

### システム名
**ProductMaster System** - 金融商品情報管理システム

### 目的
- 金融商品の包括的な情報管理
- CSV インポート/エクスポート機能
- API による商品データ提供
- 多様な表示形式（カード・テーブル）

## 🏗️ アーキテクチャ

### 技術スタック
- **Backend**: Python 3.9+, FastAPI
- **Frontend**: HTML5, JavaScript ES6+, Bootstrap 5
- **Database**: PostgreSQL (productmaster DB)
- **File Processing**: CSV, UTF-8/Shift-JIS対応
- **Deployment**: systemd, Nginx reverse proxy

### サービス構成
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Nginx Proxy   │    │  FastAPI App    │
│                 │◄──►│ (/products/)    │◄──►│   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ PostgreSQL DB   │
                                               │(productmaster)  │
                                               └─────────────────┘
```

## 🗄️ データベース設計

### 主要テーブル
```sql
-- 商品情報
products (
    id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE,
    product_name VARCHAR(200),
    product_type VARCHAR(100),
    currency VARCHAR(10),
    issuer VARCHAR(200),
    maturity_date DATE,
    interest_rate DECIMAL(5,2),
    risk_level INTEGER,
    minimum_investment DECIMAL(15,2),
    commission_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 商品カテゴリ
product_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### データ統計（2025-09-05現在）
- **商品総数**: 16件
- **商品種別**: 
  - bond（社債）: 6件
  - stock（株式）: 7件
  - fund（投資信託）: 3件

### 商品データ例
```json
{
  "product_code": "JP-TOYOTA-2027",
  "product_name": "トヨタ自動車第51回社債",
  "product_type": "bond",
  "currency": "JPY",
  "issuer": "トヨタ自動車株式会社",
  "maturity_date": "2027-03-15",
  "interest_rate": 1.25,
  "risk_level": 2,
  "minimum_investment": 1000000.00,
  "commission_rate": 0.50,
  "is_active": true,
  "description": "世界最大の自動車メーカーが発行する安定性の高い社債。ESG投資にも対応。"
}
```

## 🎯 機能仕様

### 1. 商品管理機能
- **商品一覧表示**: カード・テーブル表示切り替え
- **商品検索**: 商品名・コードでのリアルタイム検索
- **商品詳細**: 全項目表示・編集機能
- **商品登録**: フォーム入力・バリデーション

### 2. CSV機能
- **インポート**: 
  - ドラッグ&ドロップ対応
  - 文字エンコーディング自動判定
  - エラーハンドリング・プレビュー機能
- **エクスポート**:
  - UTF-8 BOM付きCSV出力
  - Excel互換性確保
  - カスタムフィールド選択

### 3. API機能
```
GET  /api/products        # 商品一覧取得
GET  /api/products/{id}   # 商品詳細取得
POST /api/products        # 商品登録
PUT  /api/products/{id}   # 商品更新
DELETE /api/products/{id} # 商品削除
GET  /api/version         # バージョン情報
GET  /api/health          # ヘルスチェック
```

## 🎨 UI/UX設計

### 表示切り替え機能
```
┌─────────────────────────────────────────┐
│  [🔍 検索] [📊 カード] [📋 テーブル]      │
├─────────────────────────────────────────┤
│                                         │
│  カード表示:                             │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
│  │商品A│ │商品B│ │商品C│ │商品D│      │
│  └─────┘ └─────┘ └─────┘ └─────┘      │
│                                         │
│  テーブル表示:                           │
│  ┌─────────────────────────────────┐   │
│  │コード│商品名│種別│通貨│リスク│    │   │
│  ├─────────────────────────────────┤   │
│  │JP001 │商品A│bond│JPY │  2   │    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### レスポンシブ対応
- **デスクトップ (1200px+)**: 4列カード表示
- **ラップトップ (992px+)**: 3列カード表示
- **タブレット (768px+)**: 2列カード表示
- **モバイル (576px+)**: 1列カード表示

### カードデザイン仕様
```css
.card {
  height: 100%;           /* 統一高さ */
  box-shadow: 0 2px 4px;  /* シャドウ効果 */
  transition: transform;   /* ホバー効果 */
}

.card:hover {
  transform: translateY(-2px);
}
```

## 🔧 技術仕様

### ファイル処理
```python
# CSV エンコーディング検出
def detect_encoding(file_content):
    encodings = ['utf-8', 'shift-jis', 'cp932', 'euc-jp']
    for encoding in encodings:
        try:
            file_content.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return 'utf-8'
```

### リスクレベル色分け
```javascript
function getRiskBadgeClass(level) {
    const classes = {
        1: 'bg-success',  // 緑 - 低リスク
        2: 'bg-info',     // 青 - やや低リスク
        3: 'bg-warning',  // 黄 - 中リスク
        4: 'bg-danger',   // 赤 - 高リスク
        5: 'bg-dark'      // 黒 - 最高リスク
    };
    return classes[level] || 'bg-secondary';
}
```

## 🚀 デプロイメント

### systemd設定
```ini
[Unit]
Description=ProductMaster System
After=network.target postgresql.service

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/ProductMaster
ExecStart=/usr/bin/python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 環境設定
```python
# config.py
DATABASE_URL = "postgresql://user:pass@localhost:5432/productmaster"
UPLOAD_DIR = "/tmp/uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.csv'}
```

## 📊 パフォーマンス

### 目標値
- **商品一覧表示**: < 200ms
- **CSV処理**: 1000件/秒
- **検索レスポンス**: < 100ms

### 最適化施策
```sql
-- インデックス設定
CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_products_type ON products(product_type);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_search ON products USING gin(to_tsvector('japanese', product_name));
```

## 🔒 セキュリティ

### ファイルアップロード対策
```python
# ファイル検証
def validate_csv_file(file):
    # ファイルサイズチェック
    if file.size > MAX_FILE_SIZE:
        raise ValueError("ファイルサイズが上限を超えています")
    
    # 拡張子チェック
    if not file.filename.endswith('.csv'):
        raise ValueError("CSVファイルのみ対応しています")
    
    # ウイルススキャン（将来実装）
    # scan_file_for_virus(file)
```

### SQL インジェクション対策
```python
# パラメータ化クエリ使用
def search_products(query: str):
    return session.query(Product).filter(
        Product.product_name.ilike(f"%{query}%")
    ).all()
```

## 🧪 テスト戦略

### テストケース
```python
# 商品検索テスト
def test_product_search():
    response = client.get("/api/products?search=トヨタ")
    assert response.status_code == 200
    assert len(response.json()["products"]) > 0

# CSV インポートテスト
def test_csv_import():
    with open("test_products.csv", "rb") as f:
        response = client.post("/api/import", files={"file": f})
    assert response.status_code == 200
```

## 📈 監視・運用

### ログ設定
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/productmaster.log'),
        logging.StreamHandler()
    ]
)
```

### メトリクス収集
- **API レスポンス時間**
- **CSV処理件数**
- **エラー発生率**
- **同時接続数**

## 🔄 今後の拡張計画

### 短期（1-3ヶ月）
- **商品比較機能**: 複数商品の並列比較
- **お気に入り機能**: ユーザー別商品ブックマーク
- **通知機能**: 商品更新・価格変動アラート

### 中期（3-6ヶ月）
- **バージョン管理**: 商品情報の履歴管理
- **承認ワークフロー**: 商品登録・更新の承認プロセス
- **API認証**: JWT トークン認証

### 長期（6ヶ月以降）
- **リアルタイム価格**: 外部API連携
- **機械学習**: 商品推奨アルゴリズム
- **GraphQL**: より柔軟なAPI提供

---

**Document Version**: v1.0.0  
**Repository**: https://github.com/takehig/ProductMaster-System  
**Last Updated**: 2025-09-05
