// Vite 設定ファイル
// Vite は高速なフロントエンド開発ツール（ビルドツール）
// React アプリケーションの開発サーバー起動、ビルド、API プロキシ設定を行う

import { defineConfig } from 'vite'      // Vite 設定定義関数
import react from '@vitejs/plugin-react'  // React サポート用プラグイン

export default defineConfig({
  // プラグイン設定
  plugins: [react()],  // React の JSX、Hot Module Replacement (HMR) を有効化
  
  // 開発サーバー設定
  server: {
    port: 5173,  // 開発サーバーのポート番号（React アプリにアクセスするポート）
    
    // プロキシ設定：API リクエストをバックエンドサーバーに転送
    proxy: {
      '/api': {
        // '/api' で始まるリクエストを http://server:8000 に転送
        // 例: http://localhost:5173/api/v1/posts → http://server:8000/api/v1/posts
        target: 'http://server:8000',  // 転送先（Docker Compose のサービス名 'server'）
        changeOrigin: true            // Origin ヘッダーを転送先に合わせて変更（CORS 対策）
      }
    }
  },
  
  // ビルド設定（本番環境用）
  build: {
    outDir: 'dist'  // ビルド成果物の出力ディレクトリ
  }
})