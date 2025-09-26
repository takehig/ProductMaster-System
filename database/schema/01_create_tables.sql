-- ProductMaster System データベーススキーマ
-- 作成日: 2025-08-21

-- 1. 商品カテゴリテーブル
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER REFERENCES product_categories(category_id),
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 商品マスターテーブル（拡張版）
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_name_en VARCHAR(200),
    category_id INTEGER REFERENCES product_categories(category_id),
    currency VARCHAR(10) DEFAULT 'JPY',
    issuer VARCHAR(100),
    issuer_rating VARCHAR(10), -- AAA, AA+, AA, AA-, A+, A, A-, BBB+, etc.
    maturity_date DATE,
    interest_rate DECIMAL(5,4),
    coupon_frequency INTEGER, -- 年間クーポン支払回数
    risk_level INTEGER CHECK (risk_level BETWEEN 1 AND 5), -- 1-5
    minimum_investment BIGINT,
    investment_unit BIGINT DEFAULT 1,
    commission_rate DECIMAL(5,4),
    management_fee_rate DECIMAL(5,4),
    early_redemption_fee DECIMAL(5,4),
    description TEXT,
    features TEXT[], -- 商品の特徴（配列）
    target_customer_type VARCHAR(50), -- conservative, moderate, aggressive
    tax_treatment VARCHAR(50), -- 税制上の取扱い
    liquidity_level VARCHAR(20), -- high, medium, low
    benchmark_index VARCHAR(100),
    inception_date DATE,
    is_esg BOOLEAN DEFAULT FALSE, -- ESG投資対象かどうか
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 商品価格履歴テーブル
CREATE TABLE product_prices (
    price_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    price DECIMAL(15,2) NOT NULL,
    price_date DATE NOT NULL,
    price_time TIME,
    price_type VARCHAR(20) DEFAULT 'current', -- current, historical, projected, nav
    bid_price DECIMAL(15,2),
    ask_price DECIMAL(15,2),
    volume BIGINT,
    source VARCHAR(50), -- bloomberg, reuters, internal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, price_date, price_time, price_type)
);

-- 4. 商品パフォーマンステーブル
CREATE TABLE product_performance (
    performance_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    period_type VARCHAR(20) NOT NULL, -- 1d, 1w, 1m, 3m, 6m, 1y, 3y, 5y, ytd, inception
    return_rate DECIMAL(8,4), -- リターン率（%）
    volatility DECIMAL(8,4), -- ボラティリティ（%）
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    benchmark_return DECIMAL(8,4),
    alpha DECIMAL(8,4),
    beta DECIMAL(8,4),
    calculated_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, period_type, calculated_date)
);

-- 5. 商品ドキュメントテーブル
CREATE TABLE product_documents (
    document_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    document_type VARCHAR(50) NOT NULL, -- prospectus, fact_sheet, annual_report, monthly_report
    document_name VARCHAR(200) NOT NULL,
    file_path VARCHAR(500),
    file_url VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    language VARCHAR(10) DEFAULT 'ja',
    publish_date DATE,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 商品関連商品テーブル（類似商品・代替商品）
CREATE TABLE product_relationships (
    relationship_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    related_product_id INTEGER REFERENCES products(product_id),
    relationship_type VARCHAR(30) NOT NULL, -- similar, alternative, underlying, derivative
    relationship_strength DECIMAL(3,2), -- 0.00-1.00の関連度
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, related_product_id, relationship_type)
);

-- 7. 商品タグテーブル
CREATE TABLE product_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL,
    tag_color VARCHAR(7), -- HEXカラーコード
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 商品タグ関連テーブル
CREATE TABLE product_tag_relations (
    product_id INTEGER REFERENCES products(product_id),
    tag_id INTEGER REFERENCES product_tags(tag_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, tag_id)
);

-- インデックスの作成
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_issuer ON products(issuer);
CREATE INDEX idx_products_maturity ON products(maturity_date) WHERE maturity_date IS NOT NULL;
CREATE INDEX idx_products_risk_level ON products(risk_level);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_product_prices_date ON product_prices(product_id, price_date DESC);
CREATE INDEX idx_product_performance_period ON product_performance(product_id, period_type);
CREATE INDEX idx_product_documents_type ON product_documents(product_id, document_type);

-- 全文検索用インデックス（PostgreSQL）
CREATE INDEX idx_products_search ON products USING gin(to_tsvector('japanese', product_name || ' ' || COALESCE(description, '')));

-- 外部キー制約の確認
ALTER TABLE products ADD CONSTRAINT chk_products_dates 
    CHECK (maturity_date IS NULL OR maturity_date > inception_date);

ALTER TABLE product_relationships ADD CONSTRAINT chk_no_self_reference 
    CHECK (product_id != related_product_id);
