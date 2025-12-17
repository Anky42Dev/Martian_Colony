# core/save_manager.py
import json
import os


class SaveManager:
    def __init__(self, filename="save.json"):
        self.filename = filename

    def load(self):
        if not os.path.exists(self.filename):
            return None
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Ошибка загрузки сохранения:", e)
            return None

    def save(self, data: dict):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Ошибка сохранения:", e)

    def reset(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
