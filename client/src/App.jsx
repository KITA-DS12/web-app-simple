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
    createPost, // 新しい投稿を作成する関数
    refetch     // データを再取得する関数（今回は使用していないが将来の拡張用）
  } = usePosts();

  // JSX（JavaScript XML）: HTMLに似た記法でUIを記述
  // returnの中に書かれた内容が画面に表示される
  return (
    <div style={{ padding: '20px' }}>
      {/* アプリケーションのタイトル */}
      <h1>FastAPI + React Posts App</h1>
      
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