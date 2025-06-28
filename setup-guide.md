# 🚀 FastAPI + React + PostgreSQL アプリを0から構築するガイド

> **目標**: シンプルな投稿アプリを段階的に作成し、Web開発の基本を実践的に学ぶ

---

## 📋 このガイドで作るもの

**機能:**
- 投稿の一覧表示
- 新しい投稿の作成
- 投稿の削除（演習）

**技術スタック:**
- **フロントエンド**: React 18 + Vite
- **バックエンド**: FastAPI (Python)
- **データベース**: PostgreSQL
- **開発環境**: Docker + Docker Compose

**プロジェクト構造:**
```
web-app-simple/
├── client/          # React フロントエンド
├── server/          # FastAPI バックエンド
├── infra/           # Docker設定
└── docs/            # ドキュメント
```

---

## 🛠️ 事前準備

### 必要なツール（Mac向け）

```bash
# 1. Homebrew がインストール済みかチェック
brew --version

# 未インストールの場合
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Docker Desktop のインストール
brew install --cask docker

# 3. Git のインストール（通常は既にインストール済み）
brew install git

# 4. VS Code のインストール（推奨）
brew install --cask visual-studio-code
```

### 開発環境の確認

```bash
# バージョン確認
docker --version          # 例: Docker version 24.0.0
docker-compose --version  # 例: docker-compose version 2.20.0
git --version             # 例: git version 2.40.0
```

---

## 📁 1. プロジェクト構造の作成

### 1.1 基本ディレクトリ構造

```bash
# プロジェクトディレクトリ作成
mkdir web-app-simple
cd web-app-simple

# サブディレクトリ作成
mkdir client server infra docs

# 確認
tree . # または ls -la
```

期待される構造:
```
web-app-simple/
├── client/
├── server/
├── infra/
└── docs/
```

### 1.2 Git リポジトリの初期化

```bash
# Git リポジトリ初期化
git init

# .gitignore ファイル作成
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
.pytest_cache/

# Environment
.env
.env.local
.env.*.local

# Build outputs
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
EOF

# 初期コミット
git add .
git commit -m "feat: 初期プロジェクト構造を作成

- client/, server/, infra/, docs/ ディレクトリを作成
- .gitignore を設定
"
```

---

## 🗄️ 2. データベース設計

### 2.1 スキーマ設計

```bash
# データベーススキーマディレクトリ作成
mkdir -p server/app/db
```

**ファイル作成**: `server/app/db/schema.sql`

```sql
-- posts テーブル：投稿データを保存するためのテーブル定義
-- このSQLファイルはアプリケーション起動時に実行され、必要なテーブルを作成します

CREATE TABLE IF NOT EXISTS posts (
    -- id: 投稿の一意識別子
    -- SERIAL: PostgreSQL の自動増分型（1, 2, 3... と自動で番号が振られる）
    -- PRIMARY KEY: 主キー（テーブル内で重複しない一意な値）
    id SERIAL PRIMARY KEY,
    
    -- text: 投稿の内容
    -- VARCHAR(255): 可変長文字列、最大255文字まで
    -- NOT NULL: 空の値（NULL）を許可しない
    text VARCHAR(255) NOT NULL,
    
    -- created_at: 投稿の作成日時
    -- TIMESTAMP: 日付と時刻を保存するデータ型
    -- DEFAULT CURRENT_TIMESTAMP: レコード作成時に現在時刻を自動設定
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 ER図（概念設計）

```mermaid
erDiagram
    POSTS {
        int id PK "主キー・自動増分"
        varchar text "投稿内容・最大255文字"
        timestamp created_at "作成日時・自動設定"
    }
```

---

## ⚙️ 3. バックエンド（FastAPI）の構築

### 3.1 ディレクトリ構造

```bash
# バックエンドの詳細構造作成
mkdir -p server/app/{core,api/v1,services,db}
```

### 3.2 依存関係の定義

**ファイル作成**: `server/requirements.txt`

```txt
fastapi==0.109.0
uvicorn[standard]==0.25.0
asyncpg==0.29.0
pydantic==2.5.3
pydantic-settings==2.1.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

### 3.3 設定管理

**ファイル作成**: `server/app/core/config.py`

```python
# アプリケーション全体の設定を管理するモジュール
# 環境変数から設定値を読み込み、型安全な設定オブジェクトを提供

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    アプリケーション設定クラス
    環境変数から自動的に値を読み込む（大文字小文字は区別しない）
    """
    
    # データベース接続URL
    # 環境変数 DATABASE_URL から読み込まれる
    # 例: postgresql://user:password@localhost:5432/dbname
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/app"
    
    # API のベースパス（バージョニング用）
    API_PREFIX: str = "/api/v1"
    
    # CORS（Cross-Origin Resource Sharing）設定
    # フロントエンドからのAPIアクセスを許可するオリジンのリスト
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]  # Vite開発サーバーのデフォルトポート
    
    # デバッグモード（開発時のみ true）
    DEBUG: bool = True

# グローバル設定インスタンス
# 他のモジュールでこれをインポートして使用する
settings = Settings()
```

### 3.4 データベース操作層（Repository）

**ファイル作成**: `server/app/db/repository.py`

```python
# データベース操作を担当するリポジトリ層
# SQLの実行とPythonオブジェクトへの変換を行う

import asyncpg
from typing import List, Dict
from app.core.config import settings

async def get_db_connection():
    """
    データベース接続を取得する関数
    アプリケーション全体でこの関数を使用してDB接続を統一管理
    """
    return await asyncpg.connect(settings.DATABASE_URL)

async def init_db():
    """
    データベース初期化関数
    アプリケーション起動時にテーブルを作成する
    """
    # スキーマファイルを読み込む
    with open("app/db/schema.sql", "r") as f:
        schema = f.read()
    
    # データベースに接続してスキーマを実行
    conn = await get_db_connection()
    try:
        await conn.execute(schema)
        print("✅ データベーステーブルが正常に作成されました")
    finally:
        # 接続を確実に閉じる（リソースリーク防止）
        await conn.close()

async def get_all_posts() -> List[Dict]:
    """
    すべての投稿を取得する関数
    
    Returns:
        List[Dict]: 投稿データのリスト
                   [{"id": 1, "text": "投稿内容", "created_at": "2024-01-01T12:00:00"}, ...]
    """
    conn = await get_db_connection()
    try:
        # SQL実行：IDの降順（新しい投稿が上に表示される）
        rows = await conn.fetch(
            "SELECT id, text, created_at FROM posts ORDER BY id DESC"
        )
        # asyncpg の Row オブジェクトを辞書に変換
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def create_post(text: str) -> Dict:
    """
    新しい投稿を作成する関数
    
    Args:
        text (str): 投稿内容
        
    Returns:
        Dict: 作成された投稿データ
              {"id": 1, "text": "投稿内容", "created_at": "2024-01-01T12:00:00"}
    """
    conn = await get_db_connection()
    try:
        # SQL実行：INSERTとRETURNINGを同時に行い、作成されたレコードを取得
        row = await conn.fetchrow(
            "INSERT INTO posts (text) VALUES ($1) RETURNING id, text, created_at",
            text
        )
        return dict(row)
    finally:
        await conn.close()
```

### 3.5 ビジネスロジック層（Service）

**ファイル作成**: `server/app/services/post_service.py`

```python
# ビジネスロジック（アプリケーションのルール）を担当するサービス層
# データの検証や加工、複雑な処理ルールをここに実装

from typing import List, Dict
from app.db import repository

async def get_all_posts() -> List[Dict]:
    """
    すべての投稿を取得するビジネスロジック
    現在はリポジトリをそのまま呼び出すだけだが、
    将来的に投稿の並び順変更やフィルタリングなどを追加可能
    """
    posts = await repository.get_all_posts()
    return posts

async def create_post(text: str) -> Dict:
    """
    新しい投稿を作成するビジネスロジック
    投稿内容のバリデーション（検証）を行う
    
    Args:
        text (str): 投稿内容
        
    Returns:
        Dict: 作成された投稿データ
        
    Raises:
        ValueError: バリデーションエラー時
    """
    # ビジネスルール1: 投稿内容が空でないことを確認
    if not text or len(text) == 0:
        raise ValueError("投稿内容を入力してください")
    
    # ビジネスルール2: 文字数制限（255文字以内）
    if len(text) > 255:
        raise ValueError("投稿は255文字以内で入力してください")
    
    # ビジネスルール3: 前後の空白を除去
    text = text.strip()
    
    # 検証が通った場合のみデータベースに保存
    post = await repository.create_post(text)
    return post
```

### 3.6 API層（FastAPI）

**ファイル作成**: `server/app/api/v1/posts.py`

```python
# HTTP API エンドポイントを定義するAPIルート層
# HTTPリクエスト/レスポンスの処理とビジネスロジックを繋ぐ

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.services import post_service
from app.db import repository

# APIルーターインスタンス（エンドポイントをグループ化）
router = APIRouter()

# Pydantic モデル：リクエスト/レスポンスデータの型定義

class PostCreate(BaseModel):
    """投稿作成時のリクエストボディの型定義"""
    text: str = Field(..., min_length=1, max_length=255, description="投稿内容")

class PostResponse(BaseModel):
    """投稿データのレスポンス型定義"""
    id: int
    text: str
    created_at: datetime

# データベース初期化関数（アプリ起動時に呼ばれる）
async def startup():
    """アプリケーション起動時の初期化処理"""
    await repository.init_db()

# API エンドポイント定義

@router.get("/posts", response_model=List[PostResponse], summary="投稿一覧取得")
async def get_posts():
    """
    投稿一覧を取得するエンドポイント
    
    Returns:
        List[PostResponse]: 投稿データのリスト（新しい順）
    """
    try:
        posts = await post_service.get_all_posts()
        return posts
    except Exception as e:
        # 予期しないエラーの場合は500エラーを返す
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")

@router.post("/posts", response_model=PostResponse, summary="新規投稿作成")
async def create_post(post_data: PostCreate):
    """
    新しい投稿を作成するエンドポイント
    
    Args:
        post_data (PostCreate): 投稿作成データ
        
    Returns:
        PostResponse: 作成された投稿データ
    """
    try:
        post = await post_service.create_post(post_data.text)
        return post
    except ValueError as e:
        # バリデーションエラーの場合は400エラーを返す
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他のエラーの場合は500エラーを返す
        raise HTTPException(status_code=500, detail=f"投稿作成エラー: {str(e)}")
```

### 3.7 メインアプリケーション

**ファイル作成**: `server/app/main.py`

```python
# FastAPI アプリケーションのエントリーポイント
# アプリケーションの設定とルーターの登録を行う

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import posts

# FastAPI アプリケーションインスタンス作成
app = FastAPI(
    title="投稿アプリAPI",
    description="シンプルな投稿機能を持つWeb APIサーバー",
    version="1.0.0"
)

# CORS ミドルウェア設定
# フロントエンド（React）からのアクセスを許可するため
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 許可するオリジン
    allow_credentials=True,                # 認証情報の送信を許可
    allow_methods=["*"],                   # すべてのHTTPメソッドを許可
    allow_headers=["*"],                   # すべてのHTTPヘッダーを許可
)

# アプリケーション起動時の処理
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にデータベースを初期化"""
    await posts.startup()

# APIルーターを登録
# /api/v1/posts のパスで投稿関連APIにアクセス可能
app.include_router(posts.router, prefix=settings.API_PREFIX)

# ルートエンドポイント（動作確認用）
@app.get("/", summary="ヘルスチェック")
async def root():
    """アプリケーションの動作確認用エンドポイント"""
    return {"message": "投稿アプリAPI が正常に動作しています", "version": "1.0.0"}
```

### 3.8 バックエンド用Dockerfile

**ファイル作成**: `server/Dockerfile.dev`

```dockerfile
# Python 3.11 の軽量版イメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# Python の設定
# PYTHONUNBUFFERED: 出力のバッファリングを無効化（ログが即座に表示される）
# PYTHONDONTWRITEBYTECODE: .pyc ファイルの生成を無効化
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# 開発サーバーを起動（ホットリロード有効）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## 🎨 4. フロントエンド（React）の構築

### 4.1 React プロジェクトのセットアップ

```bash
# client ディレクトリに移動
cd client

# Vite を使って React プロジェクトを作成
npm create vite@latest . -- --template react

# 依存関係をインストール
npm install

# 開発サーバーが起動することを確認（一旦テスト）
npm run dev
# Ctrl+C で停止

# client ディレクトリから抜ける
cd ..
```

**生成された package.json を確認:**

```json
{
  "name": "fastapi-react-client",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

### 4.2 Vite 設定の修正

**ファイル編集**: `client/vite.config.js`（既存ファイルを以下に置き換え）

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite 設定ファイル
// 開発サーバーの設定とAPIプロキシの設定
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Docker コンテナ内からアクセス可能にする
    port: 5173,       // 開発サーバーのポート
    // API プロキシ設定：/api/v1 へのリクエストをバックエンドに転送
    proxy: {
      '/api/v1': {
        target: 'http://server:8000',  // Docker Compose のサービス名で指定
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

### 4.3 HTML エントリーポイントの修正

**ファイル編集**: `client/index.html`（既存ファイルを以下に置き換え）

```html
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>投稿アプリ - FastAPI + React</title>
  </head>
  <body>
    <!-- React アプリがマウントされるコンテナ -->
    <div id="root"></div>
    <!-- React アプリのエントリーポイント -->
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### 4.4 React エントリーポイントの修正

**ファイル編集**: `client/src/main.jsx`（既存ファイルを以下に置き換え）

```javascript
// React アプリケーションのエントリーポイント
// HTMLの #root 要素に React アプリをマウントする

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// React 18 の新しい API で React アプリを初期化
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 4.5 API通信層

**ディレクトリ作成**: `client/src/api/`

**ファイル作成**: `client/src/api/posts.js`

```javascript
// API 通信を担当するモジュール
// バックエンドとの HTTP 通信を抽象化

// API のベース URL を定数として定義
// '/api/v1' は vite.config.js でプロキシ設定により http://server:8000/api/v1 に転送される
const API_BASE = '/api/v1';

// 投稿関連の API 通信を行う関数をまとめたオブジェクト
export const postsApi = {
  // 投稿一覧を取得する関数（HTTP GET リクエスト）
  async getAll() {
    // fetch() : ブラウザ標準の HTTP 通信機能
    // テンプレートリテラル（``）を使って URL を構築: /api/v1/posts
    const response = await fetch(`${API_BASE}/posts`);
    
    // response.ok : HTTP ステータスコードが 200-299 の範囲かチェック
    if (!response.ok) {
      // エラー時は Error オブジェクトを投げる（throw）
      // これにより呼び出し元の catch ブロックでエラーをキャッチできる
      throw new Error('Failed to fetch posts');
    }
    
    // response.json() : レスポンスの JSON データを JavaScript オブジェクトに変換
    return response.json();
  },

  // 新しい投稿を作成する関数（HTTP POST リクエスト）
  async create(text) {
    const response = await fetch(`${API_BASE}/posts`, {
      method: 'POST',  // HTTP メソッドを POST に指定
      
      // HTTP ヘッダー：サーバーにリクエストの詳細情報を伝える
      headers: {
        'Content-Type': 'application/json',  // JSON 形式でデータを送信することを明示
      },
      
      // リクエストボディ：サーバーに送信するデータ
      // JSON.stringify() : JavaScript オブジェクトを JSON 文字列に変換
      // { text } は { text: text } の省略記法（ES6 のプロパティ短縮記法）
      body: JSON.stringify({ text }),
    });
    
    // レスポンスのエラーチェック
    if (!response.ok) {
      // サーバーからのエラーレスポンスを JSON として取得
      const error = await response.json();
      
      // error.detail があればそれを、なければデフォルトメッセージを使用
      // || 演算子：左側が falsy（undefined, null, '' など）なら右側を使用
      throw new Error(error.detail || 'Failed to create post');
    }
    
    // 成功時は作成された投稿データを JSON として返す
    return response.json();
  }
};
```

### 4.6 カスタムフック（状態管理）

**ディレクトリ作成**: `client/src/hooks/`

**ファイル作成**: `client/src/hooks/usePosts.js`

```javascript
// 投稿データの状態管理を行うカスタムフック
// React の状態管理ロジックを再利用可能な形で分離

import { useState, useEffect } from 'react';
import { postsApi } from '../api/posts';

export function usePosts() {
  // useState: React の状態管理フック
  // [現在の値, 値を更新する関数] = useState(初期値)
  const [posts, setPosts] = useState([]);           // 投稿データの配列
  const [loading, setLoading] = useState(true);     // データ読み込み中フラグ
  const [error, setError] = useState('');           // エラーメッセージ

  // 投稿データを取得する関数
  const fetchPosts = async () => {
    try {
      setLoading(true);   // 読み込み開始
      setError('');       // 前回のエラーをクリア
      
      // API から投稿データを取得
      const data = await postsApi.getAll();
      setPosts(data);     // 取得したデータで状態を更新
    } catch (err) {
      // エラーが発生した場合
      setError('投稿の取得に失敗しました: ' + err.message);
      setPosts([]);       // 投稿データをクリア
    } finally {
      setLoading(false);  // 読み込み完了
    }
  };

  // useEffect: 副作用（APIコール等）を管理するフック
  // 第2引数が空配列 [] の場合、コンポーネントの初回レンダリング時のみ実行
  useEffect(() => {
    fetchPosts();  // 初回レンダリング時に投稿データを取得
  }, []);

  // 新しい投稿を作成する関数
  const createPost = async (text) => {
    try {
      // API で新しい投稿を作成
      const newPost = await postsApi.create(text);
      
      // 作成された投稿を現在の投稿リストの先頭に追加
      // スプレッド構文（...）を使用して既存の配列をコピーし、新しい要素を追加
      setPosts(prevPosts => [newPost, ...prevPosts]);
      
      // 成功を示すオブジェクトを返す
      return { success: true };
    } catch (err) {
      // エラーが発生した場合、エラー情報を返す
      return { success: false, error: err.message };
    }
  };

  // カスタムフックが返すオブジェクト
  // 他のコンポーネントでこれらの値と関数を使用可能
  return {
    posts,        // 投稿データの配列
    loading,      // 読み込み中フラグ
    error,        // エラーメッセージ
    createPost,   // 投稿作成関数
    refetch: fetchPosts  // 手動でデータを再取得する関数
  };
}
```

### 4.7 UIコンポーネント

**ディレクトリ作成**: `client/src/components/`

**ファイル作成**: `client/src/components/PostList.jsx`

```javascript
// 投稿一覧と投稿作成フォームを表示するUIコンポーネント
// React の useState フックをインポート（コンポーネント内でデータの状態を管理するため）
import { useState } from 'react';

// PostList コンポーネント：投稿の一覧表示と新規投稿作成機能を担当
// props（引数）として親コンポーネント（App.jsx）から以下のデータを受け取る
export function PostList({ posts, loading, error, onCreatePost }) {
  // useState フック：コンポーネント内でデータの状態を管理する
  // [現在の値, 値を変更する関数] = useState(初期値) の形で使用
  const [text, setText] = useState('');           // 入力フォームのテキスト
  const [creating, setCreating] = useState(false); // 投稿作成中かどうかのフラグ
  const [createError, setCreateError] = useState(''); // 投稿作成時のエラーメッセージ

  // フォーム送信時の処理を行う関数
  // async: 非同期処理（APIとの通信など時間のかかる処理）を扱うためのキーワード
  const handleSubmit = async (e) => {
    // preventDefault(): フォーム送信のデフォルト動作（ページリロード）を止める
    e.preventDefault();
    
    // 入力値のバリデーション（検証）
    // trim(): 文字列の前後の空白を除去。空文字だけの場合は false になる
    if (!text.trim()) {
      setCreateError('テキストを入力してください');
      return; // 処理を終了（以下のコードは実行されない）
    }

    // 文字数制限のチェック
    if (text.length > 255) {
      setCreateError('テキストは255文字以内で入力してください');
      return;
    }

    // 投稿作成処理の開始
    setCreating(true);      // 作成中フラグを true に（ボタンを無効化するため）
    setCreateError('');     // 前回のエラーメッセージをクリア
    
    // await: 非同期処理の完了を待つ。onCreatePost は親から受け取った投稿作成関数
    const result = await onCreatePost(text);
    
    // 投稿作成の結果によって処理を分岐
    if (result.success) {
      setText('');  // 成功時：入力フォームをクリア
    } else {
      setCreateError(result.error);  // 失敗時：エラーメッセージを表示
    }
    
    setCreating(false);  // 作成中フラグを false に戻す
  };

  // 早期リターン：特定の条件時は画面の表示を変える
  // loading が true の場合、以下の JSX は実行されず「読み込み中...」だけが表示される
  if (loading) return <div>読み込み中...</div>;
  if (error) return <div>エラー: {error}</div>;

  // メインの JSX：通常時に表示される画面の構造
  return (
    <div>
      {/* 投稿作成フォーム */}
      {/* onSubmit: フォーム送信時に実行される関数を指定 */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <div>
          {/* 入力フィールド */}
          <input
            type="text"
            value={text}                          // 現在の入力値（state で管理）
            onChange={(e) => setText(e.target.value)}  // 入力値が変わった時の処理
            placeholder="投稿内容を入力"            // 未入力時に表示されるヒント
            style={{ 
              width: '300px', 
              padding: '8px',
              marginRight: '10px'
            }}
            disabled={creating}                   // 投稿作成中は入力を無効化
          />
          {/* 投稿ボタン */}
          <button type="submit" disabled={creating}>
            {/* 三項演算子：条件 ? 真の場合 : 偽の場合 */}
            {creating ? '投稿中...' : '投稿'}
          </button>
        </div>
        {/* 条件付きレンダリング：createError が存在する場合のみ表示 */}
        {createError && (
          <div style={{ color: 'red', marginTop: '5px' }}>
            {createError}
          </div>
        )}
      </form>

      {/* 投稿一覧表示部分 */}
      <div>
        <h2>投稿一覧</h2>
        {/* 三項演算子で投稿の有無によって表示を切り替え */}
        {posts.length === 0 ? (
          <p>投稿がありません</p>
        ) : (
          <ul>
            {/* map 関数：配列の各要素に対して処理を実行し、新しい配列を作成 */}
            {/* ここでは各投稿データを <li> 要素に変換している */}
            {posts.map(post => (
              <li key={post.id}>  {/* key: React が要素を識別するための一意な値 */}
                {post.text} (ID: {post.id})
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
```

### 4.8 メインアプリコンポーネントの修正

**ファイル編集**: `client/src/App.jsx`（既存ファイルを以下に置き換え）

```javascript
// アプリケーション全体のメインコンポーネント
// 必要なコンポーネントとフック（機能）を読み込む
import { PostList } from './components/PostList';  // 投稿一覧を表示するコンポーネント
import { usePosts } from './hooks/usePosts';        // 投稿データを管理するカスタムフック

// App関数コンポーネント：アプリケーション全体のメイン画面
function App() {
  // usePosts カスタムフックから投稿に関する機能を取得
  // これにより、投稿データの状態管理とAPI通信が自動で行われる
  const { 
    posts,      // 投稿データの配列（例：[{id: 1, text: "投稿1"}, {id: 2, text: "投稿2"}]）
    loading,    // データ読み込み中かどうかを示すフラグ（true/false）
    error,      // エラーが発生した場合のエラーメッセージ
    createPost  // 新しい投稿を作成する関数
  } = usePosts();

  // JSX（JavaScript XML）: HTMLに似た記法でUIを記述
  // returnの中に書かれた内容が画面に表示される
  return (
    <div style={{ padding: '20px' }}>
      {/* アプリケーションのタイトル */}
      <h1>FastAPI + React 投稿アプリ</h1>
      
      {/* PostListコンポーネントに必要なデータと機能を渡す（propsという仕組み） */}
      <PostList 
        posts={posts}                    // 投稿データを子コンポーネントに渡す
        loading={loading}                // 読み込み状態を子コンポーネントに渡す
        error={error}                    // エラー情報を子コンポーネントに渡す
        onCreatePost={createPost}        // 投稿作成機能を子コンポーネントに渡す
      />
    </div>
  );
}

// このコンポーネントを他のファイルで使えるようにエクスポート
export default App;
```

### 4.9 フロントエンド用Dockerfile

**ファイル作成**: `client/Dockerfile.dev`

```dockerfile
# Node.js 18 の Alpine 版（軽量）イメージを使用
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# package.json をコピーして依存関係をインストール
# これにより、ソースコード変更時でも依存関係の再インストールを避けられる
COPY package*.json ./
RUN npm install

# アプリケーションのソースコードをコピー
COPY . .

# ポート5173を公開（Viteのデフォルトポート）
EXPOSE 5173

# 開発サーバーを起動（ホットリロード有効）
# --host 0.0.0.0: Docker コンテナ外からアクセス可能にする
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

---

## 🐳 5. Docker環境の構築

### 5.1 Docker Compose設定

**ファイル作成**: `infra/docker-compose.yml`

```yaml
# Docker Compose設定ファイル
# 開発環境で必要な3つのサービス（データベース、サーバー、クライアント）を定義
# 各サービスは独立したコンテナとして実行され、相互に通信可能

services:
  # データベースサービス（PostgreSQL）
  db:
    # Docker Hub から PostgreSQL 15 Alpine版のイメージを使用
    # Alpine: 軽量なLinuxディストリビューション
    image: postgres:15-alpine
    
    # 環境変数でデータベースの初期設定を行う
    environment:
      POSTGRES_USER: postgres      # データベースユーザー名
      POSTGRES_PASSWORD: password  # データベースパスワード
      POSTGRES_DB: app            # 作成するデータベース名
    
    # ボリューム（データの永続化）
    volumes:
      # postgres_data という名前付きボリュームにデータを保存
      # コンテナを削除してもデータが残る
      - postgres_data:/var/lib/postgresql/data
    
    # ポート設定：ホスト:コンテナ
    ports:
      - "5432:5432"  # PostgreSQLの標準ポート5432をホストからもアクセス可能に
    
    # ヘルスチェック：サービスが正常に動作しているかを確認
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]  # PostgreSQLが接続可能かチェック
      interval: 5s   # 5秒間隔でチェック
      timeout: 5s    # 5秒でタイムアウト
      retries: 5     # 5回まで再試行

  # バックエンドサーバー（FastAPI）
  server:
    # Dockerfileからイメージをビルド
    build:
      context: ../server        # ビルドコンテキスト（Dockerfileがある場所）
      dockerfile: Dockerfile.dev  # 開発用Dockerfile
    
    # ボリューム（ホットリロード対応）
    volumes:
      - ../server:/app  # ホストのserverディレクトリをコンテナの/appにマウント
                       # ファイル変更時に自動でサーバーが再起動される
    
    # 環境変数
    environment:
      # データベース接続文字列（サービス名'db'でアクセス可能）
      DATABASE_URL: postgresql://postgres:password@db:5432/app
      DEBUG: "true"   # デバッグモード有効
    
    # ポート設定
    ports:
      - "8000:8000"  # FastAPIサーバーのポート8000をホストからアクセス可能に
    
    # 依存関係：dbサービスが健全な状態になってから起動
    depends_on:
      db:
        condition: service_healthy  # dbのヘルスチェックが成功するまで待機
    
    # コンテナ起動時に実行するコマンド
    # uvicorn: Python ASGI サーバー
    # --reload: ファイル変更時の自動再起動
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # フロントエンドクライアント（React + Vite）
  client:
    # Dockerfileからイメージをビルド
    build:
      context: ../client        # ビルドコンテキスト
      dockerfile: Dockerfile.dev  # 開発用Dockerfile
    
    # ボリューム（ホットリロード対応）
    volumes:
      - ../client:/app        # ホストのclientディレクトリをマウント
      - /app/node_modules     # node_modulesは匿名ボリューム（コンテナ内のものを優先）
    
    # ポート設定
    ports:
      - "5173:5173"  # Viteの開発サーバーポート5173をホストからアクセス可能に
    
    # 環境変数
    environment:
      - NODE_ENV=development  # Node.js開発モード

# 名前付きボリューム定義
# データベースのデータを永続化するため
volumes:
  postgres_data:  # PostgreSQLデータ用の永続ボリューム
```

---

## 🚀 6. アプリケーションの起動と動作確認

### 6.1 初回起動

```bash
# プロジェクトのルートディレクトリに移動
cd web-app-simple

# infra ディレクトリに移動
cd infra

# 開発環境を起動（初回は時間がかかります）
docker-compose up --build -d

# ログの確認（問題が発生した場合）
docker-compose logs -f
```

### 6.2 動作確認

以下のURLにアクセスして動作を確認：

1. **フロントエンド**: http://localhost:5173
   - 投稿アプリの画面が表示される
   
2. **バックエンドAPI**: http://localhost:8000/docs
   - FastAPI の自動生成API仕様書が表示される
   
3. **ルートエンドポイント**: http://localhost:8000/
   - `{"message": "投稿アプリAPI が正常に動作しています", "version": "1.0.0"}` が表示される

### 6.3 基本操作のテスト

1. **投稿作成テスト**:
   - フロントエンド画面で「投稿内容を入力」に文字を入力
   - 「投稿」ボタンをクリック
   - 投稿が一覧に表示されることを確認

2. **APIの直接テスト** (http://localhost:8000/docs):
   - `/api/v1/posts` (GET) を実行して投稿一覧を確認
   - `/api/v1/posts` (POST) を実行して新しい投稿を作成

### 6.4 トラブルシューティング

**よくある問題と解決方法:**

```bash
# ポート競合エラー
docker-compose down  # 一度停止
docker-compose up --build -d  # 再起動

# データベース接続エラー
docker-compose logs db    # DBログ確認
docker-compose restart db # DB再起動

# フロントエンドが表示されない
docker-compose logs client  # クライアントログ確認
```

---

**🎉 完成！** 

これで0からシンプルな投稿アプリを構築する手順が完了しました。各ステップを順番に実行することで、FastAPI + React + PostgreSQL のフルスタックWebアプリケーションが動作するはずです。