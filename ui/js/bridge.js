// MTK Studio - JS Bridge to Python API (v2 -- sidebar console)
const Bridge = {
  _ready: false,
  _queue: [],

  init() {
    if (window.pywebview && window.pywebview.api) {
      this._ready = true;
      this._flush();
    } else {
      window.addEventListener('pywebviewready', function() {
        Bridge._ready = true;
        Bridge._flush();
      });
    }
  },

  _flush() {
    this._queue.forEach(function(fn) { fn(); });
    this._queue = [];
  },

  _call(method) {
    var args = Array.prototype.slice.call(arguments, 1);
    return new Promise(function(resolve, reject) {
      var exec = function() {
        try {
          if (window.pywebview && window.pywebview.api && window.pywebview.api[method]) {
            Promise.resolve(window.pywebview.api[method].apply(null, args)).then(resolve).catch(reject);
          } else {
            console.warn('[Bridge] pywebview.api not available for:', method);
            resolve(null);
          }
        } catch(e) {
          reject(e);
        }
      };
      if (Bridge._ready) exec();
      else Bridge._queue.push(exec);
    });
  },

  startFrpBypass:      function() { return Bridge._call('start_frp_bypass'); },
  cancelFrpBypass:     function() { return Bridge._call('cancel_frp_bypass'); },
  getDeviceInfo:       function() { return Bridge._call('get_device_info'); },
  getBypassStatus:     function() { return Bridge._call('get_bypass_status'); },
  getMockMode:         function() { return Bridge._call('get_mock_mode'); },
  setMockMode:         function(en) { return Bridge._call('set_mock_mode', en); },
  getSettings:         function() { return Bridge._call('get_settings'); },
  saveSettings:        function(obj) { return Bridge._call('save_settings', obj); },
  getOperationHistory: function() { return Bridge._call('get_operation_history'); },
  getUsbStatus:        function() { return Bridge._call('get_usb_status'); },
};

// -- Python -> JS callbacks --

// Called by Python: window.addLog(message)
window.addLog = function(message) {
  if (window.Console) {
    window.Console.addEntry(message);
  }
};

// Called by Python: window.updateProgress(percent)
window.updateProgress = function(percent) {
  var bar = document.getElementById('progress-bar');
  var pct = document.getElementById('progress-pct');
  if (bar) bar.style.width = Math.min(100, percent) + '%';
  if (pct) pct.textContent = Math.min(100, percent) + '%';
};

// Called by Python: window.updateStatus({step, state, device?, error?})
window.updateStatus = function(status) {
  if (status.step && window.Stepper) {
    var map = { setup: 1, connect: 2, detect: 3, bypass: 4, done: 5 };
    var n = map[status.step];
    if (n) window.Stepper.goToStep(n);
  }
  var footer = document.getElementById('footer-status');
  if (footer && status.state) footer.textContent = status.state;
  if (status.device) {
    window.dispatchEvent(new CustomEvent('deviceDetected', { detail: status.device }));
  }
  if (status.error) {
    window.showToast('error', status.error, function() {
      if (window.startBypass) window.startBypass();
    });
  }
  if (status.step === 'done' && window.Stepper) {
    window.Stepper.completeStep(4);
    if (window.Console) window.Console.addSessionEnd();
  }
};

// Called by Python: window.onDeviceConnected(info)
window.onDeviceConnected = function(info) {
  var deviceEl = document.getElementById('footer-device');
  var dot = document.getElementById('footer-dot');
  var port = document.getElementById('footer-port');
  if (deviceEl) deviceEl.textContent = info.chipset + ' connected';
  if (dot) {
    dot.classList.remove('bg-slate-300');
    dot.classList.add('bg-emerald-500');
  }
  if (port && info.port) port.textContent = info.port;
  window.dispatchEvent(new CustomEvent('deviceDetected', { detail: info }));
};

// Called by Python: window.onDeviceDisconnected()
window.onDeviceDisconnected = function() {
  var deviceEl = document.getElementById('footer-device');
  var dot = document.getElementById('footer-dot');
  var port = document.getElementById('footer-port');
  if (deviceEl) deviceEl.textContent = 'No device connected';
  if (dot) {
    dot.classList.remove('bg-emerald-500');
    dot.classList.add('bg-slate-300');
  }
  if (port) port.textContent = '';
};

// Called by Python (or JS): window.showToast(type, message, retryFn?)
window.showToast = function(type, message, retryFn) {
  if (window.Toast) window.Toast.show(type, message, retryFn);
};

window.Bridge = Bridge;
document.addEventListener('DOMContentLoaded', function() { Bridge.init(); });
