"""MTK Studio -- App configuration and settings persistence."""
import json
from pathlib import Path


class AppConfig:
    CONFIG_DIR = Path.home() / '.mtk-studio'
    CONFIG_FILE = CONFIG_DIR / 'config.json'
    MAX_HISTORY = 1000

    DEFAULTS = {
        'mock_mode': False,
        'last_port': None,
        'operation_history': [],
    }

    def __init__(self):
        self._data = {k: v for k, v in self.DEFAULTS.items()}

    def get(self, key):
        return self._data.get(key, self.DEFAULTS.get(key))

    def set(self, key, value):
        """Set a config value. For operation_history, use append_history() instead."""
        self._data[key] = value

    def append_history(self, entry):
        """Append an operation record to history, enforcing MAX_HISTORY cap."""
        hist = self._data.get('operation_history', [])
        hist.append(entry)
        if len(hist) > self.MAX_HISTORY:
            hist = hist[-self.MAX_HISTORY:]
        self._data['operation_history'] = hist

    def load(self):
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                self._data.update(saved)
        except Exception:
            pass  # Use defaults on any error

    def save(self):
        try:
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass
