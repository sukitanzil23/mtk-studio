"""MTK Studio -- USB device polling for MediaTek detection."""
import threading
import time

MEDIATEK_VID = 0x0E8D
BROM_PID = 0x0003
PRELOADER_PID = 0x2000
POLL_INTERVAL = 2  # seconds


class UsbMonitor:
    def __init__(self, on_connected, on_disconnected, mock_mode=False):
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.mock_mode = mock_mode
        self._running = False
        self._thread = None
        self._last_connected = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        if self.mock_mode:
            self._run_mock()
        else:
            self._run_real()

    def _run_mock(self):
        """Simulate device appearing after 3 seconds in mock mode."""
        time.sleep(3)
        if self._running and not self._last_connected:
            self._last_connected = True
            try:
                self.on_connected({
                    'chipset': 'MT6765',
                    'description': 'Helio P35',
                    'hwcode': '0x0766',
                    'is_brom': True,
                    'port': 'COM3 (Mock)',
                    'mode': 'BROM'
                })
            except Exception:
                pass

    def _run_real(self):
        """Poll for real MediaTek USB devices."""
        try:
            import usb.core
        except ImportError:
            # pyusb not available -- skip real USB polling
            return

        while self._running:
            try:
                found = None
                devices = list(usb.core.find(find_all=True, idVendor=MEDIATEK_VID) or [])
                for dev in devices:
                    pid = dev.idProduct
                    if pid in (BROM_PID, PRELOADER_PID):
                        mode = 'BROM' if pid == BROM_PID else 'Preloader'
                        found = {
                            'chipset': 'MTK',
                            'description': 'MediaTek Device',
                            'hwcode': hex(pid),
                            'is_brom': pid == BROM_PID,
                            'port': 'USB',
                            'mode': mode
                        }
                        break

                if found and not self._last_connected:
                    self._last_connected = True
                    try:
                        self.on_connected(found)
                    except Exception:
                        pass
                elif not found and self._last_connected:
                    self._last_connected = False
                    try:
                        self.on_disconnected()
                    except Exception:
                        pass
            except Exception:
                pass
            time.sleep(POLL_INTERVAL)
