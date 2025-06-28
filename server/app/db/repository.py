# データベース操作を担当するリポジトリクラス
# このファイルはデータベースとの実際の通信を行い、SQL クエリを実行する

# asyncpg: PostgreSQL 用の非同期データベースドライバー
import asyncpg
from typing import List, Dict
from app.core.config import settings


# データベース接続をシンプルに取得する関数
async def get_db_connection():
    """
    データベース接続を取得する
    使用するたびに新しい接続を作成するシンプルな方式
    """
    return await asyncpg.connect(settings.DATABASE_URL)


# データベース初期化関数
async def init_db():
    """
    データベーススキーマを初期化する
    テーブルが存在しない場合に schema.sql を実行してテーブルを作成
    """
    # schema.sql ファイルを読み込む
    with open("app/db/schema.sql", "r") as f:
        schema = f.read()
    
    # データベースに接続してスキーマを実行
    conn = await get_db_connection()
    try:
        await conn.execute(schema)
    finally:
        await conn.close()


# 投稿一覧を取得する関数
async def get_all_posts() -> List[Dict]:
    """
    全ての投稿を取得する
    戻り値: 投稿データの辞書のリスト
    """
    conn = await get_db_connection()
    try:
        # fetch() : 複数行を取得する
        # ORDER BY id DESC : 新しい投稿から順に取得
        rows = await conn.fetch(
            "SELECT id, text, created_at FROM posts ORDER BY id DESC"
        )
        # asyncpg の Row オブジェクトを Python の辞書に変換
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# 新しい投稿を作成する関数
async def create_post(text: str) -> Dict:
    """
    新しい投稿を作成する
    引数: text - 投稿内容
    戻り値: 作成された投稿データの辞書
    """
    conn = await get_db_connection()
    try:
        # fetchrow() : 1行だけを取得する
        # $1 : プレースホルダー（SQL インジェクション対策）
        # RETURNING : INSERT 後に作成されたデータを返す
        row = await conn.fetchrow(
            "INSERT INTO posts (text) VALUES ($1) RETURNING id, text, created_at",
            text  # プレースホルダー $1 に安全に値を渡す
        )
        return dict(row)
    finally:
        await conn.close()