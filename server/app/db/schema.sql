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