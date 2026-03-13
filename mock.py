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

    LOG_MESSAGES = [
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

    def __init__(self, on_log, on_progress, on_status):
        self.on_log = on_log
        self.on_progress = on_progress
        self.on_status = on_status
        self.cancelled = False

    def connect_and_erase_frp(self):
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

        # Step 3: Detect
        device = self.MOCK_DEVICE.copy()
        self.on_status({'step': 'detect', 'state': 'Device detected', 'device': device})
        self.on_log(f'[INFO] Chipset: {device["chipset"]} ({device["description"]})')
        self.on_log(f'[INFO] HW Code: {device["hwcode"]} | Boot mode: BROM')
        time.sleep(1)

        if self.cancelled:
            return

        # Step 4: Bypass -- 5% simulated failure for error handling testing
        if random.random() < 0.05:
            self.on_status({'step': 'bypass', 'state': 'Error', 'error': 'Simulated USB disconnect during bypass'})
            self.on_log('[ERROR] USB connection lost during bypass. Retry to continue.')
            return

        self.on_status({'step': 'bypass', 'state': 'FRP bypass in progress...'})
        total = len(self.LOG_MESSAGES)
        for i, msg in enumerate(self.LOG_MESSAGES):
            if self.cancelled:
                return
            self.on_log(msg)
            self.on_progress(int((i + 1) / total * 100))
            time.sleep(1.1)

        if self.cancelled:
            return

        # Step 5: Done
        self.on_progress(100)
        self.on_status({'step': 'done', 'state': 'Operation completed successfully', 'device': device})

    # ------------------------------------------------------------------
    # Factory Reset + FRP (mock)
    # ------------------------------------------------------------------

    FACTORY_RESET_LOGS = [
        '[INFO] Initializing mtkclient for factory reset...',
        '[INFO] Using built-in DA loaders',
        '[INFO] mtkclient v2 engine ready',
        '[INFO] Waiting for device... Hold Vol-Down + Power, then plug USB',
        '[INFO] Device detected on COM3',
        '[INFO] Identifying chipset and uploading Download Agent...',
        '[INFO] Download Agent uploaded successfully',
        '[INFO] Reading GPT partition table...',
        '[INFO] Partitions to erase: userdata, cache, frp, persist',
        '[INFO] Erasing userdata partition... (1/4)',
        '[SUCCESS] userdata partition erased',
        '[INFO] Erasing cache partition... (2/4)',
        '[SUCCESS] cache partition erased',
        '[INFO] Erasing frp partition... (3/4)',
        '[SUCCESS] frp partition erased',
        '[INFO] Erasing persist partition... (4/4)',
        '[SUCCESS] persist partition erased',
        '[INFO] Resetting device...',
        '[SUCCESS] Reset command sent. Disconnect USB cable.',
        '[SUCCESS] Factory reset + FRP removal complete. Device wiped.',
    ]

    def connect_and_factory_reset_frp(self):
        self.cancelled = False
        device = self.MOCK_DEVICE.copy()

        # Setup
        self.on_status({'step': 'setup', 'state': 'Initializing mtkclient...'})
        self.on_log('[INFO] Initializing mtkclient for factory reset...')
        time.sleep(0.8)
        self.on_progress(5)

        if self.cancelled:
            return

        # Connect
        self.on_status({'step': 'connect', 'state': 'Waiting for device in BROM mode...'})
        self.on_log('[INFO] Waiting for device...')
        time.sleep(2)
        self.on_log('[INFO] Device detected on COM3')
        self.on_progress(20)

        if self.cancelled:
            return

        # Detect
        self.on_status({'step': 'detect', 'state': 'Device detected', 'device': device})
        self.on_log(f'[INFO] Chipset: {device["chipset"]} ({device["description"]})')
        time.sleep(1)
        self.on_progress(40)

        if self.cancelled:
            return

        # Factory erase
        self.on_status({'step': 'bypass', 'state': 'Factory reset in progress...'})
        partitions = ['userdata', 'cache', 'frp', 'persist']
        for i, part in enumerate(partitions):
            if self.cancelled:
                return
            pct = 45 + int((i / len(partitions)) * 40)
            self.on_progress(pct)
            self.on_log(f'[INFO] Erasing {part} partition... ({i+1}/{len(partitions)})')
            time.sleep(1.5)
            self.on_log(f'[SUCCESS] {part} partition erased')
            time.sleep(0.3)

        self.on_progress(90)

        # Reset
        self.on_log('[INFO] Resetting device...')
        time.sleep(0.5)
        self.on_log('[SUCCESS] Reset command sent. Disconnect USB cable.')
        self.on_progress(100)
        self.on_status({
            'step': 'done',
            'state': 'Factory reset completed successfully',
            'device': device
        })
        self.on_log('[SUCCESS] Factory reset + FRP removal complete. Device wiped.')

    # ------------------------------------------------------------------
    # Read Partitions (mock)
    # ------------------------------------------------------------------

    MOCK_PARTITIONS = [
        {'name': 'boot',       'sector': 2048,     'sectors': 65536,   'size_bytes': 33554432,  'size_human': '32.0 MB'},
        {'name': 'recovery',   'sector': 67584,    'sectors': 65536,   'size_bytes': 33554432,  'size_human': '32.0 MB'},
        {'name': 'lk',         'sector': 133120,   'sectors': 2048,    'size_bytes': 1048576,   'size_human': '1.0 MB'},
        {'name': 'lk2',        'sector': 135168,   'sectors': 2048,    'size_bytes': 1048576,   'size_human': '1.0 MB'},
        {'name': 'para',       'sector': 137216,   'sectors': 1024,    'size_bytes': 524288,    'size_human': '512.0 KB'},
        {'name': 'misc',       'sector': 138240,   'sectors': 1024,    'size_bytes': 524288,    'size_human': '512.0 KB'},
        {'name': 'expdb',      'sector': 139264,   'sectors': 20480,   'size_bytes': 10485760,  'size_human': '10.0 MB'},
        {'name': 'frp',        'sector': 159744,   'sectors': 512,     'size_bytes': 262144,    'size_human': '256.0 KB'},
        {'name': 'persist',    'sector': 160256,   'sectors': 6144,    'size_bytes': 3145728,   'size_human': '3.0 MB'},
        {'name': 'nvdata',     'sector': 166400,   'sectors': 65536,   'size_bytes': 33554432,  'size_human': '32.0 MB'},
        {'name': 'metadata',   'sector': 231936,   'sectors': 65536,   'size_bytes': 33554432,  'size_human': '32.0 MB'},
        {'name': 'protect1',   'sector': 297472,   'sectors': 20480,   'size_bytes': 10485760,  'size_human': '10.0 MB'},
        {'name': 'protect2',   'sector': 317952,   'sectors': 20480,   'size_bytes': 10485760,  'size_human': '10.0 MB'},
        {'name': 'seccfg',     'sector': 338432,   'sectors': 1024,    'size_bytes': 524288,    'size_human': '512.0 KB'},
        {'name': 'system',     'sector': 339456,   'sectors': 6291456, 'size_bytes': 3221225472,'size_human': '3.0 GB'},
        {'name': 'vendor',     'sector': 6630912,  'sectors': 1048576, 'size_bytes': 536870912, 'size_human': '512.0 MB'},
        {'name': 'cache',      'sector': 7679488,  'sectors': 524288,  'size_bytes': 268435456, 'size_human': '256.0 MB'},
        {'name': 'userdata',   'sector': 8203776,  'sectors': 52428800,'size_bytes': 26843545600,'size_human': '25.0 GB'},
    ]

    def read_partitions(self):
        self.cancelled = False
        device = self.MOCK_DEVICE.copy()

        # Setup
        self.on_status({'step': 'setup', 'state': 'Initializing mtkclient...'})
        self.on_log('[INFO] Initializing mtkclient for partition read...')
        time.sleep(0.5)
        self.on_progress(10)

        if self.cancelled:
            return {'error': 'Cancelled'}

        # Connect
        self.on_status({'step': 'connect', 'state': 'Waiting for device in BROM mode...'})
        self.on_log('[INFO] Waiting for device...')
        time.sleep(1.5)
        self.on_log('[INFO] Device detected on COM3')
        self.on_progress(30)

        if self.cancelled:
            return {'error': 'Cancelled'}

        # Detect + DA
        self.on_status({'step': 'detect', 'state': 'Uploading DA...', 'device': device})
        self.on_log(f'[INFO] Chipset: {device["chipset"]}')
        time.sleep(0.8)
        self.on_progress(50)

        # Read GPT
        self.on_status({'step': 'bypass', 'state': 'Reading partition table...'})
        self.on_log('[INFO] Reading GPT partition table...')
        time.sleep(1)
        self.on_progress(60)

        for p in self.MOCK_PARTITIONS:
            self.on_log(f'  {p["name"]}: sector={p["sector"]}, size={p["size_human"]}')
            time.sleep(0.1)

        self.on_progress(90)

        # Done
        self.on_log('[INFO] Device disconnected cleanly.')
        time.sleep(0.3)
        self.on_progress(100)
        self.on_status({
            'step': 'done',
            'state': f'Read {len(self.MOCK_PARTITIONS)} partitions successfully',
            'device': device
        })
        self.on_log(f'[SUCCESS] Found {len(self.MOCK_PARTITIONS)} partitions.')
        return {'partitions': self.MOCK_PARTITIONS, 'count': len(self.MOCK_PARTITIONS)}

    def cancel(self):
        self.cancelled = True

    def get_device_info(self):
        return self.MOCK_DEVICE.copy()
