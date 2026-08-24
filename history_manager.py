import json
import os
from typing import List, Dict, Any

HISTORY_FILE = "history.json"

class HistoryManager:
    def __init__(self, file_path: str = HISTORY_FILE):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            self.save_history([])

    def load_history(self) -> List[Dict[str, Any]]:
        """保存されている再生履歴を取得"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return []

    def save_history(self, history: List[Dict[str, Any]]):
        """再生履歴を保存"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def add_to_history(self, video_data: Dict[str, Any]):
        """新しい動画を履歴に追加（最大100件保存）"""
        history = self.load_history()
        # 重複削除（既存の同じ動画IDがあれば一度取り除く）
        history = [item for item in history if item.get("id") != video_data.get("id")]
        # 先頭に最新の動画を挿入
        history.insert(0, video_data)
        # 最大100件に保持
        if len(history) > 100:
            history = history[:100]
        self.save_history(history)

    def get_watched_ids(self) -> set:
        """視聴済み動画IDのセットを取得"""
        history = self.load_history()
        return {item["id"] for item in history if "id" in item}

    def clear_history(self):
        """履歴をクリア"""
        self.save_history([])
