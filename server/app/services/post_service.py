# ビジネスロジック層（サービス層）
# APIとデータベースの間に位置し、アプリケーションの中核的な処理を担当
# データの検証、ビジネスルールの実装などを行う

from typing import List, Dict
from app.db import repository  # データベース操作層


# 全ての投稿を取得する関数
async def get_all_posts() -> List[Dict]:
    """
    全ての投稿を取得する
    
    ビジネスロジック：
    - データベースから投稿一覧を取得
    
    戻り値: 投稿データの辞書のリスト
    """
    # リポジトリ層に処理を委譲（データアクセスの詳細は隙蔽）
    posts = await repository.get_all_posts()
    return posts


# 新しい投稿を作成する関数
async def create_post(text: str) -> Dict:
    """
    新しい投稿を作成する
    
    ビジネスルール：
    - 投稿内容は1文字以上255文字以内である必要がある
    - 空文字列や空白のみの投稿は許可しない
    
    引数:
        text: 投稿内容
        
    戻り値: 作成された投稿データ
    
    例外:
        ValueError: ビジネスルール違反時（文字数制限等）
    """
    # ビジネスルール検証：文字数制限チェック
    # API層でも検証されるが、サービス層でも二重チェック（防御的プログラミング）
    if not text or len(text) > 255:
        # ValueError: ビジネスロジック関連のエラー
        # API層でHTTPステータス400に変換される
        raise ValueError("Text must be between 1 and 255 characters")
    
    # データベースに投稿を保存
    post = await repository.create_post(text)
    return post