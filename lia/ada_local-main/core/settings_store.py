"""
Centralized settings storage with persistence.
Saves settings to ~/.pocket_ai/settings.json
Optimized for LIA - Algerian AI Assistant.
"""

import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal


# الإعدادات الافتراضية - مخصصة لـ LIA
DEFAULT_SETTINGS = {
    "theme": "Dark",
    "ollama_url": "http://localhost:11434",
    "models": {
        "chat": "qwen3:1.7b",  # موديل سريع جداً للاستجابة الفورية
        "web_agent": "qwen3-vl:4b",
    },
    "web_agent_params": {
        "temperature": 0.8,    # تم تقليلها قليلاً لتكون مرحة وفي نفس الوقت دقيقة
        "top_k": 40,
        "top_p": 0.9
    },
    "tts": {
        "voice": "ar-DZ-AminaNeural", # صوت "أمينة" الجزائري الأنثوي (الأفضل للمرح والسرعة)
        "language": "ar_DZ",
        "speed": 1.1                  # زيادة السرعة قليلاً لتكون استجابتها "فايقة"
    },
    "general": {
        "assistant_name": "LIA",      # تغيير الاسم إلى ليا
        "max_history": 15,            # تقليل التاريخ قليلاً لتسريع معالجة الذاكرة
        "auto_fetch_news": True,
        "personality": "Cheerful and witty Algerian girl" # نبرة الشخصية
    },
    "weather": {
        "latitude": 36.7538,
        "longitude": 3.0588,
        "city": "Algeria"
    }
}


class SettingsStore(QObject):
    """
    مدير الإعدادات الآمن مع دعم الإشارات لضمان استجابة الواجهة بسرعة.
    """
    
    setting_changed = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
        self._settings: Dict[str, Any] = {}
        self._settings_dir = Path.home() / ".pocket_ai"
        self._settings_file = self._settings_dir / "settings.json"
        
        self._load()
    
    def _load(self):
        """تحميل الإعدادات أو تهيئة LIA لأول مرة."""
        with self._lock:
            if self._settings_file.exists():
                try:
                    with open(self._settings_file, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    self._settings = self._deep_merge(DEFAULT_SETTINGS.copy(), loaded)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[Settings] Error: {e}. Resetting to LIA defaults.")
                    self._settings = DEFAULT_SETTINGS.copy()
            else:
                self._settings = DEFAULT_SETTINGS.copy()
                self._save()
    
    def _save(self):
        """حفظ الإعدادات مع دعم الحروف العربية."""
        with self._lock:
            try:
                self._settings_dir.mkdir(parents=True, exist_ok=True)
                with open(self._settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self._settings, f, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"[Settings] Save error: {e}")
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        with self._lock:
            keys = key_path.split('.')
            value = self._settings
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default
    
    def set(self, key_path: str, value: Any):
        with self._lock:
            keys = key_path.split('.')
            target = self._settings
            for k in keys[:-1]:
                if k not in target: target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            self._save()
        
        self.setting_changed.emit(key_path, value)

    def reset_to_defaults(self):
        with self._lock:
            self._settings = DEFAULT_SETTINGS.copy()
            self._save()
        self.setting_changed.emit("*", None)

settings = SettingsStore()ا