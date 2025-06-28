# Web App MVP - FastAPI + React + PostgreSQL

FastAPI と React を使用した投稿管理アプリケーションの MVP (Minimum Viable Product)。

## 技術スタック

- **バックエンド**: Python 3.11, FastAPI, asyncpg
- **フロントエンド**: React 18, Vite, JavaScript
- **データベース**: PostgreSQL
- **コンテナ**: Docker, Docker Compose
- **デプロイ**: Google Cloud Run

## 機能

- 投稿の一覧表示（GET /api/v1/posts）
- 新規投稿の作成（POST /api/v1/posts）
- リアルタイムでの投稿反映
- バリデーション（空文字、255文字超のチェック）

## セットアップ

### 開発環境

```bash
# 開発環境の起動
make dev

# 開発環境の停止
make dev-down
```

アプリケーションは以下のURLでアクセス可能:
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- データベース: localhost:5432

### テスト実行

```bash
# テストの実行
make test

# 詳細なテスト結果を表示
make test-verbose
```

### 本番環境へのデプロイ

#### 前提条件
- Google Cloud SDK (`gcloud`) がインストールされていること
- Google Cloud プロジェクトが作成済みであること
- Container Registry または Artifact Registry が有効化されていること
- Cloud Run API が有効化されていること

#### 手順

1. **Google Cloud へのログイン**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **API の有効化**
```bash
# Cloud Run API を有効化
gcloud services enable run.googleapis.com

# Container Registry API を有効化
gcloud services enable containerregistry.googleapis.com

# Cloud Build API を有効化
gcloud services enable cloudbuild.googleapis.com
```

3. **データベースの準備（Cloud SQL を使用する場合）**
```bash
# Cloud SQL インスタンスの作成
gcloud sql instances create my-postgres-instance \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# データベースの作成
gcloud sql databases create app --instance=my-postgres-instance

# ユーザーの作成
gcloud sql users create myuser --instance=my-postgres-instance --password=mypassword
```

4. **ビルドとデプロイ**
```bash
# 環境変数を設定
export IMAGE=gcr.io/YOUR_PROJECT_ID/web-app-mvp
export SERVICE=web-app-mvp
export REGION=us-central1

# Dockerイメージのビルドとプッシュ、デプロイを一括実行
make deploy-all IMAGE=$IMAGE SERVICE=$SERVICE REGION=$REGION

# または個別に実行
make build IMAGE=$IMAGE
make push IMAGE=$IMAGE
make deploy IMAGE=$IMAGE SERVICE=$SERVICE REGION=$REGION
```

5. **環境変数の設定（Cloud SQL を使用する場合）**
```bash
# Cloud SQL 接続名を取得
gcloud sql instances describe my-postgres-instance --format="value(connectionName)"

# 環境変数を設定してデプロイ
gcloud run services update $SERVICE \
  --add-cloudsql-instances=YOUR_PROJECT_ID:us-central1:my-postgres-instance \
  --set-env-vars="DATABASE_URL=postgresql://myuser:mypassword@/app?host=/cloudsql/YOUR_PROJECT_ID:us-central1:my-postgres-instance" \
  --region=$REGION
```

6. **デプロイの確認**
```bash
# サービスの URL を取得
gcloud run services describe $SERVICE --region=$REGION --format="value(status.url)"
```

## 環境変数

### 開発環境（.env.dev）
```
DATABASE_URL=postgresql://postgres:password@db:5432/app
DEBUG=true
```

### 本番環境（.env.prod）
```
DATABASE_URL=postgresql://user:password@/database?host=/cloudsql/CONNECTION_NAME
DEBUG=false
```

## プロジェクト構造

```
web-app-mvp/
├─ infra/               # インフラ設定
├─ server/              # バックエンドアプリケーション
│  ├─ app/
│  │  ├─ core/         # 設定、ロギング
│  │  ├─ db/           # データベース関連
│  │  ├─ services/     # ビジネスロジック
│  │  └─ api/          # APIエンドポイント
│  └─ tests/           # テスト
├─ client/              # フロントエンドアプリケーション
└─ Makefile            # ビルド・デプロイコマンド
```

## 注意事項

- 本番環境では適切なデータベース接続情報を設定してください
- Cloud SQL を使用する場合は、Cloud SQL Proxy の設定が必要です
- 環境変数は適切に管理し、シークレットは公開しないでください
- Cloud Run の無料枠を超える場合は料金が発生します
- 初回デプロイ時はコールドスタートが発生する可能性があります

## トラブルシューティング

### デプロイエラー
- `gcloud` コマンドが見つからない → Google Cloud SDK をインストール
- 権限エラー → `gcloud auth login` で再認証
- ビルドエラー → Docker Desktop が起動していることを確認

### 接続エラー
- データベース接続エラー → Cloud SQL Proxy の設定を確認
- CORS エラー → 本番環境の URL を `CORS_ORIGINS` に追加