# ビジネスロジック層（サービス層）
# APIとデータベースの間に位置し、アプリケーションの中核的な処理を担当
# データの検証、ビジネスルールの実装、ログ出力などを行う

from typing import List, Dict
from app.db.repository import post_repository  # データベース操作層
from app.core.logging import setup_logger

logger = setup_logger(__name__)


class PostService:
    """
    投稿に関するビジネスロジックを担当するサービスクラス
    
    レイヤードアーキテクチャにおけるサービス層の役割：
    - ビジネスルールの実装（データ検証、制約チェック）
    - 複数のリポジトリ操作の組み合わせ
    - ログ出力やメトリクス収集
    - エラーハンドリングとビジネス例外の生成
    """
    
    async def get_all_posts(self) -> List[Dict]:
        """
        全ての投稿を取得する
        
        ビジネスロジック：
        - データベースから投稿一覧を取得
        - 取得件数をログに記録（運用監視のため）
        
        戻り値: 投稿データの辞書のリスト
        """
        # リポジトリ層に処理を委譲（データアクセスの詳細は隠蔽）
        posts = await post_repository.get_all_posts()
        
        # ビジネス要件：取得件数をログに記録
        # 運用時のトラフィック監視や性能分析に活用
        logger.info(f"Retrieved {len(posts)} posts")
        
        return posts

    async def create_post(self, text: str) -> Dict:
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
        post = await post_repository.create_post(text)
        
        # ビジネス要件：投稿作成をログに記録
        # 監査ログやビジネス分析に活用
        logger.info(f"Created post with id: {post['id']}")
        
        return post


# サービスのシングルトンインスタンス
# 依存性注入によってAPIレイヤーに提供される
post_service = PostService()