# シンプル投稿アプリ - FastAPI + React + PostgreSQL

FastAPI と React を使用した投稿管理アプリケーション。学習・理解に最適化されたシンプルな構成。

## 技術スタック

- **バックエンド**: Python 3.11, FastAPI, asyncpg
- **フロントエンド**: React 18, Vite, JavaScript
- **データベース**: PostgreSQL
- **コンテナ**: Docker, Docker Compose

## 機能

- 投稿の一覧表示（GET /api/v1/posts）
- 新規投稿の作成（POST /api/v1/posts）
- リアルタイムでの投稿反映
- バリデーション（空文字、255文字超のチェック）

## セットアップ

### 開発環境

```bash
# infra ディレクトリに移動
cd infra

# 開発環境の起動
docker-compose up --build -d

# 開発環境の停止
docker-compose down
```

アプリケーションは以下のURLでアクセス可能:
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- API仕様書: http://localhost:8000/docs
- データベース: localhost:5432

## プロジェクト構造

```
web-app-simple/
├─ infra/               # インフラ設定
│  └─ docker-compose.yml # 開発環境設定
├─ server/              # バックエンドアプリケーション
│  ├─ app/
│  │  ├─ core/         # 設定管理
│  │  ├─ db/           # データベース関連
│  │  ├─ services/     # ビジネスロジック
│  │  └─ api/          # APIエンドポイント
│  └─ requirements.txt # 使用ライブラリ一覧
├─ client/              # フロントエンドアプリケーション
│  ├─ src/             # ソースコード
│  └─ package.json     # 使用ライブラリ一覧
└─ lecture-materials.md # 学習教材
```

## 環境変数

### 開発環境（docker-compose.yml内で設定済み）
```
DATABASE_URL=postgresql://postgres:password@db:5432/app
DEBUG=true
```

## シンプル化について

このプロジェクトは学習・理解しやすさを重視してシンプル化されています：

### 削除された機能
- テスト機能
- ログ機能  
- 複雑なライフサイクル管理
- デプロイ関連ファイル
- 静的ファイル配信
- ヘルスチェック
- 依存性注入（Depends）

### シンプル化された部分
- データベース接続（プールなし、直接接続）
- サービス層（関数ベース）
- API層（直接関数呼び出し）

### 保持された部分
- 基本的な投稿機能
- レイヤー分離（API・サービス・リポジトリ）
- 詳細なコメント（学習用）
- バリデーション
- エラーハンドリング

## 学習リソース

詳細な学習教材は `lecture-materials.md` を参照してください。
- Web開発の基本概念
- 各ファイルの役割と構造
- 実習課題

## トラブルシューティング

### よくある問題

**ポート競合エラー**
```bash
docker-compose down  # 一度停止
docker-compose up --build -d  # 再起動
```

**データベース接続エラー**
```bash
# データベースコンテナの状態確認
docker-compose ps

# ログ確認
docker-compose logs db
```

**フロントエンドが表示されない**
- ブラウザで http://localhost:5173 にアクセス
- 少し待ってからリロード（初回起動は時間がかかります）