-- ProductMaster用サンプルデータ拡張

-- 日本企業社債
INSERT INTO products (product_code, product_name, product_type, currency, issuer, maturity_date, interest_rate, risk_level, minimum_investment, commission_rate, is_active, description) VALUES
('JP-TOYOTA-2027', 'トヨタ自動車第51回社債', 'bond', 'JPY', 'トヨタ自動車株式会社', '2027-03-15', 1.25, 2, 1000000.00, 0.50, true, '世界最大の自動車メーカーが発行する安定性の高い社債。ESG投資にも対応。'),
('JP-MITSUBISHI-2026', '三菱UFJ銀行第45回社債', 'bond', 'JPY', '株式会社三菱UFJ銀行', '2026-12-20', 0.85, 1, 500000.00, 0.30, true, '日本最大級のメガバンクが発行する超安全性社債。機関投資家にも人気。'),
('JP-NTT-2028', 'NTT第30回社債', 'bond', 'JPY', '日本電信電話株式会社', '2028-06-30', 1.55, 2, 1000000.00, 0.60, true, '通信インフラの最大手企業。5G・DX関連事業の成長期待。'),
('JP-KDDI-2027', 'KDDI第25回社債', 'bond', 'JPY', 'KDDI株式会社', '2027-09-15', 1.35, 2, 500000.00, 0.40, true, 'au・UQモバイルで知られる通信大手。安定したキャッシュフロー。'),

-- 米国企業社債
('US-APPLE-2029', 'Apple Inc. 2029年満期社債', 'bond', 'USD', 'Apple Inc.', '2029-01-15', 2.15, 2, 10000.00, 0.80, true, '世界最高時価総額企業。iPhone・Macの革新的技術で持続的成長。'),
('US-MSFT-2028', 'Microsoft 2028年満期社債', 'bond', 'USD', 'Microsoft Corporation', '2028-11-30', 1.95, 2, 10000.00, 0.70, true, 'クラウド・AI分野のリーディングカンパニー。Azure事業の急成長。'),
('US-GOOGL-2030', 'Alphabet 2030年満期社債', 'bond', 'USD', 'Alphabet Inc.', '2030-04-20', 2.35, 3, 15000.00, 0.90, true, 'Google検索・YouTube・クラウドを展開。AI技術の最先端企業。'),
('US-TESLA-2027', 'Tesla 2027年満期社債', 'bond', 'USD', 'Tesla Inc.', '2027-08-10', 3.25, 4, 20000.00, 1.20, true, '電気自動車・自動運転技術のパイオニア。高成長・高リスク銘柄。'),

-- 国債
('JGB-10Y-2034', '日本国債10年第400回', 'bond', 'JPY', '日本国', '2034-03-20', 0.55, 1, 100000.00, 0.10, true, '日本政府発行の10年満期国債。最高格付けの安全性。デフレ対策の一環。'),
('JGB-5Y-2029', '日本国債5年第250回', 'bond', 'JPY', '日本国', '2029-06-15', 0.35, 1, 100000.00, 0.10, true, '日本政府発行の5年満期国債。短期運用に適した安全資産。'),
('USB-10Y-2034', '米国債10年', 'bond', 'USD', '米国政府', '2034-05-15', 4.25, 1, 1000.00, 0.20, true, '米国政府発行の10年満期国債。世界基軸通貨建ての安全資産。'),
('USB-30Y-2054', '米国債30年', 'bond', 'USD', '米国政府', '2054-08-15', 4.55, 1, 1000.00, 0.30, true, '米国政府発行の30年満期国債。長期運用・年金基金に最適。'),

-- 投資信託
('MF-NIKKEI225', '日経225インデックスファンド', 'fund', 'JPY', '野村アセットマネジメント', NULL, NULL, 3, 10000.00, 1.00, true, '日経平均株価に連動するパッシブファンド。日本株式市場への分散投資。'),
('MF-SP500', 'S&P500インデックスファンド', 'fund', 'USD', 'バンガード', NULL, NULL, 3, 100.00, 0.80, true, '米国大型株500社に分散投資。世界最大の株式市場への投資。'),
('MF-EMERGING', '新興国株式ファンド', 'fund', 'JPY', '大和投資信託', NULL, NULL, 4, 10000.00, 1.50, true, 'アジア・南米等の新興国株式に投資。高成長期待・高リスク。'),
('MF-REIT', 'グローバルREITファンド', 'fund', 'JPY', '三井住友アセット', NULL, NULL, 3, 10000.00, 1.20, true, '世界各国の不動産投資信託に分散投資。インカムゲイン重視。'),

-- 株式
('STK-TOYOTA', 'トヨタ自動車株式', 'stock', 'JPY', 'トヨタ自動車株式会社', NULL, NULL, 3, 100.00, 0.30, true, '世界最大の自動車メーカー。ハイブリッド・水素技術のリーダー。'),
('STK-SOFTBANK', 'ソフトバンクグループ株式', 'stock', 'JPY', 'ソフトバンクグループ株式会社', NULL, NULL, 4, 100.00, 0.30, true, 'テクノロジー投資会社。AI・IoT分野への積極投資。'),
('STK-APPLE', 'Apple株式', 'stock', 'USD', 'Apple Inc.', NULL, NULL, 3, 1.00, 0.50, true, 'iPhone・Mac・iPadの革新的メーカー。サービス事業も拡大。'),
('STK-MICROSOFT', 'Microsoft株式', 'stock', 'USD', 'Microsoft Corporation', NULL, NULL, 3, 1.00, 0.50, true, 'Windows・Office・Azureの総合IT企業。AI分野でも先行。'),
('STK-NVIDIA', 'NVIDIA株式', 'stock', 'USD', 'NVIDIA Corporation', NULL, NULL, 4, 1.00, 0.50, true, 'GPU・AI半導体の世界的リーダー。生成AI ブームの恩恵銘柄。'),

-- 暗号資産・ETF
('ETF-BITCOIN', 'ビットコインETF', 'fund', 'USD', 'BlackRock', NULL, NULL, 5, 100.00, 0.75, true, 'ビットコインに連動するETF。暗号資産への間接投資が可能。'),
('ETF-GOLD', '金ETF', 'fund', 'USD', 'SPDR', NULL, NULL, 2, 100.00, 0.40, true, '金現物に連動するETF。インフレヘッジ・安全資産として人気。'),
('ETF-VIX', 'VIX指数ETF', 'fund', 'USD', 'ProShares', NULL, NULL, 5, 1000.00, 0.95, true, '恐怖指数に連動。市場の不安定期にヘッジ効果を発揮。');
