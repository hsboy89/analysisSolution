"""설정 관리 모듈 - API 키, 엔진 선택, 모델 설정 저장/로드"""
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".analysisSolution"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "engine": "claude",  # "claude" or "gemini"
    "claude": {
        "api_key": "",
        "model": "claude-sonnet-4-20250514",
        "models": [
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            "claude-haiku-4-5-20251001",
        ],
    },
    "gemini": {
        "api_key": "",
        "model": "gemini-2.0-flash",
        "models": [
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ],
    },
    "output": {
        "format": "html",  # "html", "pdf", "word"
        "output_dir": "",
    },
    "template": "analysis",  # "analysis" or "report"
}


class Config:
    def __init__(self):
        self._data = {}
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self._data = {**DEFAULT_CONFIG, **saved}
        else:
            self._data = DEFAULT_CONFIG.copy()

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def engine(self):
        return self._data["engine"]

    @engine.setter
    def engine(self, value):
        self._data["engine"] = value

    def get_api_key(self, engine=None):
        engine = engine or self.engine
        return self._data[engine]["api_key"]

    def set_api_key(self, key, engine=None):
        engine = engine or self.engine
        self._data[engine]["api_key"] = key

    def get_model(self, engine=None):
        engine = engine or self.engine
        return self._data[engine]["model"]

    def set_model(self, model, engine=None):
        engine = engine or self.engine
        self._data[engine]["model"] = model

    def get_models(self, engine=None):
        engine = engine or self.engine
        return self._data[engine]["models"]

    @property
    def output_format(self):
        return self._data["output"]["format"]

    @output_format.setter
    def output_format(self, value):
        self._data["output"]["format"] = value

    @property
    def output_dir(self):
        return self._data["output"]["output_dir"]

    @output_dir.setter
    def output_dir(self, value):
        self._data["output"]["output_dir"] = value

    @property
    def template(self):
        return self._data["template"]

    @template.setter
    def template(self, value):
        self._data["template"] = value
