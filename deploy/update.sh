#!/bin/bash

# ProductMaster EC2更新スクリプト
# EC2上で実行: ./deploy/update.sh

set -e

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# バックアップ作成
create_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    log_info "バックアップ作成中..."
    tar -czf "/home/ec2-user/ProductMaster_backup_${timestamp}.tar.gz" -C /home/ec2-user ProductMaster
    log_success "バックアップ作成完了: ProductMaster_backup_${timestamp}.tar.gz"
}

# Git更新
update_from_git() {
    log_info "GitHubから最新版を取得中..."
    cd /home/ec2-user/ProductMaster
    git fetch origin
    git reset --hard origin/main
    log_success "ソースコード更新完了"
}

# 依存関係更新
update_dependencies() {
    log_info "依存関係を確認中..."
    cd /home/ec2-user/ProductMaster
    if [ -f requirements.txt ]; then
        if pip install -r requirements.txt --quiet; then
            log_success "依存関係更新完了"
        else
            log_warning "依存関係更新でエラーが発生しましたが、続行します"
        fi
    fi
}

# サービス再起動
restart_service() {
    log_info "ProductMasterサービスを再起動中..."
    
    # 既存プロセス停止
    pkill -f "uvicorn.*8001" || true
    sleep 2
    
    # 新しいプロセス開始
    cd /home/ec2-user/ProductMaster/backend
    nohup python3 -m uvicorn fixed_main:app --host 0.0.0.0 --port 8001 > ../app.log 2>&1 &
    
    sleep 5
    log_success "ProductMasterサービス再起動完了"
}

# 動作確認
verify_service() {
    log_info "サービス動作確認中..."
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health | grep -q "200"; then
        log_success "ProductMaster正常動作確認"
    else
        log_error "ProductMaster動作確認に失敗"
        return 1
    fi
}

# メイン処理
main() {
    log_info "ProductMaster更新開始"
    
    create_backup
    update_from_git
    update_dependencies
    restart_service
    verify_service
    
    log_success "ProductMaster更新完了"
    log_info "アクセス: http://44.217.45.24/products/"
}

main "$@"
