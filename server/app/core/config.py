# アプリケーション設定管理ファイル
# 環境変数や設定値を一元管理し、開発・本番環境での切り替えを容易にする

import os
from pydantic_settings import BaseSettings  # Pydantic による設定管理


class Settings(BaseSettings):
    """
    アプリケーション設定クラス
    環境変数からの値読み込みと型検証を自動で行う
    """
    
    # データベース接続URL
    # 環境変数 DATABASE_URL が存在しない場合はデフォルト値を使用
    # デフォルト値は Docker Compose での設定に対応
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@db:5432/app"  # デフォルト：Docker Compose用
    )
    
    # API のベースパス
    # 全てのAPIエンドポイントに付加されるプレフィックス
    API_PREFIX: str = "/api/v1"
    
    # デバッグモードフラグ
    # 環境変数 DEBUG が "true" の場合のみ True になる
    # 詳細なログ出力や開発用機能の有効化に使用
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS 許可オリジンリスト
    # フロントエンドからのアクセスを許可するURL一覧
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite 開発サーバー（React）
        "http://localhost:8080"   # その他の開発用ポート
    ]

    class Config:
        """
        Pydantic Settings の設定クラス
        .env ファイルからの自動読み込みを有効化
        """
        env_file = ".env"  # .env ファイルが存在する場合、そこから環境変数を読み込む


# 設定のシングルトンインスタンス
# アプリケーション全体で同一の設定オブジェクトを共有
settings = Settings()