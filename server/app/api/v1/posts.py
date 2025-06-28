# FastAPI の必要なモジュールをインポート
from fastapi import APIRouter, HTTPException, Depends  # APIルーター、例外、依存性注入
from pydantic import BaseModel, Field                  # データモデル定義、バリデーション
from typing import List                                # 型ヒント（リスト型）
from datetime import datetime                          # 日時データ型
from app.api.deps import get_post_service_dep          # 依存性注入用の関数
from app.services.post_service import PostService      # ビジネスロジック層

# APIRouter: URL エンドポイントをグループ化するための仕組み
# このルーターに定義した関数が実際の API エンドポイントになる
router = APIRouter()


# Pydantic モデル：リクエストデータの構造とバリデーションルールを定義
class PostCreate(BaseModel):
    """投稿作成時に受け取るデータの形式を定義"""
    # Field(..., min_length=1, max_length=255)
    # ... : 必須フィールドであることを示す
    # min_length=1 : 最低1文字以上
    # max_length=255 : 最大255文字まで
    text: str = Field(..., min_length=1, max_length=255)


# Pydantic モデル：レスポンスデータの構造を定義
class PostResponse(BaseModel):
    """API レスポンスとして返す投稿データの形式を定義"""
    id: int                # 投稿ID
    text: str              # 投稿内容
    created_at: datetime   # 作成日時


# GET /posts エンドポイント：投稿一覧を取得
# @router.get() : HTTP GET メソッドでアクセス可能にするデコレータ
# response_model=List[PostResponse] : レスポンスの型を指定（PostResponse のリスト）
@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    # Depends() : 依存性注入の仕組み
    # post_service: PostService に get_post_service_dep() の結果が自動で渡される
    post_service: PostService = Depends(get_post_service_dep)
):
    """投稿一覧を取得する API エンドポイント"""
    # サービス層に処理を委譲（レイヤードアーキテクチャの実践）
    posts = await post_service.get_all_posts()
    return posts  # FastAPI が自動で JSON に変換してレスポンス


# POST /posts エンドポイント：新しい投稿を作成
@router.post("/posts", response_model=PostResponse)
async def create_post(
    # post_data: PostCreate で自動的にリクエストボディをバリデーション
    post_data: PostCreate,
    post_service: PostService = Depends(get_post_service_dep)
):
    """新しい投稿を作成する API エンドポイント"""
    try:
        # サービス層で投稿作成処理を実行
        post = await post_service.create_post(post_data.text)
        return post
    except ValueError as e:
        # ValueError（ビジネスロジックエラー）を HTTP 400 エラーに変換
        # HTTPException : FastAPI の例外クラス
        # status_code=400 : Bad Request（クライアントエラー）
        # detail : エラーメッセージ
        raise HTTPException(status_code=400, detail=str(e))