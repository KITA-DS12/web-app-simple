// React の useState と useEffect フックをインポート
import { useState, useEffect } from 'react';
// API 通信を行う関数をインポート
import { postsApi } from '../api/posts';

// カスタムフック：投稿関連の状態管理とAPI通信をまとめた再利用可能な機能
// 「use」で始まる関数名にすることで React がフックとして認識する
export function usePosts() {
  // 状態管理：useState フックで各種状態を定義
  const [posts, setPosts] = useState([]);        // 投稿データの配列
  const [loading, setLoading] = useState(true);  // データ読み込み中フラグ
  const [error, setError] = useState(null);      // エラー情報

  // 投稿一覧を取得する非同期関数
  const fetchPosts = async () => {
    try {
      // try-catch 文：エラーが発生する可能性のある処理を安全に実行
      setLoading(true);  // 読み込み開始
      
      // API から投稿データを取得（await で完了を待つ）
      const data = await postsApi.getAll();
      
      setPosts(data);    // 取得したデータで状態を更新
      setError(null);    // エラーをクリア
    } catch (err) {
      // API 通信でエラーが発生した場合の処理
      setError(err.message);
    } finally {
      // try または catch のどちらが実行されても最後に必ず実行される
      setLoading(false);  // 読み込み完了
    }
  };

  // 新しい投稿を作成する非同期関数
  const createPost = async (text) => {
    try {
      // API に新しい投稿を送信
      const newPost = await postsApi.create(text);
      
      // スプレッド演算子（...）を使って新しい投稿を配列の先頭に追加
      // [newPost, ...posts] は [新しい投稿, 既存の投稿1, 既存の投稿2, ...] という配列になる
      setPosts([newPost, ...posts]);
      
      // 成功時は success: true を返す
      return { success: true };
    } catch (err) {
      // 失敗時は success: false とエラーメッセージを返す
      return { success: false, error: err.message };
    }
  };

  // useEffect フック：コンポーネントの生存期間中の特定のタイミングで処理を実行
  // 第二引数の配列（依存配列）が空の場合、コンポーネントの初回マウント時のみ実行
  useEffect(() => {
    fetchPosts();  // コンポーネント表示時に投稿一覧を取得
  }, []); // 空の依存配列 = 初回のみ実行

  // このカスタムフックを使用するコンポーネントに提供する値や関数
  return {
    posts,           // 投稿データの配列
    loading,         // 読み込み中フラグ
    error,           // エラー情報
    createPost,      // 投稿作成関数
    refetch: fetchPosts  // データ再取得関数（refetch という名前で fetchPosts を提供）
  };
}