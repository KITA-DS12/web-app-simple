# データベース操作を担当するリポジトリクラス
# このファイルはデータベースとの実際の通信を行い、SQL クエリを実行する

# asyncpg: PostgreSQL 用の非同期データベースドライバー
import asyncpg
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.logging import setup_logger

logger = setup_logger(__name__)


class PostRepository:
    """
    投稿データの永続化を担当するリポジトリクラス
    データベース接続の管理と SQL クエリの実行を行う
    """
    
    def __init__(self):
        # コネクションプール: データベース接続を効率的に管理する仕組み
        # Optional[asyncpg.Pool] : None または asyncpg.Pool 型であることを示す型ヒント
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """
        データベース接続プールを作成する
        複数の接続を事前に作っておくことで、リクエストごとの接続コストを削減
        """
        self.pool = await asyncpg.create_pool(
            settings.DATABASE_URL,  # データベース接続文字列（設定ファイルから取得）
            min_size=1,             # 最小接続数（常に1つの接続を維持）
            max_size=10             # 最大接続数（同時に最大10個の接続を利用可能）
        )
        logger.info("Database connection pool created")

    async def disconnect(self):
        """
        データベース接続プールを正常に閉じる
        アプリケーション終了時にリソースを適切に解放するため
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def init_db(self):
        """
        データベーススキーマを初期化する
        テーブルが存在しない場合に schema.sql を実行してテーブルを作成
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        # schema.sql ファイルを読み込む
        with open("app/db/schema.sql", "r") as f:
            schema = f.read()
        
        # 接続プールから接続を取得してスキーマを実行
        # async with : 非同期コンテキストマネージャー（自動でリソースを解放）
        async with self.pool.acquire() as conn:
            await conn.execute(schema)
            logger.info("Database schema initialized")

    async def get_all_posts(self) -> List[Dict]:
        """
        全ての投稿を取得する
        戻り値: 投稿データの辞書のリスト
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            # fetch() : 複数行を取得する
            # ORDER BY id DESC : 新しい投稿から順に取得
            rows = await conn.fetch(
                "SELECT id, text, created_at FROM posts ORDER BY id DESC"
            )
            # asyncpg の Row オブジェクトを Python の辞書に変換
            return [dict(row) for row in rows]

    async def create_post(self, text: str) -> Dict:
        """
        新しい投稿を作成する
        引数: text - 投稿内容
        戻り値: 作成された投稿データの辞書
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            # fetchrow() : 1行だけを取得する
            # $1 : プレースホルダー（SQL インジェクション対策）
            # RETURNING : INSERT 後に作成されたデータを返す
            row = await conn.fetchrow(
                "INSERT INTO posts (text) VALUES ($1) RETURNING id, text, created_at",
                text  # プレースホルダー $1 に安全に値を渡す
            )
            return dict(row)


# リポジトリのシングルトンインスタンス
# アプリケーション全体で1つのインスタンスを共有する
post_repository = PostRepository()