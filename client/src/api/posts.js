// API のベース URL を定数として定義
// '/api/v1' は vite.config.js でプロキシ設定により http://localhost:8000/api/v1 に転送される
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