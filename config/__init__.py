import json
import os

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_CONFIG = {
    "language": "en",
    "theme": "light",
    "window_width": 1200,
    "window_height": 750,
}


class AppConfig:
    _instance = None
    _data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = cls._instance._load()
        return cls._instance

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return DEFAULT_CONFIG.copy()

    def save(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    @property
    def language(self):
        return self._data.get("language", "en")

    @language.setter
    def language(self, value):
        self._data["language"] = value
        self.save()

    @property
    def theme(self):
        return self._data.get("theme", "light")

    @theme.setter
    def theme(self, value):
        self._data["theme"] = value
        self.save()


config = AppConfig()
