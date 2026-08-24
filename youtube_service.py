import random
import yt_dlp
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi

THEME_KEYWORDS = {
    "AI": ["AI 活用 最新", "ChatGPT 使い方 解説", "生成AI 入門", "AIニュース わかりやすく"],
    "英語": ["英語 勉強法", "英会話 コツ", "リスニング 英語 解説", "ネイティブ 英語 表現"],
    "思考法": ["思考法 本 概要", "論理的思考 入門", "クリティカルシンキング", "問題解決 思考"],
    "ビジネス": ["ビジネスモデル 解説", "マーケティング 基礎", "キャリア 思考法", "生産性 向上 テクニック"],
    "プログラミング": ["プログラミング 基礎 入門", "Python 活用法", "Web開発 初心者", "エンジニア 勉強法"],
    "科学・教養": ["科学 解説 わかりやすく", "歴史 雑学 教養", "宇宙 謎 解説", "経済 仕組み 基礎"]
}

PRESET_VIDEOS = {
    "AI": [
        {
            "id": "5sLYA310vg4", 
            "title": "【最新AI入門】AIの基礎知識と活用例をわかりやすく解説", 
            "duration": 600, 
            "channel": "教養チャンネル", 
            "theme": "AI",
            "upload_date_formatted": "2026/08/10 (14日前)",
            "days_ago": 14,
            "key_points": [
                "💡 AIの定義と機械学習・ディープラーニングの違いを初心者向けに整理",
                "⚡ ChatGPTをはじめとする生成AIのビジネス活用事例（文章作成・データ分析）",
                "🎯 今後伸びるAIスキルと人間の役割分担のコツ"
            ],
            "summary": "AIの基本的な概念から、仕事や日常生活での最新活用シーンまで初心者向けにわかりやすく解説した動画です。"
        }
    ]
}

def clean_and_summarize(description: Optional[str]) -> str:
    if not description or not description.strip():
        return "この動画のテキスト概要はありません。"

    lines = description.splitlines()
    clean_lines = []
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        if re.match(r'^https?://', line_str) or line_str.startswith('#'):
            continue
        if any(keyword in line_str.lower() for keyword in ['twitter', 'instagram', 'facebook', 'チャンネル登録', '高評価']):
            continue
        clean_lines.append(line_str)

    if not clean_lines:
        return description[:180] + "..." if len(description) > 180 else description

    summary_text = " / ".join(clean_lines[:3])
    if len(summary_text) > 220:
        summary_text = summary_text[:220] + "..."
    return summary_text


def extract_key_points(video_id: str, description: Optional[str]) -> List[str]:
    """
    YouTube字幕(Transcript)から動画本編の重要ポイント3選を抽出・要約。
    字幕がない場合は説明文からキーポイントを生成。
    """
    key_points = []
    
    try:
        # 字幕データを取得（日本語または英語）
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
        
        # 字幕テキストを結合
        full_text = " ".join([item['text'] for item in transcript_list if item.get('text')])
        
        # 意味のある文（20文字以上）をフィルタ
        sentences = [s.strip() for s in re.split(r'[。！!？?\n]', full_text) if len(s.strip()) > 15]
        
        if len(sentences) >= 3:
            # 序盤、中盤、終盤の重要フレーズを1つずつ抽出
            idx1 = min(1, len(sentences) - 1)
            idx2 = len(sentences) // 2
            idx3 = max(0, len(sentences) - 2)
            
            p1 = sentences[idx1][:80]
            p2 = sentences[idx2][:80]
            p3 = sentences[idx3][:80]
            
            key_points = [
                f"💡 【オープニング/導入】: {p1}...",
                f"⚡ 【メインテーマ】: {p2}...",
                f"🎯 【結論/まとめ】: {p3}..."
            ]
    except Exception:
        # 字幕取得不可の場合のフォールバック
        pass

    # 字幕から十分なポイントが得られなかった場合、説明文（description）を利用
    if not key_points and description:
        lines = [l.strip() for l in description.splitlines() if len(l.strip()) > 10 and not l.strip().startswith(('http', 'www', '#'))]
        if len(lines) >= 3:
            key_points = [
                f"💡 ポイント1: {lines[0][:75]}",
                f"⚡ ポイント2: {lines[1][:75]}",
                f"🎯 ポイント3: {lines[2][:75]}"
            ]
        elif lines:
            key_points = [f"💡 動画の概要: {lines[0][:150]}"]

    if not key_points:
        key_points = ["💡 本編のキーポイント情報はありません。動画をご視聴ください。"]

    return key_points


def parse_upload_date(upload_date_str: Optional[str]) -> tuple[str, int]:
    if not upload_date_str or len(upload_date_str) != 8:
        return "公開日不明", 9999

    try:
        dt = datetime.strptime(upload_date_str, "%Y%m%d")
        now = datetime.now()
        days_ago = (now - dt).days
        formatted = f"{dt.strftime('%Y/%m/%d')} ({days_ago}日前)"
        return formatted, days_ago
    except Exception:
        return "公開日不明", 9999


def format_search_query(query: str) -> str:
    if not query:
        return query
    cleaned = re.sub(r'\d+\.|\d+[\.\s、,]', ' ', query)
    cleaned = re.sub(r'[,、/\n]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else query


class YouTubeService:
    def __init__(self):
        pass

    def fetch_videos(
        self, 
        theme: str, 
        custom_keyword: Optional[str] = None, 
        min_duration: int = 300, 
        max_duration: int = 1200, 
        only_recent: bool = False,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        if custom_keyword and custom_keyword.strip():
            query = format_search_query(custom_keyword)
        else:
            keywords = THEME_KEYWORDS.get(theme, [f"{theme} 解説"])
            query = random.choice(keywords)

        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
            'no_warnings': True,
            'default_search': f'ytsearch{limit * 3}'
        }

        videos = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{limit * 3}:{query}", download=False)
                entries = info.get('entries', [])

                for entry in entries:
                    duration = entry.get('duration')
                    if duration is None:
                        continue
                    
                    if min_duration <= duration <= max_duration:
                        video_id = entry.get('id')
                        title = entry.get('title', '無題')
                        channel = entry.get('uploader') or entry.get('channel', '不明')
                        description = entry.get('description', '')
                        upload_date_str = entry.get('upload_date')
                        
                        date_formatted, days_ago = parse_upload_date(upload_date_str)

                        if only_recent and days_ago > 30:
                            continue

                        if video_id:
                            # ⚡ KEY POINTSの抽出生成
                            key_pts = extract_key_points(video_id, description)

                            videos.append({
                                'id': video_id,
                                'title': title,
                                'duration': duration,
                                'duration_formatted': f"{duration // 60}分{duration % 60:02d}秒",
                                'channel': channel,
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'theme': theme if not custom_keyword else query,
                                'upload_date_formatted': date_formatted,
                                'days_ago': days_ago,
                                'key_points': key_pts,
                                'summary': clean_and_summarize(description)
                            })
        except Exception as e:
            print(f"yt-dlp search error: {e}")

        if not videos:
            preset = PRESET_VIDEOS.get(theme, PRESET_VIDEOS.get("AI", []))
            for item in preset:
                item_copy = item.copy()
                item_copy['duration_formatted'] = f"{item_copy['duration'] // 60}分{item_copy['duration'] % 60:02d}秒"
                item_copy['url'] = f"https://www.youtube.com/watch?v={item_copy['id']}"
                if only_recent and item_copy.get('days_ago', 0) > 30:
                    continue
                videos.append(item_copy)

        return videos

    def pick_random_video(self, videos: List[Dict[str, Any]], watched_ids: set) -> tuple[Optional[Dict[str, Any]], bool]:
        if not videos:
            return None, False

        unwatched_videos = [v for v in videos if v['id'] not in watched_ids]

        if unwatched_videos:
            return random.choice(unwatched_videos), False
        else:
            return random.choice(videos), True
