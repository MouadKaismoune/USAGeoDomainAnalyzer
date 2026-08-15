import json
import os

TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "languages")


class Translator:
    _instance = None
    _current_language = "en"
    _translations = {}
    _callbacks = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_translations()
        return cls._instance

    def _load_all_translations(self):
        self._translations = {}
        if not os.path.exists(TRANSLATIONS_DIR):
            os.makedirs(TRANSLATIONS_DIR)
        for filename in os.listdir(TRANSLATIONS_DIR):
            if filename.endswith(".json"):
                lang_code = filename.replace(".json", "")
                filepath = os.path.join(TRANSLATIONS_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    self._translations[lang_code] = json.load(f)

    def get_available_languages(self):
        return list(self._translations.keys())

    def set_language(self, lang_code: str):
        if lang_code in self._translations:
            self._current_language = lang_code
            for callback in self._callbacks:
                callback(lang_code)

    def on_language_changed(self, callback):
        self._callbacks.append(callback)

    def t(self, key: str, **kwargs) -> str:
        lang_data = self._translations.get(self._current_language, {})
        fallback = self._translations.get("en", {})
        text = lang_data.get(key, fallback.get(key, key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return text

    def get_current_language(self):
        return self._current_language

    def reload(self):
        self._load_all_translations()


translator = Translator()
