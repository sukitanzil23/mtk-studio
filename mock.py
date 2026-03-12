"""MTK Studio -- Mock bridge for testing without real hardware."""
import time
import random


class MockBridge:
    MOCK_DEVICE = {
        'chipset': 'MT6765',
        'description': 'Helio P35',
        'hwcode': '0x0766',
        'is_brom': True,
        'port': 'COM3 (Mock)',
        'mode': 'BROM'
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

    def cancel(self):
        self.cancelled = True

    def get_device_info(self):
        return self.MOCK_DEVICE.copy()
