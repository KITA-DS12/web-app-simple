# FastAPI メインアプリケーションファイル
# このファイルはサーバーアプリケーションの全体的な設定と起動を担当する

# FastAPI の基本クラスとミドルウェアをインポート
from fastapi import FastAPI                      # Web API フレームワーク
from fastapi.middleware.cors import CORSMiddleware  # CORS (Cross-Origin Resource Sharing) 設定

# アプリケーション内のモジュールをインポート
from app.core.config import settings            # 設定管理
from app.api.v1 import posts                    # 投稿関連 API ルーター


# FastAPI アプリケーションインスタンスを作成
app = FastAPI()

# CORS ミドルウェアの設定
# CORS : ブラウザのセキュリティ機能で、異なるオリジン間の通信を制御
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,    # 許可するオリジン（通常は React 開発サーバーのURL）
    allow_credentials=True,                  # 認証情報（Cookie）の送信を許可
    allow_methods=["*"],                     # 全ての HTTP メソッド（GET, POST, PUT, DELETE 等）を許可
    allow_headers=["*"],                     # 全ての HTTP ヘッダーを許可
)

# アプリケーション起動時の初期化処理
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にデータベースを初期化"""
    await posts.startup()

# API ルーターを追加
# prefix=settings.API_PREFIX : 全ての API エンドポイントに /api/v1 のプレフィックスを追加
app.include_router(posts.router, prefix=settings.API_PREFIX)