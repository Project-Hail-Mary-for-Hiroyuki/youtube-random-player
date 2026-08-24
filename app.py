import streamlit as st
import streamlit.components.v1 as components
from youtube_service import YouTubeService, THEME_KEYWORDS
from history_manager import HistoryManager

# ページ基本設定
st.set_page_config(
    page_title="YouTube テーマ別ランダムプレイヤー",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.2rem;
    }

    .video-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .next-preview-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(49, 46, 129, 0.8));
        border-left: 5px solid #6366f1;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .next-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #818cf8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
    }

    .next-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .badge {
        display: inline-block;
        background: #ef4444;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }

    .badge-time {
        display: inline-block;
        background: #3b82f6;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }

    .badge-date {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        color: white;
        font-size: 1.15rem;
        font-weight: 700;
        padding: 0.75rem 1.8rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
        background: linear-gradient(90deg, #f87171 0%, #ef4444 100%);
    }

    .summary-box {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 10px;
        border-left: 3px solid #10b981;
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.5;
    }

    .history-item {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #ef4444;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

yt_service = YouTubeService()
history_mgr = HistoryManager()

if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "next_video" not in st.session_state:
    st.session_state.next_video = None
if "cached_candidates" not in st.session_state:
    st.session_state.cached_candidates = []
if "last_theme" not in st.session_state:
    st.session_state.last_theme = ""
if "last_only_recent" not in st.session_state:
    st.session_state.last_only_recent = True

# --- サイドバー ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/youtube-play.png", width=64)
    st.title("⚙️ 再生設定")
    st.markdown("---")

    # 1. テーマ選択
    theme_options = list(THEME_KEYWORDS.keys()) + ["カスタム入力"]
    selected_theme = st.selectbox(
        "📚 テーマを選択",
        options=theme_options,
        index=0,
        help="再生したい動画の分野・ジャンルを選択してください。"
    )

    custom_keyword = ""
    if selected_theme == "カスタム入力":
        custom_keyword = st.text_input("🔍 カスタムキーワードを入力", placeholder="例: 心理学 テクニック")

    st.markdown("---")

    # 2. 投稿日フィルター（1ヶ月以内チェックボックス）
    st.subheader("📅 投稿日時フィルター")
    only_recent = st.checkbox(
        "1ヶ月以内の動画のみに絞り込む",
        value=True,
        help="過去30日以内に作成・投稿された最新の動画のみを抽出します。外すと過去の全動画が対象になります。"
    )

    st.markdown("---")

    # 3. 時間制限スライダー
    st.subheader("⏱️ 動画の長さを制限")
    duration_range = st.slider(
        "分単位で指定",
        min_value=1,
        max_value=60,
        value=(5, 20),
        step=1
    )

    min_sec = duration_range[0] * 60
    max_sec = duration_range[1] * 60

    st.markdown("---")

    # 4. 履歴管理
    st.subheader("📜 履歴管理")
    watched_count = len(history_mgr.load_history())
    st.write(f"再生済み動画数: **{watched_count}** 件")
    
    if st.button("🗑️ 履歴をクリア", use_container_width=True):
        history_mgr.clear_history()
        st.session_state.current_video = None
        st.session_state.next_video = None
        st.session_state.cached_candidates = []
        st.toast("再生履歴をクリアしました！", icon="🧹")
        st.rerun()

# ヘッダー
st.markdown('<div class="main-title">🎬 YouTube テーマ別ランダムプレイヤー</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">5分〜20分の動画を自動再生。1ヶ月以内フィルタ・次回予告・要約機能付き。</div>', unsafe_allow_html=True)

current_theme_key = custom_keyword if selected_theme == "カスタム入力" else selected_theme

def prepare_candidates_and_next():
    """条件変更時や候補が少ない場合に動画を再取得・選定"""
    if (st.session_state.last_theme != current_theme_key or 
        st.session_state.last_only_recent != only_recent or
        len(st.session_state.cached_candidates) < 2):
        
        candidates = yt_service.fetch_videos(
            theme=selected_theme,
            custom_keyword=custom_keyword,
            min_duration=min_sec,
            max_duration=max_sec,
            only_recent=only_recent
        )
        st.session_state.cached_candidates = candidates
        st.session_state.last_theme = current_theme_key
        st.session_state.last_only_recent = only_recent

    if not st.session_state.next_video and st.session_state.cached_candidates:
        watched_ids = history_mgr.get_watched_ids()
        if st.session_state.current_video:
            watched_ids.add(st.session_state.current_video['id'])
            
        next_vid, _ = yt_service.pick_random_video(st.session_state.cached_candidates, watched_ids)
        st.session_state.next_video = next_vid

if selected_theme != "カスタム入力" or custom_keyword.strip():
    prepare_candidates_and_next()

# --- 次の動画（予告）カード ---
if st.session_state.next_video:
    nv = st.session_state.next_video
    date_str = nv.get('upload_date_formatted', '')
    date_html = f"&nbsp;|&nbsp; 📅 投稿日: <strong>{date_str}</strong>" if date_str else ""
    st.markdown(
        f"""
        <div class="next-preview-card">
            <div class="next-label">⏭️ 次に再生される動画（予告）</div>
            <div class="next-title">{nv.get('title')}</div>
            <div style="font-size: 0.85rem; color: #cbd5e1;">
                📺 チャンネル: <strong>{nv.get('channel')}</strong> &nbsp;|&nbsp; ⏱️ 時間: <strong>{nv.get('duration_formatted')}</strong>{date_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

col_btn, _ = st.columns([2, 1])
with col_btn:
    play_clicked = st.button("🎲 次の動画に切り替える（自動再生スタート）", use_container_width=True)

if play_clicked:
    if selected_theme == "カスタム入力" and not custom_keyword.strip():
        st.error("カスタムキーワードを入力してください。")
    else:
        with st.spinner("次の動画を準備中... 🚀"):
            if st.session_state.next_video:
                st.session_state.current_video = st.session_state.next_video
                history_mgr.add_to_history(st.session_state.current_video)
                st.session_state.next_video = None
            else:
                prepare_candidates_and_next()
                if st.session_state.cached_candidates:
                    watched_ids = history_mgr.get_watched_ids()
                    cur_vid, reset_occ = yt_service.pick_random_video(st.session_state.cached_candidates, watched_ids)
                    st.session_state.current_video = cur_vid
                    if cur_vid:
                        history_mgr.add_to_history(cur_vid)
                    if reset_occ:
                        st.toast("一通りの動画を視聴したため、過去の動画を含めて再選択しました 🔄", icon="ℹ️")

            watched_ids = history_mgr.get_watched_ids()
            if st.session_state.current_video:
                watched_ids.add(st.session_state.current_video['id'])
            
            new_next, _ = yt_service.pick_random_video(st.session_state.cached_candidates, watched_ids)
            st.session_state.next_video = new_next
            st.rerun()

# --- メイン動画再生エリア ---
if st.session_state.current_video:
    video = st.session_state.current_video
    video_id = video["id"]

    col_player, col_details = st.columns([7, 5])

    with col_player:
        iframe_src = f"https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0&enablejsapi=1"
        components.iframe(iframe_src, height=450, scrolling=False)

    with col_details:
        st.markdown('<div class="video-card">', unsafe_allow_html=True)
        date_badge = f'<span class="badge-date">📅 {video.get("upload_date_formatted")}</span>' if video.get("upload_date_formatted") else ""
        st.markdown(f'<span class="badge">{video.get("theme", "テーマ")}</span><span class="badge-time">⏱️ {video.get("duration_formatted")}</span>{date_badge}', unsafe_allow_html=True)
        st.markdown(f"### {video.get('title')}")
        st.markdown(f"**📺 チャンネル:** {video.get('channel')}")
        st.markdown(f"**🔗 YouTubeで開く:** [{video.get('url')}]({video.get('url')})")
        
        st.markdown("#### 📝 動画の要約・ポイント")
        st.markdown(f'<div class="summary-box">{video.get("summary", "要約情報はありません。")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 「🎲 次の動画に切り替える」ボタンを押すと、予告されている動画が自動再生でスタートします！")

st.markdown("---")

# 再生履歴
st.subheader("📜 最近の再生履歴")
history_list = history_mgr.load_history()

if history_list:
    with st.expander(f"過去に再生した動画一覧 ({len(history_list)}件)", expanded=False):
        for idx, item in enumerate(history_list[:15]):
            st.markdown(
                f"""
                <div class="history-item">
                    <strong>{idx + 1}. [{item.get('theme')}] {item.get('title')}</strong> 
                    ({item.get('duration_formatted', '')} - 投稿日: {item.get('upload_date_formatted', '不明')})
                    <br><a href="{item.get('url')}" target="_blank" style="color: #60a5fa; font-size: 0.8rem;">YouTubeで開く ↗</a>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.caption("再生履歴はまだありません。")
