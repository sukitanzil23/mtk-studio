// MTK Studio - Toast Notification System
const Toast = {
  _container: null,

  init() {
    this._container = document.createElement('div');
    this._container.id = 'toast-container';
    this._container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
    document.body.appendChild(this._container);
  },

  show(type, message, retryCallback) {
    if (!this._container) this.init();
    const colors = {
      success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
      error:   'bg-red-50 border-red-200 text-red-800',
      warning: 'bg-amber-50 border-amber-200 text-amber-800',
      info:    'bg-blue-50 border-blue-200 text-blue-800',
    };
    const icons = {
      success: '\u2713', error: '\u2715', warning: '\u26A0', info: '\u2139'
    };
    const toast = document.createElement('div');
    toast.className = `flex items-start gap-3 p-4 rounded-xl border shadow-lg max-w-sm ${colors[type] || colors.info}`;
    toast.innerHTML = `
      <span class="text-lg font-bold flex-shrink-0">${icons[type] || icons.info}</span>
      <div class="flex-1 text-sm font-medium">${message}</div>
      <div class="flex flex-col gap-1 flex-shrink-0">
        ${retryCallback ? '<button onclick="this.closest(\'[data-toast]\').retryFn()" class="text-xs font-bold underline hover:no-underline">Retry</button>' : ''}
        <button class="text-lg leading-none font-bold opacity-60 hover:opacity-100" onclick="this.closest('[data-toast]').remove()">&times;</button>
      </div>
    `;
    toast.setAttribute('data-toast', '');
    if (retryCallback) toast.retryFn = retryCallback;
    this._container.appendChild(toast);
  }
};

window.Toast = Toast;
document.addEventListener('DOMContentLoaded', () => Toast.init());
