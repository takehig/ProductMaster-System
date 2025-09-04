#!/bin/bash

echo "=== サンプルデータ拡張開始 ==="

# PostgreSQLにサンプルデータを投入
sudo -u postgres psql -d productmaster -f /tmp/sample_data_expansion.sql

echo "=== データ件数確認 ==="

# 件数確認
sudo -u postgres psql -d productmaster -c "
SELECT 'products' as table_name, COUNT(*) as count FROM products 
UNION 
SELECT 'customers', COUNT(*) FROM customers 
UNION 
SELECT 'customer_holdings', COUNT(*) FROM customer_holdings
ORDER BY table_name;
"

echo "=== 商品種別別件数 ==="

sudo -u postgres psql -d productmaster -c "
SELECT product_type, COUNT(*) as count 
FROM products 
GROUP BY product_type 
ORDER BY count DESC;
"

echo "=== 顧客種別別件数 ==="

sudo -u postgres psql -d productmaster -c "
SELECT customer_type, COUNT(*) as count 
FROM customers 
GROUP BY customer_type 
ORDER BY count DESC;
"

echo "=== サンプルデータ拡張完了 ==="
