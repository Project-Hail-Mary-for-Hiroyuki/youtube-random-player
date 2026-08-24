import streamlit as st
import streamlit.components.v1 as components
from youtube_service import YouTubeService, THEME_KEYWORDS
from history_manager import HistoryManager

# ページ基本設定
st.set_page_config(
    page_title="Freestyle YouTube! 🎧 DJ Random Player",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（ナイトライフ・ネオン・DJコントローラーデザイン）
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">

<style>
    /* 全体背景 - クラブナイト・メッシュブラックグラデーション */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1e1035 0%, #080912 60%, #030408 100%);
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }

    /* サイドバー - メタル＆ダークコンソール調 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111322 0%, #090a14 100%);
        border-right: 1px solid rgba(168, 85, 247, 0.2);
    }

    /* タイトル - ネオンサイバーサイン */
    .dj-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #ec4899 0%, #a855f7 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .dj-subtitle {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 3px;
        color: #38bdf8;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .dj-subtitle::before {
        content: "🔴 LIVE";
        font-size: 0.7rem;
        background: #ef4444;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 800;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }

    /* DJデッキ風ネオン予告カード */
    .next-deck-card {
        background: linear-gradient(135deg, rgba(24, 24, 43, 0.9), rgba(15, 23, 42, 0.95));
        border: 1px solid #a855f7;
        border-left: 6px solid #38bdf8;
        border-radius: 14px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.25), inset 0 0 10px rgba(6, 182, 212, 0.1);
        position: relative;
        overflow: hidden;
    }

    .next-deck-label {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8rem;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .next-deck-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* DJ SPINメインボタン */
    div.stButton > button:first-child {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(135deg, #ec4899 0%, #a855f7 50%, #6366f1 100%);
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 0.9rem 2rem;
        border-radius: 50px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 25px rgba(236, 72, 153, 0.5), 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: all 0.25s ease-in-out;
        width: 100%;
        text-transform: uppercase;
    }
    
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 0 35px rgba(168, 85, 247, 0.8), 0 6px 20px rgba(0, 0, 0, 0.7);
        border-color: #ffffff;
        background: linear-gradient(135deg, #f43f5e 0%, #c084fc 50%, #38bdf8 100%);
    }

    /* 再生中動画コンソール */
    .now-playing-card {
        background: rgba(15, 23, 42, 0.85);
        border-radius: 14px;
        padding: 1.4rem;
        border: 1px solid rgba(168, 85, 247, 0.3);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
    }

    /* バッジスタイリング */
    .badge-theme {
        background: linear-gradient(90deg, #ec4899, #8b5cf6);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        margin-right: 6px;
        box-shadow: 0 0 10px rgba(236, 72, 153, 0.4);
    }

    .badge-time {
        background: rgba(6, 182, 212, 0.2);
        border: 1px solid #06b6d4;
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        margin-right: 6px;
    }

    .badge-date {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* 音声トラック要約ボックス */
    .track-summary {
        background: rgba(10, 15, 30, 0.8);
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 12px;
        border-left: 4px solid #a855f7;
        font-size: 0.92rem;
        color: #cbd5e1;
        line-height: 1.6;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.4);
    }

    .history-item {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #ec4899;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 0.88rem;
        transition: background 0.2s ease;
    }

    .history-item:hover {
        background: rgba(30, 41, 59, 0.8);
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

# --- サイドバー (DJ CONSOLE SETTINGS) ---
with st.sidebar:
    st.markdown('<h2 style="font-family:\'Orbitron\'; color:#a855f7; font-size:1.4rem;">🎛️ DJ CONSOLE</h2>', unsafe_allow_html=True)
    st.markdown("---")

    # 1. テーマ選択
    theme_options = list(THEME_KEYWORDS.keys()) + ["カスタム入力"]
    selected_theme = st.selectbox(
        "🎧 SELECT GENRE / THEME",
        options=theme_options,
        index=0,
        help="再生したいテーマ・ジャンルを選択してください。"
    )

    custom_keyword = ""
    if selected_theme == "カスタム入力":
        custom_keyword = st.text_input("🔍 CUSTOM KEYWORD", placeholder="例: 心理学 テクニック")

    st.markdown("---")

    # 2. 投稿日フィルター
    st.subheader("📅 DATE FILTER")
    only_recent = st.checkbox(
        "1ヶ月以内の最新トラックのみ",
        value=True,
        help="過去30日以内に作成・投稿された最新動画のみに絞り込みます。"
    )

    st.markdown("---")

    # 3. 時間制限スライダー
    st.subheader("⏱️ TRACK DURATION")
    duration_range = st.slider(
        "再生時間（分）",
        min_value=1,
        max_value=60,
        value=(5, 20),
        step=1
    )

    min_sec = duration_range[0] * 60
    max_sec = duration_range[1] * 60

    st.markdown("---")

    # 4. 履歴管理
    st.subheader("📜 CRATE HISTORY")
    watched_count = len(history_mgr.load_history())
    st.write(f"PLAYED TRACKS: **{watched_count}**")
    
    if st.button("🗑️ CLEAR CRATE", use_container_width=True):
        history_mgr.clear_history()
        st.session_state.current_video = None
        st.session_state.next_video = None
        st.session_state.cached_candidates = []
        st.toast("履歴クレートをクリアしました！", icon="🧹")
        st.rerun()

# メインヘッダー
st.markdown('<div class="dj-title">🎧 FREESTYLE YOUTUBE!</div>', unsafe_allow_html=True)
st.markdown('<div class="dj-subtitle">RANDOM TRACK SELECTOR & AUTOPLAY CONSOLE</div>', unsafe_allow_html=True)

current_theme_key = custom_keyword if selected_theme == "カスタム入力" else selected_theme

def prepare_candidates_and_next():
    """テーマや条件変更時に動画を自動収集・選定"""
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

# --- DJ ON DECK (次回予告カード) ---
if st.session_state.next_video:
    nv = st.session_state.next_video
    date_str = nv.get('upload_date_formatted', '')
    date_html = f"&nbsp;|&nbsp; 📅 {date_str}" if date_str else ""
    st.markdown(
        f"""
        <div class="next-deck-card">
            <div class="next-deck-label">🎧 NEXT ON DECK (次回トラック予告)</div>
            <div class="next-deck-title">{nv.get('title')}</div>
            <div style="font-size: 0.88rem; color: #a5f3fc;">
                📺 CHANNEL: <strong>{nv.get('channel')}</strong> &nbsp;|&nbsp; ⏱️ DURATION: <strong>{nv.get('duration_formatted')}</strong>{date_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

col_btn, _ = st.columns([2, 1])
with col_btn:
    play_clicked = st.button("🎛️ SPIN THE DECK (NEXT TRACK)", use_container_width=True)

if play_clicked:
    if selected_theme == "カスタム入力" and not custom_keyword.strip():
        st.error("カスタムキーワードを入力してください。")
    else:
        with st.spinner("SPINNING THE DECK... ⚡"):
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
                        st.toast("一通りのトラックを視聴したため、クレートを循環再選択しました 🔄", icon="ℹ️")

            watched_ids = history_mgr.get_watched_ids()
            if st.session_state.current_video:
                watched_ids.add(st.session_state.current_video['id'])
            
            new_next, _ = yt_service.pick_random_video(st.session_state.cached_candidates, watched_ids)
            st.session_state.next_video = new_next
            st.rerun()

# --- NOW PLAYING MAIN CONSOLE ---
if st.session_state.current_video:
    video = st.session_state.current_video
    video_id = video["id"]

    col_player, col_details = st.columns([7, 5])

    with col_player:
        iframe_src = f"https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0&enablejsapi=1"
        components.iframe(iframe_src, height=450, scrolling=False)

    with col_details:
        st.markdown('<div class="now-playing-card">', unsafe_allow_html=True)
        date_badge = f'<span class="badge-date">📅 {video.get("upload_date_formatted")}</span>' if video.get("upload_date_formatted") else ""
        st.markdown(f'<span class="badge-theme">{video.get("theme", "GENRE")}</span><span class="badge-time">⏱️ {video.get("duration_formatted")}</span>{date_badge}', unsafe_allow_html=True)
        st.markdown(f"### {video.get('title')}")
        st.markdown(f"**📺 CHANNEL:** {video.get('channel')}")
        st.markdown(f"**🔗 OPEN ON YOUTUBE:** [{video.get('url')}]({video.get('url')})")
        
        st.markdown("<h4 style='color:#c084fc; margin-top:14px;'>🎚️ TRACK SUMMARY & NOTES</h4>", unsafe_allow_html=True)
        st.markdown(f'<div class="track-summary">{video.get("summary", "要約情報はありません。")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 「🎛️ SPIN THE DECK」ボタンを押してトラック再生をスタート！")

st.markdown("---")

# PLAYLIST CRATE HISTORY
st.subheader("📜 PLAYLIST CRATE (HISTORY)")
history_list = history_mgr.load_history()

if history_list:
    with st.expander(f"CRATE ITEMS ({len(history_list)} TRACKS)", expanded=False):
        for idx, item in enumerate(history_list[:15]):
            st.markdown(
                f"""
                <div class="history-item">
                    <strong>{idx + 1}. [{item.get('theme')}] {item.get('title')}</strong> 
                    ({item.get('duration_formatted', '')} - 📅 {item.get('upload_date_formatted', '不明')})
                    <br><a href="{item.get('url')}" target="_blank" style="color: #38bdf8; font-size: 0.8rem;">PLAY ON YOUTUBE ↗</a>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.caption("NO TRACKS IN CRATE YET.")
