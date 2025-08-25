# ProductMaster System AWS デプロイ計画（修正版）

## 構成
- **既存EC2**: WealthAI CRM + ProductMaster System Webページ
- **新規RDS**: ProductMaster用 PostgreSQL データベース
- **API Gateway**: ProductMaster System REST API エンドポイント
- **既存EC2上の追加**: ProductMaster System バックエンド + Webページ

## デプロイ手順
1. RDS PostgreSQL作成（ProductMaster用）
2. 既存EC2にProductMaster Systemデプロイ
3. 既存EC2にProductMaster用Webページ追加
4. API Gateway設定（ProductMaster System用）
5. 動作確認

## エージェントから見た構成
- **CRMサービス**: http://EC2-IP:8000/ (顧客情報)
- **ProductMasterサービス**: API Gateway経由 (商品情報)
- **ProductMaster Webページ**: http://EC2-IP/products/ (管理画面)

作成日時: 2025-08-21 17:44 UTC
