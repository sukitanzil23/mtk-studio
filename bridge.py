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
  4. DaHandler.da_erase(['frp'], 'user') -- erase FRP partition
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Main FRP bypass flow
    # ------------------------------------------------------------------

    def connect_and_erase_frp(self):
        """Full FRP bypass: init -> connect -> configure DA -> erase frp -> reset."""

        # ---- Pre-flight checks ----------------------------------------
        if not HAS_MTKCLIENT:
            self._status({
                'step': 'setup', 'state': 'Error',
                'error': ('mtkclient is not installed. '
                          'Run: pip install mtkclient  (or pip install -r requirements.txt)')
            })
            self._log('[ERROR] mtkclient package not found. Install it with: pip install mtkclient')
            return

        try:
            self._do_bypass()
        except Exception as exc:
            err_msg = str(exc)
            self._log(f'[ERROR] Unexpected failure: {err_msg}')
            self._status({'step': 'bypass', 'state': 'Error', 'error': err_msg})

    def _do_bypass(self):
        # ---- Step 1: Setup / Init ------------------------------------
        self._status({'step': 'setup', 'state': 'Initializing mtkclient...'})
        self._progress(0)
        self._log('[INFO] Initializing mtkclient...')

        config = MtkConfig(loglevel=logging.INFO, gui=None)

        # If user supplied a custom DA path, inject it
        if self.da_path and os.path.isfile(self.da_path):
            config.loader = self.da_path
            self._log(f'[INFO] Using custom DA loader: {self.da_path}')
        else:
            self._log('[INFO] Using built-in DA loaders (no custom DA needed)')

        mtk = Mtk(config=config, loglevel=logging.INFO)
        self.mtk = mtk
        self._log('[INFO] mtkclient v2 engine ready')
        self._progress(5)

        if self._check_cancelled():
            return

        # ---- Step 2: Connect (wait for BROM/Preloader) ---------------
        self._status({'step': 'connect', 'state': 'Waiting for device in BROM mode...'})
        self._log('[INFO] Waiting for device... Hold Vol-Down + Power, then plug USB')
        self._progress(10)

        da_handler = DaHandler(mtk, loglevel=logging.INFO)
        self.da_handler = da_handler

        mtk = da_handler.connect(mtk, directory='.')
        if mtk is None:
            self._log('[ERROR] Failed to connect to device. Is it in BROM mode?')
            self._status({
                'step': 'connect', 'state': 'Error',
                'error': 'Could not connect to device. Ensure it is powered off, '
                         'hold Vol-Down + Power, then plug USB.'
            })
            return

        self.mtk = mtk
        self._log('[INFO] Device connected via USB')
        self._progress(20)

        if self._check_cancelled():
            return

        # ---- Step 3: Detect chipset & configure DA -------------------
        self._status({'step': 'detect', 'state': 'Detecting chipset & uploading DA...'})
        self._log('[INFO] Identifying chipset and uploading Download Agent...')

        mtk = da_handler.configure_da(mtk)
        if mtk is None:
            self._log('[ERROR] Failed to configure DA. Device may need a custom DA loader.')
            self._status({
                'step': 'detect', 'state': 'Error',
                'error': 'DA configuration failed. Try providing a custom DA via Settings > DA Path.'
            })
            return

        self.mtk = mtk
        self._progress(35)

        # Extract device info from config
        try:
            hwcode = hex(mtk.config.hwcode) if mtk.config.hwcode else 'Unknown'
        except Exception:
            hwcode = 'Unknown'

        try:
            chipname = mtk.config.chipconfig.name or f'MT{hwcode}'
        except Exception:
            chipname = f'MT{hwcode}'

        is_brom = getattr(mtk.config, 'is_brom', False)

        self.device_info = {
            'chipset': chipname,
            'hwcode': hwcode,
            'is_brom': is_brom,
            'mode': 'BROM' if is_brom else 'Preloader',
            'description': chipname,
        }

        self._log(f'[INFO] Chipset: {chipname} (HW code: {hwcode})')
        self._log(f'[INFO] Boot mode: {"BROM" if is_brom else "Preloader"}')
        self._log('[INFO] Download Agent uploaded successfully')
        self._status({
            'step': 'detect', 'state': 'Device detected',
            'device': self.device_info
        })
        self._progress(40)

        if self._check_cancelled():
            return

        # ---- Step 4: Erase FRP partition -----------------------------
        self._status({'step': 'bypass', 'state': 'FRP bypass in progress...'})
        self._log('[INFO] Reading GPT partition table...')
        self._progress(45)

        # Verify FRP partition exists before erasing
        gpt_data = None
        try:
            gpt_data = mtk.daloader.get_partition_data(parttype='user')
            frp_found = False
            for entry in gpt_data:
                if entry.name.lower() == 'frp':
                    frp_found = True
                    pagesize = 512
                    try:
                        pagesize = mtk.daloader.daconfig.pagesize
                    except Exception:
                        pass
                    size_bytes = entry.sectors * pagesize
                    self._log(f'[INFO] FRP partition found: {entry.name} '
                              f'(sector {entry.sector}, {size_bytes} bytes)')
                    break
            if not frp_found:
                # Some devices use 'persist' or 'persistent' instead
                alt_names = ['persist', 'persistent', 'persistdata']
                for entry in gpt_data:
                    if entry.name.lower() in alt_names:
                        frp_found = True
                        self._log(f'[WARN] No "frp" partition found. '
                                  f'Using alternative: {entry.name}')
                        break
                if not frp_found:
                    self._log('[ERROR] FRP partition not found in GPT table.')
                    self._log('[INFO] Available partitions:')
                    for entry in gpt_data:
                        self._log(f'  - {entry.name}')
                    self._status({
                        'step': 'bypass', 'state': 'Error',
                        'error': 'FRP partition not found on this device.'
                    })
                    return
        except Exception as exc:
            self._log(f'[WARN] Could not read GPT: {exc}. Attempting blind erase...')

        self._progress(55)

        if self._check_cancelled():
            return

        # Perform the actual erase
        self._log('[INFO] Erasing FRP partition...')
        self._progress(60)

        try:
            # da_erase expects a list of partition names and parttype
            da_handler.da_erase(partitions=['frp'], parttype='user')
            self._log('[SUCCESS] FRP partition erased')
            self._progress(80)
        except Exception as exc:
            err_msg = str(exc)
            self._log(f'[ERROR] FRP erase failed: {err_msg}')
            self._status({
                'step': 'bypass', 'state': 'Error',
                'error': f'FRP erase failed: {err_msg}'
            })
            return

        if self._check_cancelled():
            return

        # Also erase 'persist' partition if it exists (some devices
        # store FRP data there too)
        if gpt_data:
            try:
                self._log('[INFO] Checking for persist/persistent partition...')
                for entry in gpt_data:
                    if entry.name.lower() in ('persist', 'persistent'):
                        self._log(f'[INFO] Erasing {entry.name} partition as well...')
                        da_handler.da_erase(partitions=[entry.name], parttype='user')
                        self._log(f'[SUCCESS] {entry.name} partition erased')
                        break
            except Exception:
                pass  # Not critical -- frp was already erased

        self._progress(90)

        # ---- Step 5: Reset device ------------------------------------
        self._log('[INFO] Resetting device...')
        try:
            mtk.daloader.shutdown(bootmode=0)
            self._log('[SUCCESS] Reset command sent. Disconnect USB cable.')
        except Exception:
            self._log('[WARN] Could not send reset. Please power-cycle the device manually.')

        self._progress(100)
        self._status({
            'step': 'done',
            'state': 'FRP bypass completed successfully',
            'device': self.device_info
        })
        self._log('[SUCCESS] FRP lock removed. Device will boot without Google account.')

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def cancel(self):
        self.cancelled = True
        # Try to abort mtkclient operations
        try:
            if self.mtk and hasattr(self.mtk, 'port'):
                self.mtk.port.close()
        except Exception:
            pass

    def get_device_info(self):
        return self.device_info or None
