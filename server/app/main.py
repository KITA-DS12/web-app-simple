# FastAPI メインアプリケーションファイル
# このファイルはサーバーアプリケーションの全体的な設定と起動を担当する

# FastAPI の基本クラスとミドルウェアをインポート
from fastapi import FastAPI                      # Web API フレームワーク
from fastapi.middleware.cors import CORSMiddleware  # CORS (Cross-Origin Resource Sharing) 設定
from fastapi.staticfiles import StaticFiles     # 静的ファイル配信（HTML, CSS, JS など）
import os                                        # ファイルシステム操作
from contextlib import asynccontextmanager       # 非同期コンテキストマネージャー

# アプリケーション内のモジュールをインポート
from app.core.config import settings            # 設定管理
from app.core.logging import setup_logger       # ログ設定
from app.api.v1 import posts                    # 投稿関連 API ルーター
from app.db.repository import post_repository   # データベース操作

# ログ設定: このファイル用のロガーを初期化
logger = setup_logger(__name__)


# アプリケーションのライフサイクル管理
# @asynccontextmanager : 非同期での起動・停止処理を定義するデコレータ
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションの起動時と停止時の処理を定義
    起動時: データベース接続とテーブル初期化
    停止時: データベース接続を正常に切断
    """
    # アプリケーション起動時の処理
    await post_repository.connect()      # データベースに接続
    await post_repository.init_db()      # テーブルが存在しない場合は作成
    logger.info("Application startup complete")
    
    # yield : ここでアプリケーションが実行される（起動完了）
    yield
    
    # アプリケーション停止時の処理
    await post_repository.disconnect()   # データベース接続を安全に切断
    logger.info("Application shutdown complete")


# FastAPI アプリケーションインスタンスを作成
# lifespan=lifespan : 上で定義したライフサイクル管理を適用
app = FastAPI(lifespan=lifespan)

# CORS ミドルウェアの設定
# CORS : ブラウザのセキュリティ機能で、異なるオリジン間の通信を制御
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,    # 許可するオリジン（通常は React 開発サーバーのURL）
    allow_credentials=True,                  # 認証情報（Cookie）の送信を許可
    allow_methods=["*"],                     # 全ての HTTP メソッド（GET, POST, PUT, DELETE 等）を許可
    allow_headers=["*"],                     # 全ての HTTP ヘッダーを許可
)

# API ルーターを追加
# prefix=settings.API_PREFIX : 全ての API エンドポイントに /api/v1 のプレフィックスを追加
app.include_router(posts.router, prefix=settings.API_PREFIX)

# 静的ファイル配信の設定（本番環境用）
# /public ディレクトリが存在する場合、フロントエンドのビルド済みファイルを配信
if os.path.exists("/public"):
    # mount() : 特定のパスに静的ファイルサーバーを設定
    # html=True : index.html を自動的に返す（SPA 対応）
    app.mount("/", StaticFiles(directory="/public", html=True), name="static")


# ヘルスチェック用エンドポイント
# 運用環境でアプリケーションが正常に動作しているかを確認するため
@app.get("/health")
async def health_check():
    """アプリケーションの健全性を確認するエンドポイント"""
    return {"status": "healthy"}