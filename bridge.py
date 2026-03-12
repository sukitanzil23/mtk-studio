"""MTK Studio -- Real device bridge wrapping mtkclient."""


class MtkBridge:
    def __init__(self, on_log, on_progress, on_status):
        self.on_log = on_log
        self.on_progress = on_progress
        self.on_status = on_status
        self.mtk = None
        self.da_handler = None
        self.device_info = {}
        self.cancelled = False

    def connect_and_erase_frp(self):
        """
        Full FRP bypass flow via mtkclient.
        Phase 5 implementation:
          1. MtkConfig + Mtk init
          2. da_handler.connect(mtk)  [blocks until device in BROM]
          3. Read chipconfig: name, hwcode, is_brom
          4. da_handler.configure_da(mtk)
          5. da_handler.da_erase(['frp'], 'user')
        """
        self.on_status({'step': 'setup', 'state': 'Error',
                        'error': 'Real device bridge not yet implemented. Enable Mock Mode in Settings.'})
        self.on_log('[ERROR] Real device bridge not yet implemented. Enable Mock Mode in Settings.')

    def cancel(self):
        self.cancelled = True

    def get_device_info(self):
        return self.device_info or None
