"""MTK Studio -- Mock bridge for testing without real hardware."""
import time
import random


class MockBridge:
    MOCK_DEVICE = {
        'chipset': 'MT6765',
        'description': 'MT6765',
        'hwcode': '0x0766',
        'is_brom': True,
        'port': 'COM3 (Mock)',
        'mode': 'BROM',
        'marketing': 'Helio P35 / G35',
        'exploit': 'kamakiri',
        'status': 'SUPPORTED',
        'family': 'helio',
    }

    FRP_LOG_MESSAGES = [
        '[INFO] Initializing mtkclient...',
        '[INFO] Scanning for USB devices...',
        '[INFO] MediaTek device found (VID=0x0E8D PID=0x0003)',
        '[INFO] Entering BROM handshake...',
        '[INFO] Security bypass active',
        '[INFO] Loading Download Agent...',
        '[INFO] Download Agent authenticated successfully',
        '[INFO] Reading GPT partition table...',
        '[INFO] FRP partition located at 0x00200000 (256KB)',
        '[INFO] Erasing FRP partition...',
        '[SUCCESS] FRP partition wiped (256KB zeroed)',
        '[SUCCESS] Verifying erase result...',
        '[SUCCESS] FRP lock removed. Device will boot without Google account.',
    ]

    MOCK_PARTITIONS = [
        {'index': 0,  'name': 'preloader', 'sector': 0,          'size_human': '256 KB',  'type': 'raw'},
        {'index': 1,  'name': 'proinfo',   'sector': 512,        'size_human': '256 KB',  'type': 'raw'},
        {'index': 2,  'name': 'nvram',     'sector': 1024,       'size_human': '512 KB',  'type': 'raw'},
        {'index': 3,  'name': 'protect1',  'sector': 2048,       'size_human': '10 MB',   'type': 'ext4'},
        {'index': 4,  'name': 'protect2',  'sector': 22528,      'size_human': '10 MB',   'type': 'ext4'},
        {'index': 5,  'name': 'lk',        'sector': 43008,      'size_human': '512 KB',  'type': 'raw'},
        {'index': 6,  'name': 'para',      'sector': 44032,      'size_human': '512 KB',  'type': 'raw'},
        {'index': 7,  'name': 'boot',      'sector': 45056,      'size_human': '32 MB',   'type': 'raw'},
        {'index': 8,  'name': 'recovery',  'sector': 110592,     'size_human': '32 MB',   'type': 'raw'},
        {'index': 9,  'name': 'vbmeta',    'sector': 176128,     'size_human': '64 KB',   'type': 'raw'},
        {'index': 10, 'name': 'metadata',  'sector': 176256,     'size_human': '16 MB',   'type': 'ext4'},
        {'index': 11, 'name': 'frp',       'sector': 209024,     'size_human': '256 KB',  'type': 'raw'},
        {'index': 12, 'name': 'super',     'sector': 209536,     'size_human': '4 GB',    'type': 'raw'},
        {'index': 13, 'name': 'userdata',  'sector': 8598144,    'size_human': '54 GB',   'type': 'ext4'},
    ]

    def __init__(self, on_log, on_progress, on_status):
        self.on_log = on_log
        self.on_progress = on_progress
        self.on_status = on_status
        self.cancelled = False

    # ------------------------------------------------------------------
    # Phase 1: Detection only  (setup -> connect -> detect -> STOP)
    # Called by api.start_frp_bypass().  Reaches step 3 then pauses so
    # the user can choose an operation.
    # ------------------------------------------------------------------

    def connect_and_detect(self):
        """Run setup + connect + detect phases, then STOP at step 3."""
        self.cancelled = False

        # Step 1: Setup
        self.on_status({'step': 'setup', 'state': 'Checking system readiness...'})
        self.on_log('[INFO] Checking USB drivers...')
        time.sleep(0.8)
        self.on_log('[SUCCESS] USB drivers OK')
        time.sleep(0.4)
        self.on_log('[INFO] mtkclient v2.0 initialized')
        time.sleep(0.8)

        if self.cancelled:
            return

        # Step 2: Connect (waiting for BROM)
        self.on_status({'step': 'connect', 'state': 'Waiting for device in BROM mode...'})
        self.on_log('[INFO] Waiting for device... Hold Vol- + Power, then plug USB')
        time.sleep(3)
        self.on_log('[INFO] Device detected on COM3')

        if self.cancelled:
            return

        # Step 3: Detect -- emit device info and STOP here
        device = self.MOCK_DEVICE.copy()
        self.on_status({'step': 'detect', 'state': 'Device detected', 'device': device})
        self.on_log(f'[INFO] Chipset: {device["chipset"]} ({device["description"]})')
        self.on_log(f'[INFO] HW Code: {device["hwcode"]} | Boot mode: BROM')
        # DO NOT proceed to bypass -- wait for user to pick an operation

    # ------------------------------------------------------------------
    # Phase 2 operations -- each called separately after user picks one
    # ------------------------------------------------------------------

    def erase_frp(self):
        """Erase FRP partition only (step 4 -> step 5)."""
        self.cancelled = False

        # 5% simulated failure for error handling testing
        if random.random() < 0.05:
            self.on_status({'step': 'bypass', 'state': 'Error', 'error': 'Simulated USB disconnect during bypass'})
            self.on_log('[ERROR] USB connection lost during bypass. Retry to continue.')
            return

        self.on_status({'step': 'bypass', 'state': 'FRP bypass in progress...'})
        for i, msg in enumerate(self.FRP_LOG_MESSAGES):
            if self.cancelled:
                return
            self.on_log(msg)
            progress = int((i + 1) / len(self.FRP_LOG_MESSAGES) * 100)
            self.on_progress(progress)
            time.sleep(random.uniform(0.4, 1.2))

        # Step 5: Done
        self.on_status({'step': 'done', 'state': 'FRP bypass complete'})
        self.on_log('[SUCCESS] FRP bypass finished -- device is now unlocked.')

    def factory_reset(self):
        """Simulate full factory reset (erase userdata + cache + frp)."""
        self.cancelled = False
        self.on_status({'step': 'bypass', 'state': 'Factory reset in progress...'})

        messages = [
            '[INFO] Starting factory reset...',
            '[INFO] Erasing userdata partition...',
            '[INFO] Erasing cache partition...',
            '[INFO] Wiping frp partition...',
            '[SUCCESS] All partitions wiped',
            '[INFO] Rebooting device...',
            '[SUCCESS] Factory reset complete. Device will reboot to setup wizard.',
        ]

        for i, msg in enumerate(messages):
            if self.cancelled:
                return
            self.on_log(msg)
            progress = int((i + 1) / len(messages) * 100)
            self.on_progress(progress)
            time.sleep(random.uniform(0.5, 1.5))

        self.on_status({'step': 'done', 'state': 'Factory reset complete'})

    def read_partitions(self):
        """Simulate GPT partition read and emit partition table."""
        self.cancelled = False
        self.on_status({'step': 'bypass', 'state': 'Reading partition table...'})

        self.on_log('[INFO] Sending GPT read command...')
        time.sleep(0.8)
        self.on_log('[INFO] Reading GPT header...')
        self.on_progress(20)
        time.sleep(0.6)
        self.on_log('[INFO] Parsing partition entries...')
        self.on_progress(50)
        time.sleep(0.8)

        partitions = self.MOCK_PARTITIONS
        for i, p in enumerate(partitions):
            if self.cancelled:
                return
            self.on_log(f'  [{p["index"]:2d}] {p["name"]:<16s} sector {p["sector"]:<10d} {p["size_human"]}')
            self.on_progress(50 + int((i + 1) / len(partitions) * 50))
            time.sleep(0.08)

        self.on_log(f'[SUCCESS] {len(partitions)} partitions read successfully.')
        self.on_status({
            'step': 'done',
            'state': 'Partition read complete',
            'partitions': partitions
        })

    # ------------------------------------------------------------------
    # Legacy: connect_and_erase_frp kept for backward compat but now
    # just chains detect + erase_frp
    # ------------------------------------------------------------------

    def connect_and_erase_frp(self):
        """Full flow for legacy callers: detect then immediately erase FRP."""
        self.connect_and_detect()
        if not self.cancelled:
            time.sleep(1)
            self.erase_frp()

    def get_device_info(self):
        """Return MOCK_DEVICE dict immediately."""
        return self.MOCK_DEVICE.copy()

    def cancel(self):
        self.cancelled = True
