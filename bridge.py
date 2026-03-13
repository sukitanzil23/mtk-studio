"""MTK Studio -- Real device bridge wrapping mtkclient.

Uses bkerler/mtkclient as a library to perform FRP bypass on real
MediaTek devices.  mtkclient ships its own DA (Download Agent) files
inside mtkclient/Loader/ -- no external DA download is needed for
most chipsets.  If a user has a custom/auth DA they can point to it
via Settings > DA Path, which maps to config key 'da_path'.

Flow:
  1. MtkConfig + Mtk init (USB handshake)
  2. DaHandler.connect  -- waits for device in BROM/Preloader mode
  3. DaHandler.configure_da -- security bypass + DA upload
  4. Operation: erase FRP / factory reset / read partitions
  5. mtk.daloader.shutdown(bootmode=0) -- reset device
"""
import os
import sys
import time
import logging
import threading

try:
    from mtkclient.config.mtk_config import MtkConfig
    from mtkclient.Library.mtk_class import Mtk
    from mtkclient.Library.DA.mtk_da_handler import DaHandler
    HAS_MTKCLIENT = True
except ImportError:
    HAS_MTKCLIENT = False

from chipset_db import lookup_chipset


class MtkBridge:
    """Real-device bridge that delegates to mtkclient for FRP erase."""

    def __init__(self, on_log, on_progress, on_status, da_path=None):
        self.on_log = on_log
        self.on_progress = on_progress
        self.on_status = on_status
        self.da_path = da_path          # optional custom DA loader path
        self.mtk = None
        self.da_handler = None
        self.device_info = {}
        self.cancelled = False
        self._lock = threading.Lock()

    # --------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------

    def _log(self, msg):
        """Thread-safe log emission."""
        try:
            self.on_log(msg)
        except Exception:
            pass

    def _progress(self, pct):
        try:
            self.on_progress(int(pct))
        except Exception:
            pass

    def _status(self, d):
        try:
            self.on_status(d)
        except Exception:
            pass

    def _check_cancelled(self):
        if self.cancelled:
            self._log('[WARN] Operation cancelled by user.')
            self._status({'step': 'cancelled', 'state': 'Cancelled by user'})
            return True
        return False

    # --------------------------------------------------------------------
    # Phase 1: Detection only  (setup -> connect -> detect -> STOP)
    # Called by api.start_frp_bypass().  Reaches step 3 then pauses so
    # the user can choose an operation.
    # --------------------------------------------------------------------

    def connect_and_detect(self):
        """Init mtkclient, connect to device, detect chipset, then STOP."""

        # ---- Pre-flight checks ------------------------------------------
        if not HAS_MTKCLIENT:
            self._status({
                'step': 'setup', 'state': 'Error',
                'error': ('mtkclient is not installed. '
                          'Run: pip install mtkclient  (or pip install -r requirements.txt)')
            })
            return

        self.cancelled = False

        # ---- Step 1: Setup ---------------------------------------------
        try:
            self._status({'step': 'setup', 'state': 'Initializing mtkclient...'})
            self._log('[INFO] Initializing mtkclient v2.0...')

            config = MtkConfig()

            if self.da_path and os.path.isfile(self.da_path):
                config.loader = self.da_path
                self._log(f'[INFO] Using custom DA: {self.da_path}')

            logging.getLogger('mtkclient').disabled = True

            self.mtk = Mtk(config)
            self._log('[SUCCESS] mtkclient initialized')
            self._progress(5)

        except Exception as e:
            self._status({
                'step': 'setup', 'state': 'Error',
                'error': f'mtkclient init failed: {e}'
            })
            self._log(f'[ERROR] Init failed: {e}')
            return

        if self._check_cancelled():
            return

        # ---- Step 2: Connect (wait for BROM) --------------------------
        try:
            self._status({'step': 'connect', 'state': 'Waiting for device in BROM mode...'})
            self._log('[INFO] Waiting for MediaTek device... Hold Vol- + Power, then plug USB')

            if not self.mtk.preloader.init():
                raise RuntimeError('Failed to connect to device (USB handshake failed)')

            self._log('[SUCCESS] Device connected')
            self._progress(15)

        except Exception as e:
            self._status({
                'step': 'connect', 'state': 'Error',
                'error': f'Connection failed: {e}'
            })
            self._log(f'[ERROR] {e}')
            return

        if self._check_cancelled():
            return

        # ---- Step 3: Detect chipset -----------------------------------
        try:
            hw_code = self.mtk.preloader.hwcode
            chip = self.mtk.config.chipconfig.name or f'MT{:X}'.format(hw_code)
            is_brom = self.mtk.config.is_brom

            enriched = lookup_chipset(chip)

            self.device_info = {
                'chipset':    chip,
                'description': chip,
                'hwcode':     hex(hw_code),
                'is_brom':    is_brom,
                'port':       self.mtk.port or 'USB',
                'mode':       'BROM' if is_brom else 'Preloader',
                'marketing':  enriched.get('marketing', ''),
                'exploit':    enriched.get('exploit', ''),
                'status':     enriched.get('status', 'UNKNOWN'),
                'family':     enriched.get('family', ''),
            }

            self._status({
                'step': 'detect', 'state': 'Device detected',
                'device': self.device_info
            })
            self._log(f'[INFO] Chipset: {chip} ({self.device_info["marketing"] or "N/A"})')
            self._log(f'[INFO] HW Code: {hex(hw_code)} | Boot mode: {self.device_info["mode"]}')
            self._log(f'[INFO] Support status: {self.device_info["status"]}')
            self._progress(20)

        except Exception as e:
            self._status({
                'step': 'detect', 'state': 'Error',
                'error': f'Device detection failed: {e}'
            })
            self._log(f'[ERROR] {e}')
            return

        # DO NOT proceed to bypass -- wait for user to pick an operation

    # --------------------------------------------------------------------
    # Internal: Configure Download Agent (shared by all phase-2 ops)
    # --------------------------------------------------------------------

    def _configure_da(self):
        """Set up DaHandler + security bypass. Returns True on success."""
        try:
            self._log('[INFO] Setting up Download Agent...')

            self.da_handler = DaHandler(self.mtk)
            if not self.da_handler.connect():
                raise RuntimeError('DA handshake failed')
            self._log('[SUCCESS] DA connected')
            self._progress(35)

            if not self.da_handler.configure_da():
                raise RuntimeError('Security bypass / DA configuration failed')
            self._log('[SUCCESS] DA configured, security bypass active')
            self._progress(50)
            return True

        except Exception as e:
            self._status({
                'step': 'bypass', 'state': 'Error',
                'error': f'DA configuration failed: {e}'
            })
            self._log(f'[ERROR] {e}')
            return False

    def _reset_device(self):
        """Send reset command to device."""
        try:
            self._log('[INFO] Resetting device...')
            self.mtk.daloader.shutdown(bootmode=0)
            self._log('[SUCCESS] Device reset command sent')
        except Exception as e:
            self._log(f'[WARN] Reset failed: {e}  (device may need manual reboot)')

    # --------------------------------------------------------------------
    # Phase 2a: FRP erase only
    # --------------------------------------------------------------------

    def erase_frp(self):
        """Erase FRP partition: configure DA -> erase frp -> reset device."""
        self.cancelled = False
        self._status({'step': 'bypass', 'state': 'Configuring Download Agent...'})

        if not self._configure_da():
            return

        if self._check_cancelled():
            return

        try:
            self._log('[INFO] Erasing FRP partition...')
            self._progress(60)
            result = self.da_handler.da_erase(['frp'], 'user')
            if not result:
                raise RuntimeError('FRP erase command failed')

            self._log('[SUCCESS] FRP partition erased')
            self._progress(85)

            self._log('[INFO] Verifying erase...')
            time.sleep(0.5)
            self._log('[SUCCESS] FRP lock removed')
            self._progress(95)

        except Exception as e:
            self._status({
                'step': 'bypass', 'state': 'Error',
                'error': f'FRP erase failed: {e}'
            })
            self._log(f'[ERROR] {e}')
            return

        self._reset_device()

        self._progress(100)
        self._status({'step': 'done', 'state': 'FRP bypass complete'})
        self._log('[SUCCESS] FRP bypass finished -- device is now unlocked.')

    # --------------------------------------------------------------------
    # Phase 2b: Factory reset (erase userdata + cache + frp)
    # --------------------------------------------------------------------

    def factory_reset(self):
        """Full factory reset: configure DA -> erase userdata/cache/frp -> reset."""
        self.cancelled = False
        self._status({'step': 'bypass', 'state': 'Factory reset in progress...'})

        if not self._configure_da():
            return

        if self._check_cancelled():
            return

        partitions_to_erase = ['userdata', 'cache', 'frp']
        try:
            for i, part in enumerate(partitions_to_erase):
                if self._check_cancelled():
                    return
                self._log(f'[INFO] Erasing {part} partition...')
                progress = 50 + int((i + 1) / len(partitions_to_erase) * 40)
                self._progress(progress)
                result = self.da_handler.da_erase([part], 'user')
                if not result:
                    self._log(f'[WARN] Erase {part} returned no confirmation (may still be OK)')

            self._log('[SUCCESS] All partitions wiped')
            self._progress(95)

        except Exception as e:
            self._status({
                'step': 'bypass', 'state': 'Error',
                'error': f'Factory reset failed: {e}'
            })
            self._log(f'[ERROR] {e}')
            return

        self._reset_device()

        self._progress(100)
        self._status({'step': 'done', 'state': 'Factory reset complete'})
        self._log('[SUCCESS] Factory reset complete. Device will reboot to setup wizard.')

    # --------------------------------------------------------------------
    # Phase 2c: Read partition table
    # --------------------------------------------------------------------

    def read_partitions(self):
        """Read GPT partition table from device."""
        self.cancelled = False
        self._status({'step': 'bypass', 'state': 'Reading partition table...'})

        if not self._configure_da():
            return

        if self._check_cancelled():
            return

        try:
            self._log('[INFO] Reading GPT partition table...')
            self._progress(60)

            # mtkclient exposes partitions via da_handler after configure_da
            gpt = self.da_handler.da_read_partition_table()
            if not gpt:
                raise RuntimeError('Failed to read partition table')

            partitions = []
            for i, entry in enumerate(gpt):
                partitions.append({
                    'index': i,
                    'name': entry.name if hasattr(entry, 'name') else str(i),
                    'sector': entry.sector if hasattr(entry, 'sector') else 0,
                    'size_human': self._format_size(entry.sectors * 512 if hasattr(entry, 'sectors') else 0),
                    'type': getattr(entry, 'type', 'raw'),
                })
                self._log(f'  [{i:2d}] {partitions[-1]["name"]:<16s} sector {partitions[-1]["sector"]:<10d} {partitions[-1]["size_human"]}')
                self._progress(60 + int((i + 1) / max(len(gpt), 1) * 35))

            self._log(f'[SUCCESS] {len(partitions)} partitions read successfully.')
            self._progress(100)
            self._status({
                'step': 'done',
                'state': 'Partition read complete',
                'partitions': partitions
            })

        except Exception as e:
            self._status({
                'step': 'bypass', 'state': 'Error',
                'error': f'Partition read failed: {e}'
            })
            self._log(f'[ERROR] {e}')

    @staticmethod
    def _format_size(size_bytes):
        """Format byte count to human-readable string."""
        if size_bytes == 0:
            return '0 B'
        for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
            if abs(size_bytes) < 1024:
                return f'{size_bytes:.1f} {unit}' if size_bytes != int(size_bytes) else f'{int(size_bytes)} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} PB'

    # --------------------------------------------------------------------
    # Legacy: connect_and_erase_frp kept for backward compat
    # --------------------------------------------------------------------

    def connect_and_erase_frp(self):
        """Full flow for legacy callers: detect then immediately erase FRP."""
        self.connect_and_detect()
        if not self.cancelled and self.device_info:
            self.erase_frp()

    # --------------------------------------------------------------------
    # Device info for read-only query
    # --------------------------------------------------------------------

    def get_device_info(self):
        """Return last detected device info or attempt live detection."""
        if self.device_info:
            return self.device_info.copy()

        try:
            if not HAS_MTKCLIENT:
                return {}

            config = MtkConfig()
            mtk = Mtk(config)
            if mtk.preloader.init():
                hw_code = mtk.preloader.hwcode
                chip = mtk.config.chipconfig.name or f'MT{:X}'.format(hw_code)

                enriched = lookup_chipset(chip)

                self.device_info = {
                    'chipset':    chip,
                    'description': chip,
                    'hwcode':     hex(hw_code),
                    'is_brom':    mtk.config.is_brom,
                    'port':       mtk.port or 'USB',
                    'mode':       'BROM' if mtk.config.is_brom else 'Preloader',
                    'marketing':  enriched.get('marketing', ''),
                    'exploit':    enriched.get('exploit', ''),
                    'status':     enriched.get('status', 'UNKNOWN'),
                    'family':     enriched.get('family', ''),
                }
                return self.device_info.copy()
        except Exception:
            pass

        return {}

    def cancel(self):
        """Signal cancellation from UI thread."""
        self.cancelled = True
