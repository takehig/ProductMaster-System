        // CSVダウンロード機能（エンコーディング対応版）
        async function downloadCSV(encoding = 'utf-8-sig') {
            try {
                // 現在のフィルター条件を取得
                const typeFilter = document.getElementById('typeFilter').value;
                const params = new URLSearchParams();
                
                if (typeFilter) {
                    params.append('product_type', typeFilter);
                }
                
                // エンコーディングパラメータを追加
                params.append('encoding', encoding);
                
                const url = `${API_BASE}/products/download-csv?${params.toString()}`;
                
                // ダウンロード用のリンクを作成
                const response = await fetch(url, { headers });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    
                    // ファイル名を取得（Content-Dispositionヘッダーから）
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'products.csv';
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                        if (filenameMatch) {
                            filename = filenameMatch[1];
                        }
                    }
                    
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(downloadUrl);
                    
                    // 成功メッセージ
                    const encodingName = {
                        'utf-8-sig': 'UTF-8 BOM付き（Excel推奨）',
                        'shift_jis': 'Shift_JIS（日本語Windows）',
                        'utf-8': 'UTF-8（標準）'
                    }[encoding] || encoding;
                    
                    showNotification(`CSVファイルをダウンロードしました（${encodingName}）`, 'success');
                } else {
                    throw new Error('ダウンロードに失敗しました');
                }
            } catch (error) {
                console.error('CSVダウンロードエラー:', error);
                showNotification('CSVファイルのダウンロードに失敗しました', 'error');
            }
        }

        // エンコーディング選択モーダルを表示
        function showEncodingModal() {
            const modal = new bootstrap.Modal(document.getElementById('encodingModal'));
            modal.show();
        }

        // 通知表示機能
        function showNotification(message, type = 'success') {
            const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
            const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
            
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            alertDiv.innerHTML = `
                <i class="fas ${icon}"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alertDiv);
            
            // 5秒後に自動で消す
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 5000);
        }
