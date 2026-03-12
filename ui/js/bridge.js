// MTK Studio - JS Bridge to Python API
const Bridge = {
  _ready: false,
  _queue: [],

  init() {
    if (window.pywebview && window.pywebview.api) {
      this._ready = true;
      this._flush();
    } else {
      window.addEventListener('pywebviewready', () => {
        this._ready = true;
        this._flush();
      });
    }
  },

  _flush() {
    this._queue.forEach(fn => fn());
    this._queue = [];
  },

  _call(method, ...args) {
    return new Promise((resolve, reject) => {
      const exec = () => {
        try {
          if (window.pywebview && window.pywebview.api && window.pywebview.api[method]) {
            Promise.resolve(window.pywebview.api[method](...args)).then(resolve).catch(reject);
          } else {
            console.warn('[Bridge] pywebview.api not available for:', method);
            resolve(null);
          }
        } catch(e) {
          reject(e);
        }
      };
      if (this._ready) exec();
      else this._queue.push(exec);
    });
  },

  startFrpBypass:      () => Bridge._call('start_frp_bypass'),
  cancelFrpBypass:     () => Bridge._call('cancel_frp_bypass'),
  getDeviceInfo:       () => Bridge._call('get_device_info'),
  getBypassStatus:     () => Bridge._call('get_bypass_status'),
  getMockMode:         () => Bridge._call('get_mock_mode'),
  setMockMode:     (en) => Bridge._call('set_mock_mode', en),
  getSettings:         () => Bridge._call('get_settings'),
  saveSettings:   (obj) => Bridge._call('save_settings', obj),
  getOperationHistory: () => Bridge._call('get_operation_history'),
  getUsbStatus:        () => Bridge._call('get_usb_status'),
};

// Python -> JS callbacks (called via window.evaluate_js from Python)

// Called by Python: window.addLog(message)
window.addLog = function(message) {
  // Append to #console-log if it exists
  const panel = document.getElementById('console-log');
  if (panel) {
    const time = new Date().toTimeString().slice(0, 8);
    const div = document.createElement('div');
    let cls = 'text-slate-300';
    if (message.includes('[ERROR]')) cls = 'text-red-400';
    else if (message.includes('[SUCCESS]')) cls = 'text-green-400';
    else if (message.includes('[WARN]')) cls = 'text-yellow-400';
    div.className = `${cls} text-xs font-mono leading-5`;
    div.textContent = `[${time}] ${message}`;
    panel.appendChild(div);
    panel.scrollTop = panel.scrollHeight;
  }
  // Also append to #operation-log (step 4 log)
  const opLog = document.getElementById('operation-log');
  if (opLog) {
    const time = new Date().toTimeString().slice(0, 8);
    const div = document.createElement('div');
    div.className = 'text-xs text-slate-600 py-1 border-b border-slate-100 flex gap-2';
    div.innerHTML = `<span class="text-slate-400 font-mono flex-shrink-0">[${time}]</span><span>${message}</span>`;
    opLog.appendChild(div);
    opLog.scrollTop = opLog.scrollHeight;
  }
};

// Called by Python: window.updateProgress(percent)
window.updateProgress = function(percent) {
  const bar = document.getElementById('progress-bar');
  const pct = document.getElementById('progress-pct');
  if (bar) bar.style.width = Math.min(100, percent) + '%';
  if (pct) pct.textContent = Math.min(100, percent) + '%';
};

// Called by Python: window.updateStatus({step, state, device?, error?})
window.updateStatus = function(status) {
  // Route to correct step
  if (status.step && window.Stepper) {
    const map = { setup: 1, connect: 2, detect: 3, bypass: 4, done: 5 };
    const n = map[status.step];
    if (n) window.Stepper.goToStep(n);
  }
  // Update footer
  const footer = document.getElementById('footer-status');
  if (footer && status.state) footer.textContent = status.state;
  // Populate device info if provided
  if (status.device) {
    window.dispatchEvent(new CustomEvent('deviceDetected', { detail: status.device }));
  }
  // Show error toast
  if (status.error) {
    window.showToast('error', status.error, () => {
      if (window.startBypass) window.startBypass();
    });
  }
  // Mark step complete when done
  if (status.step === 'done' && window.Stepper) {
    window.Stepper.completeStep(4);
  }
};

// Called by Python: window.onDeviceConnected(info)
window.onDeviceConnected = function(info) {
  const dev = document.getElementById('footer-device');
  const dot = document.getElementById('footer-dot');
  const port = document.getElementById('footer-port');
  if (dev) dev.textContent = `${info.chipset} (${info.description})`;
  if (dot) { dot.classList.remove('bg-slate-300'); dot.classList.add('bg-emerald-500'); }
  if (port && info.port) port.textContent = info.port;
  // Fire deviceDetected event for step 3 card
  window.dispatchEvent(new CustomEvent('deviceDetected', { detail: info }));
};

// Called by Python: window.onDeviceDisconnected()
window.onDeviceDisconnected = function() {
  const dev = document.getElementById('footer-device');
  const dot = document.getElementById('footer-dot');
  const port = document.getElementById('footer-port');
  if (dev) dev.textContent = 'No device connected';
  if (dot) { dot.classList.remove('bg-emerald-500'); dot.classList.add('bg-slate-300'); }
  if (port) port.textContent = '';
};

// Called by Python (or JS): window.showToast(type, message, retryFn?)
window.showToast = function(type, message, retryFn) {
  if (window.Toast) window.Toast.show(type, message, retryFn);
};

// Init bridge
document.addEventListener('DOMContentLoaded', () => Bridge.init());
window.Bridge = Bridge;
