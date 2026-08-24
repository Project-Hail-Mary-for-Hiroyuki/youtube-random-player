import random
import yt_dlp
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

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
            "summary": "AIの基本的な概念から、仕事や日常生活での最新活用シーンまで初心者向けにわかりやすく解説した動画です。"
        },
        {
            "id": "L_LUpnjgPso", 
            "title": "ChatGPT実践活用法まとめ", 
            "duration": 900, 
            "channel": "テック解説", 
            "theme": "AI",
            "upload_date_formatted": "2026-08-18 (6日前)",
            "days_ago": 6,
            "summary": "ChatGPTをプロのように使いこなすためのプロンプト作成テクニックと具体例を凝縮して紹介します。"
        }
    ],
    "英語": [
        {
            "id": "juKd26qk5S0", 
            "title": "【有料級】英語が聞き取れるようになるリスニング勉強法", 
            "duration": 720, 
            "channel": "英語ラウンジ", 
            "theme": "英語",
            "upload_date_formatted": "2026/08/05 (19日前)",
            "days_ago": 19,
            "summary": "ネイティブの発音ルール（音の連結・脱落）を理解し、最短でリスニング力を向上させるステップを解説。"
        }
    ],
    "思考法": [
        {
            "id": "w9S68n_3Zms", 
            "title": "頭が良い人の思考パターンと問題解決アプローチ", 
            "duration": 850, 
            "channel": "思考ラボ", 
            "theme": "思考法",
            "upload_date_formatted": "2026/08/12 (12日前)",
            "days_ago": 12,
            "summary": "複雑な課題をシンプルに整理・分解して根本解決に導くロジカルシンキングの実践フレームワークを伝授します。"
        }
    ]
}

def clean_and_summarize(description: Optional[str]) -> str:
    if not description or not description.strip():
        return "この動画のテキスト概要はありません。動画をご視聴ください。"

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


def parse_upload_date(upload_date_str: Optional[str]) -> tuple[str, int]:
    """YYYYMMDD 文字列からフォーマット済み日付と経過日数を返す"""
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
        """
        指定テーマ・キーワードに沿って YouTube 動画を検索
        min_duration〜max_duration の長さ制限と only_recent (30日以内) フィルタを適用
        """
        if custom_keyword and custom_keyword.strip():
            query = custom_keyword.strip()
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
                    
                    # 1. 時間制限フィルタ
                    if min_duration <= duration <= max_duration:
                        video_id = entry.get('id')
                        title = entry.get('title', '無題')
                        channel = entry.get('uploader') or entry.get('channel', '不明')
                        description = entry.get('description', '')
                        upload_date_str = entry.get('upload_date')
                        
                        date_formatted, days_ago = parse_upload_date(upload_date_str)

                        # 2. 1ヶ月以内 (30日以内) フィルタ
                        if only_recent and days_ago > 30:
                            continue

                        if video_id:
                            videos.append({
                                'id': video_id,
                                'title': title,
                                'duration': duration,
                                'duration_formatted': f"{duration // 60}分{duration % 60:02d}秒",
                                'channel': channel,
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'theme': theme if not custom_keyword else custom_keyword,
                                'upload_date_formatted': date_formatted,
                                'days_ago': days_ago,
                                'summary': clean_and_summarize(description)
                            })
        except Exception as e:
            print(f"yt-dlp search error: {e}")

        # フォールバック
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
