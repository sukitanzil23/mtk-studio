// MTK Studio - Sidebar Console Controller
// Glassmorphism right-panel for persistent output logs

const Console = {
  _el: null,        // sidebar root element
  _log: null,       // scrollable log container
  _badge: null,     // entry count badge
  _count: 0,        // total entries
  _startTime: null, // session start for elapsed calc

  // Icon + color map for log entry types
  _typeMap: {
    info:     { icon: 'info',          color: 'text-slate-400' },
    action:   { icon: 'bolt',          color: 'text-sky-400' },
    success:  { icon: 'check_circle',  color: 'text-emerald-400 font-bold' },
    error:    { icon: 'error',         color: 'text-red-400 font-bold' },
    warn:     { icon: 'warning',       color: 'text-yellow-400' },
    hardware: { icon: 'memory',        color: 'text-slate-300 font-bold' },
    usb:      { icon: 'usb',           color: 'text-slate-300 font-bold' },
    system:   { icon: 'terminal',      color: 'text-slate-500 italic' },
  },

  init() {
    this._el    = document.getElementById('console-sidebar');
    this._log   = document.getElementById('console-log');
    this._badge = document.getElementById('console-entry-count');
    if (!this._el) return;

    // Restore collapsed state from sessionStorage
    const collapsed = sessionStorage.getItem('console-collapsed') === 'true';
    if (collapsed) {
      this._el.classList.add('collapsed');
    }
  },

  // Detect log type from message content
  _detectType(message) {
    const m = message.toLowerCase();
    if (m.includes('[error]'))                    return 'error';
    if (m.includes('[success]') || m.includes('[done]')) return 'success';
    if (m.includes('[warn]'))                     return 'warn';
    if (m.includes('usb') || m.includes('device connected') || m.includes('device disconnected')) return 'usb';
    if (m.includes('chipset') || m.includes('brom') || m.includes('preloader') || m.includes('hw_code')) return 'hardware';
    if (m.includes('bypass') || m.includes('erasing') || m.includes('flashing') || m.includes('writing')) return 'action';
    if (m.includes('ready') || m.includes('init'))  return 'system';
    return 'info';
  },

  // Add a log entry to the sidebar console
  addEntry(message, type) {
    if (!this._log) return;
    if (!this._startTime) this._startTime = Date.now();

    type = type || this._detectType(message);
    const meta = this._typeMap[type] || this._typeMap.info;
    const time = new Date().toTimeString().slice(0, 8);

    const row = document.createElement('div');
    row.className = 'flex items-start gap-3';

    row.innerHTML =
      '<span class="material-symbols-outlined ' + meta.color + '" style="font-size:16px;line-height:1.625rem;">' + meta.icon + '</span>' +
      '<span class="flex-1 ' + meta.color + '">' +
        '<span class="text-slate-500 mr-1">[' + time + ']</span>' +
        message +
      '</span>';

    this._log.appendChild(row);
    this._count++;

    // Update badge
    if (this._badge) {
      this._badge.textContent = this._count + ' entr' + (this._count === 1 ? 'y' : 'ies');
    }

    // Auto-scroll to bottom
    this._log.scrollTop = this._log.scrollHeight;
  },

  // Add a session-end separator with elapsed time
  addSessionEnd() {
    if (!this._log) return;
    const elapsed = this._startTime
      ? ((Date.now() - this._startTime) / 1000).toFixed(1) + 's elapsed'
      : '';

    const sep = document.createElement('div');
    sep.className = 'border-t border-white/5 mt-3 pt-2 text-slate-500 italic text-[10px] tracking-wide';
    sep.textContent = elapsed ? 'Session complete -- ' + elapsed : 'Session complete';
    this._log.appendChild(sep);
    this._log.scrollTop = this._log.scrollHeight;
    this._startTime = null;
  },

  // Toggle sidebar visibility
  // FIX: uses CSS width:0 collapse via .collapsed class -- no more
  // broken #main-wrapper margin hack. The sidebar is a flex child so
  // collapsing its width automatically gives space back to <main>.
  toggle() {
    if (!this._el) return;
    const isCollapsed = this._el.classList.toggle('collapsed');
    sessionStorage.setItem('console-collapsed', isCollapsed);

    // Update chevron direction
    const chevron = document.getElementById('console-toggle-icon');
    if (chevron) {
      chevron.textContent = isCollapsed ? 'chevron_left' : 'chevron_right';
    }
  },

  // Copy all log text to clipboard
  copyLogs() {
    if (!this._log) return;
    const text = this._log.innerText;
    navigator.clipboard.writeText(text).then(() => {
      if (window.showToast) window.showToast('success', 'Logs copied to clipboard');
    });
  },

  // Clear all log entries
  clearLogs() {
    if (!this._log) return;
    this._log.innerHTML = '';
    this._count = 0;
    this._startTime = null;
    if (this._badge) this._badge.textContent = '0 entries';
    this.addEntry('Console cleared', 'system');
  },
};

window.Console = Console;
