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
        return str(s).replace('\\', '\\\\').replace("'", "\\'")\
                     .replace('\n', '\\n').replace('\r', '')

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
        """Bug 2 fix: check if a bypass thread is actively running."""
        return (self._bypass_thread is not None
                and self._bypass_thread.is_alive())

    def _reset_state(self):
        """Bug 4 fix: clean up bridge and thread refs after completion/cancel."""
        self._bridge = None
        self._bypass_thread = None
        with self._status_lock:
            self._status = {'step': 'idle', 'state': 'idle', 'progress': 0}

    def _run_bypass(self):
        """Thread target -- runs bypass then resets state."""
        try:
            self._bridge.connect_and_erase_frp()
        finally:
            # Bug 4 fix: always reset after the thread finishes
            self._reset_state()

    def start_frp_bypass(self):
        try:
            # Bug 2 fix: reject if already running
            if self._is_bypass_running():
                return {'error': 'Bypass already in progress'}
            self._bridge = self._get_bridge()
            with self._status_lock:
                self._status = {'step': 'starting', 'state': 'Initializing...', 'progress': 0}
            self._bypass_thread = threading.Thread(
                target=self._run_bypass,
                daemon=True
            )
            self._bypass_thread.start()
            return {'status': 'started'}
        except Exception as e:
            return {'error': str(e)}

    def cancel_frp_bypass(self):
        try:
            if self._bridge:
                self._bridge.cancel()
                with self._status_lock:
                    self._status = {'step': 'cancelled', 'state': 'Cancelled by user', 'progress': 0}
            return {'status': 'cancelled'}
        except Exception as e:
            return {'error': str(e)}

    def get_device_info(self):
        try:
            if self._bridge:
                return self._bridge.get_device_info()
            # Bug 3 fix: return empty dict instead of None
            return {'error': 'No active connection', 'chipset': None, 'port': None}
        except Exception as e:
            return {'error': str(e)}

    def get_bypass_status(self):
        try:
            # Bug 1 fix: return actual tracked status instead of hardcoded idle
            with self._status_lock:
                return dict(self._status)
        except Exception as e:
            return {'error': str(e)}

    def get_mock_mode(self):
        try:
            return bool(self.config.get('mock_mode'))
        except Exception as e:
            return {'error': str(e)}

    def set_mock_mode(self, enabled):
        try:
            self.config.set('mock_mode', bool(enabled))
            self.config.save()
            # Restart USB monitor with updated mode
            if self._usb_monitor:
                self._usb_monitor.stop()
            self._usb_monitor = UsbMonitor(
                on_connected=self._on_device_connected,
                on_disconnected=self._on_device_disconnected,
                mock_mode=bool(enabled)
            )
            self._usb_monitor.start()
            return {'status': 'ok', 'mock_mode': bool(enabled)}
        except Exception as e:
            return {'error': str(e)}

    def get_settings(self):
        try:
            return {
                'mock_mode': bool(self.config.get('mock_mode')),
                'last_port': self.config.get('last_port'),
                'da_path': self.config.get('da_path')
            }
        except Exception as e:
            return {'error': str(e)}

    def save_settings(self, settings):
        try:
            for k, v in settings.items():
                self.config.set(k, v)
            self.config.save()
            return {'status': 'ok'}
        except Exception as e:
            return {'error': str(e)}

    def browse_da_file(self):
        """Open a native file dialog to pick a DA loader (.bin) file."""
        try:
            if not self.window:
                return {'error': 'Window not ready'}
            result = self.window.create_file_dialog(
                dialog_type=10,  # OPEN_DIALOG
                allow_multiple=False,
                file_types=('DA Loader Files (*.bin)|*.bin',
                            'All Files (*.*)|*.*')
            )
            if result and len(result) > 0:
                path = result[0]
                if os.path.isfile(path):
                    self.config.set('da_path', path)
                    self.config.save()
                    return {'status': 'ok', 'da_path': path}
            return {'status': 'cancelled'}
        except Exception as e:
            return {'error': str(e)}

    def clear_da_path(self):
        """Remove the custom DA path, reverting to built-in DA loaders."""
        try:
            self.config.set('da_path', None)
            self.config.save()
            return {'status': 'ok'}
        except Exception as e:
            return {'error': str(e)}

    def get_operation_history(self):
        try:
            return self.config.get('operation_history') or []
        except Exception as e:
            return {'error': str(e)}

    def get_usb_status(self):
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            mtk_ports = [p for p in ports if 'MediaTek' in (p.description or '')
                         or 'MTK' in (p.description or '')
                         or (p.vid == 0x0E8D if p.vid else False)]
            if mtk_ports:
                p = mtk_ports[0]
                return {
                    'connected': True,
                    'port': p.device,
                    'mode': 'Detected',
                    'device': {'chipset': 'MTK', 'description': p.description, 'port': p.device}
                }
            return {'connected': False, 'port': None, 'mode': None, 'device': None}
        except Exception:
            return {'connected': False, 'port': None, 'mode': None, 'device': None}
