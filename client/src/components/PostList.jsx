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