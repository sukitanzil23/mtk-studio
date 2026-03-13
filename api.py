"""MTK Studio -- Python API exposed to JavaScript via pywebview."""
import json
import os
import threading
from config import AppConfig
from mock import MockBridge
from bridge import MtkBridge
from usb_monitor import UsbMonitor


class Api:
    def __init__(self):
        self.window = None
        self.config = AppConfig()
        self.config.load()
        self._bridge = None
        self._bypass_thread = None
        self._op_thread = None          # thread for phase-2 operations
        self._usb_monitor = None
        # Bug 1 fix: track bypass status internally so get_bypass_status() returns real data
        self._status = {'step': 'idle', 'state': 'idle', 'progress': 0}
        self._status_lock = threading.Lock()

    def set_window(self, window):
        self.window = window
        mock_mode = self.config.get('mock_mode') or False
        self._usb_monitor = UsbMonitor(
            on_connected=self._on_device_connected,
            on_disconnected=self._on_device_disconnected,
            mock_mode=mock_mode
        )
        self._usb_monitor.start()

    def _get_bridge(self):
        if self.config.get('mock_mode'):
            return MockBridge(
                on_log=self._on_log,
                on_progress=self._on_progress,
                on_status=self._on_status
            )
        da_path = self.config.get('da_path')
        return MtkBridge(
            on_log=self._on_log,
            on_progress=self._on_progress,
            on_status=self._on_status,
            da_path=da_path
        )

    def _safe_js_string(self, s):
        """Escape a string for safe interpolation into a JS single-quoted string."""
        return str(s).replace('\\', '\\\\').replace("'", "\\'")                     .replace('\n', '\\n').replace('\r', '')

    def _on_log(self, message):
        if self.window:
            safe = self._safe_js_string(message)
            self.window.evaluate_js(f"window.addLog(\'{safe}\')")

    def _on_progress(self, percent):
        # Bug 1 fix: capture progress into _status
        with self._status_lock:
            self._status['progress'] = int(percent)
        if self.window:
            self.window.evaluate_js(f'window.updateProgress({int(percent)})')

    def _on_status(self, status_dict):
        # Bug 1 fix: capture full status dict
        with self._status_lock:
            self._status.update(status_dict)
        if self.window:
            self.window.evaluate_js(f'window.updateStatus({json.dumps(status_dict)})')

    def _on_device_connected(self, info):
        if self.window:
            self.window.evaluate_js(f'window.onDeviceConnected({json.dumps(info)})')

    def _on_device_disconnected(self):
        if self.window:
            self.window.evaluate_js('window.onDeviceDisconnected()')

    def _is_bypass_running(self):
        """Check if a bypass/detect thread is actively running."""
        return (self._bypass_thread is not None
                and self._bypass_thread.is_alive())

    def _is_op_running(self):
        """Check if an operation thread is actively running."""
        return (self._op_thread is not None
                and self._op_thread.is_alive())

    def _reset_state(self):
        """Reset internal status back to idle."""
        with self._status_lock:
            self._status = {'step': 'idle', 'state': 'idle', 'progress': 0}
        self._bridge = None

    # -----------------------------------------------------------------
    # Exposed API (called from JavaScript)
    # -----------------------------------------------------------------

    def start_frp_bypass(self):
        """Phase 1: Launch detection flow in background thread.

        Runs setup -> connect -> detect, then STOPS at step 3 so the
        user can choose an operation (FRP erase, factory reset, or
        read partitions).
        """
        if self._is_bypass_running():
            return json.dumps({'ok': False, 'error': 'Detection already running'})
        self._reset_state()
        self._bridge = self._get_bridge()
        self._bypass_thread = threading.Thread(
            target=self._bridge.connect_and_detect, daemon=True
        )
        self._bypass_thread.start()
        return json.dumps({'ok': True})

    def start_frp_erase(self):
        """Phase 2a: Erase FRP partition only (user picked FRP Bypass)."""
        if not self._bridge:
            return json.dumps({'ok': False, 'error': 'No device detected. Run detection first.'})
        if self._is_op_running():
            return json.dumps({'ok': False, 'error': 'Operation already running'})
        self._op_thread = threading.Thread(
            target=self._bridge.erase_frp, daemon=True
        )
        self._op_thread.start()
        return json.dumps({'ok': True})

    def start_factory_reset(self):
        """Phase 2b: Factory reset + FRP erase (user picked Factory Reset)."""
        if not self._bridge:
            return json.dumps({'ok': False, 'error': 'No device detected. Run detection first.'})
        if self._is_op_running():
            return json.dumps({'ok': False, 'error': 'Operation already running'})
        self._op_thread = threading.Thread(
            target=self._bridge.factory_reset, daemon=True
        )
        self._op_thread.start()
        return json.dumps({'ok': True})

    def read_partitions(self):
        """Phase 2c: Read partition table (user picked Read Partitions)."""
        if not self._bridge:
            return json.dumps({'ok': False, 'error': 'No device detected. Run detection first.'})
        if self._is_op_running():
            return json.dumps({'ok': False, 'error': 'Operation already running'})
        self._op_thread = threading.Thread(
            target=self._bridge.read_partitions, daemon=True
        )
        self._op_thread.start()
        return json.dumps({'ok': True})

    def cancel_frp_bypass(self):
        if self._bridge:
            self._bridge.cancel()
            self._on_status({'step': 'cancelled', 'state': 'Bypass cancelled by user'})
        return json.dumps({'ok': True})

    def get_bypass_status(self):
        with self._status_lock:
            return json.dumps(self._status.copy())

    def get_settings(self):
        return json.dumps({
            'mock_mode': bool(self.config.get('mock_mode')),
            'da_path': self.config.get('da_path') or '',
            'theme': self.config.get('theme') or 'system',
        })

    def save_settings(self, settings_json):
        try:
            settings = json.loads(settings_json)
            for key in ('mock_mode', 'da_path', 'theme'):
                if key in settings:
                    self.config.set(key, settings[key])
            self.config.save()
            return json.dumps({'ok': True})
        except Exception as e:
            return json.dumps({'ok': False, 'error': str(e)})

    def get_app_info(self):
        return json.dumps({
            'app_name': 'MTK Studio',
            'version': '0.1.0-alpha',
            'mtkclient': 'bundled v2.0',
            'python': f'{os_info}' if (os_info := f'{os.name}/{os.sys.platform}') else '',
        })
