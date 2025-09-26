-- ProductMaster System サンプルデータ
-- 作成日: 2025-08-21

-- 商品カテゴリのサンプルデータ
INSERT INTO product_categories (category_code, category_name, description, display_order) VALUES
('BOND', '債券', '国債、社債、地方債等の債券商品', 1),
('STOCK', '株式', '国内外の株式商品', 2),
('FUND', '投資信託', 'アクティブ・パッシブファンド', 3),
('STRUCT', '仕組み商品', 'デリバティブを組み込んだ商品', 4),
('INSURANCE', '保険', '変額保険、外貨建て保険等', 5),
('REIT', 'REIT', '不動産投資信託', 6),
('COMMODITY', 'コモディティ', '金、原油等の商品', 7);

-- 株式詳細カテゴリ（フラット構造）
INSERT INTO product_categories (category_code, category_name, description, display_order) VALUES
('STOCK_DOM', '国内株式', '日本株式', 11),
('STOCK_US', '米国株式', '米国株式', 12),
('STOCK_INTL', '国際株式', '新興国等の株式', 13);

-- 商品マスターのサンプルデータ
INSERT INTO products (
    product_code, product_name, product_name_en, product_type, category_id,
    currency, issuer, issuer_rating, maturity_date, interest_rate,
    risk_level, minimum_investment, commission_rate, description,
    features, target_customer_type, inception_date, is_active
) VALUES
-- 債券商品
('JGB10Y-2024', '第394回10年国債', 'JGB 10Y Series 394', 'bond', 8,
 'JPY', '日本国', 'A+', '2034-12-20', 0.0075,
 1, 10000, 0.0000, '日本国が発行する10年満期の国債。安全性が高く、安定した利回りが期待できます。',
 ARRAY['元本保証', '半年毎利払い', '流動性高'], 'conservative', '2024-12-20', true),

('TOYOTA-2029', 'トヨタ自動車第50回社債', 'Toyota Motor Corp Bond 50th', 'bond', 9,
 'JPY', 'トヨタ自動車', 'AA-', '2029-03-15', 0.0125,
 2, 100000, 0.0050, 'トヨタ自動車が発行する5年満期の無担保社債。優良企業による安定した投資機会。',
 ARRAY['年2回利払い', '無担保', '格付AA-'], 'conservative', '2024-03-15', true),

('APPLE-USD-2030', 'Apple Inc. 社債 2030年満期', 'Apple Inc. Corporate Bond 2030', 'bond', 9,
 'USD', 'Apple Inc.', 'AAA', '2030-05-01', 0.0275,
 2, 1000, 0.0075, 'Apple社が発行するドル建て社債。世界最高格付けの安全性と魅力的な利回り。',
 ARRAY['ドル建て', '年2回利払い', '格付AAA'], 'moderate', '2025-05-01', true),

-- 株式商品  
('7203', 'トヨタ自動車', 'Toyota Motor Corporation', 'stock', 11,
 'JPY', 'トヨタ自動車', NULL, NULL, NULL,
 3, 100, 0.0125, '世界最大級の自動車メーカー。ハイブリッド技術のリーディングカンパニー。',
 ARRAY['自動車', '配当利回り2.5%', 'ESG'], 'moderate', NULL, true),

('AAPL', 'Apple Inc.', 'Apple Inc.', 'stock', 12,
 'USD', 'Apple Inc.', NULL, NULL, NULL,
 3, 1, 0.0150, '世界最大のテクノロジー企業。iPhone、Mac等の革新的製品を展開。',
 ARRAY['テクノロジー', '成長株', 'NASDAQ'], 'moderate', NULL, true),

-- 投資信託
('NIKKEI225-INDEX', '日経225インデックスファンド', 'Nikkei 225 Index Fund', 'fund', 3,
 'JPY', 'ABC投信', NULL, NULL, NULL,
 3, 10000, 0.0050, '日経平均株価に連動するパッシブファンド。低コストで日本株式市場に投資。',
 ARRAY['インデックス', '信託報酬0.15%', 'パッシブ'], 'moderate', '2020-01-01', true),

('GLOBAL-GROWTH', 'グローバル成長株ファンド', 'Global Growth Equity Fund', 'fund', 3,
 'JPY', 'XYZ投信', NULL, NULL, NULL,
 4, 10000, 0.0100, '世界の成長企業に投資するアクティブファンド。長期的な資産成長を目指します。',
 ARRAY['アクティブ', '信託報酬1.65%', '世界株式'], 'aggressive', '2019-06-01', true),

-- 仕組み商品
('EB-NIKKEI-2026', '日経平均リンク債', 'Nikkei 225 Linked Note', 'structured_product', 4,
 'JPY', 'DEF証券', 'A', '2026-12-15', 0.0000,
 4, 1000000, 0.0200, '日経平均の値動きに連動する仕組み債。元本保証付きで株式市場の上昇に参加。',
 ARRAY['元本保証', '日経平均連動', '満期3年'], 'moderate', '2023-12-15', true),

-- REIT
('J-REIT-INDEX', 'J-REITインデックスファンド', 'J-REIT Index Fund', 'fund', 6,
 'JPY', 'GHI投信', NULL, NULL, NULL,
 3, 10000, 0.0030, '東証REIT指数に連動するファンド。不動産投資による安定した分配金収入。',
 ARRAY['REIT', '分配金利回り4%', 'インデックス'], 'moderate', '2021-03-01', true),

-- ESG投資
('ESG-GLOBAL', 'ESGグローバル株式ファンド', 'ESG Global Equity Fund', 'fund', 3,
 'JPY', 'JKL投信', NULL, NULL, NULL,
 3, 10000, 0.0120, 'ESG基準を満たす世界の企業に投資。持続可能な社会の実現と投資リターンの両立。',
 ARRAY['ESG投資', 'SRI', '世界株式'], 'moderate', '2022-04-01', true);

-- 商品価格のサンプルデータ
INSERT INTO product_prices (product_id, price, price_date, price_type, source) VALUES
-- 債券価格（額面100に対する価格）
(1, 99.85, '2025-08-20', 'current', 'bloomberg'),
(2, 101.25, '2025-08-20', 'current', 'bloomberg'),
(3, 98.75, '2025-08-20', 'current', 'bloomberg'),

-- 株式価格
(4, 2850.00, '2025-08-20', 'current', 'tokyo_exchange'),
(5, 185.50, '2025-08-20', 'current', 'nasdaq'),

-- 投資信託基準価額
(6, 15420, '2025-08-20', 'nav', 'fund_company'),
(7, 18750, '2025-08-20', 'nav', 'fund_company'),

-- 仕組み商品
(8, 100.00, '2025-08-20', 'current', 'issuer'),

-- REIT
(9, 12580, '2025-08-20', 'nav', 'fund_company'),

-- ESG
(10, 11250, '2025-08-20', 'nav', 'fund_company');

-- 商品パフォーマンスのサンプルデータ
INSERT INTO product_performance (product_id, period_type, return_rate, volatility, calculated_date) VALUES
-- 1年リターン
(4, '1y', 8.5, 18.2, '2025-08-20'),
(5, '1y', 12.3, 22.1, '2025-08-20'),
(6, '1y', 15.2, 16.8, '2025-08-20'),
(7, '1y', 22.1, 24.5, '2025-08-20'),

-- 3年リターン（年率）
(4, '3y', 6.8, 19.1, '2025-08-20'),
(5, '3y', 18.5, 25.3, '2025-08-20'),
(6, '3y', 12.4, 17.2, '2025-08-20'),
(7, '3y', 15.8, 23.8, '2025-08-20');
