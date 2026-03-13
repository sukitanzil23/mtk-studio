// MTK Studio - Main App Router (v2 -- with sidebar console)
const ROUTES = {
  'frp-bypass': 'pages/frp-bypass.html',
  'dashboard': 'pages/dashboard.html',
  'flash-tool': 'pages/flash-tool.html',
  'imei-repair': 'pages/imei-repair.html',
  'settings': 'pages/settings.html',
};

let currentPage = null;

const PAGE_LABELS = {
  'frp-bypass': 'FRP Bypass',
  'dashboard': 'Dashboard',
  'flash-tool': 'Flash Tool',
  'imei-repair': 'IMEI Repair',
  'settings': 'Settings',
};

async function loadPage(pageName) {
  const url = ROUTES[pageName];
  if (!url) return;
  try {
    const res = await fetch(url);
    const html = await res.text();
    const container = document.getElementById('page-content');
    container.innerHTML = html;
    currentPage = pageName;
    updateActiveNav(pageName);

    const breadcrumb = document.getElementById('breadcrumb-page');
    if (breadcrumb) breadcrumb.textContent = PAGE_LABELS[pageName] || pageName;

    const footerStatus = document.getElementById('footer-status');
    if (footerStatus && pageName !== 'frp-bypass') {
      footerStatus.textContent = 'Ready';
    }

    container.querySelectorAll('script').forEach(function(oldScript) {
      const newScript = document.createElement('script');
      if (oldScript.src) {
        newScript.src = oldScript.src;
      } else {
        newScript.textContent = oldScript.textContent;
      }
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });

    if (pageName === 'frp-bypass' && window.initStepper) {
      window.initStepper();
    }
  } catch (e) {
    console.error('Failed to load page:', e);
  }
}

function updateActiveNav(pageName) {
  document.querySelectorAll('[data-page]').forEach(function(el) {
    const isActive = el.dataset.page === pageName;
    el.classList.remove('bg-blue-50', 'text-blue-700', 'bg-primary/10', 'text-primary', 'text-slate-600', 'hover:bg-slate-100');
    if (isActive) {
      el.classList.add('bg-primary/10', 'text-primary');
    } else {
      el.classList.add('text-slate-600', 'hover:bg-slate-100');
    }
    const icon = el.querySelector('.material-symbols-outlined');
    if (icon) {
      icon.style.fontVariationSettings = isActive
        ? "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24"
        : "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24";
    }
  });
}

function navigate(pageName) {
  window.location.hash = '/' + pageName;
}

window.addEventListener('hashchange', function() {
  const hash = window.location.hash.replace('#/', '');
  loadPage(hash || 'frp-bypass');
});

document.addEventListener('DOMContentLoaded', function() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="flex h-screen w-full overflow-hidden bg-slate-50">

      <!-- Left Navigation Sidebar -->
      <aside id="sidebar" class="w-64 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col">

        <!-- Brand -->
        <div class="flex items-center gap-3 p-6 border-b border-slate-200">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white" style="background:#3B82F6;">
            <span class="material-symbols-outlined">developer_mode_tv</span>
          </div>
          <div>
            <h1 class="text-base font-bold leading-none text-slate-900">MTK Studio</h1>
            <p class="text-xs text-slate-500 mt-1">v2.4.0</p>
          </div>
        </div>

        <!-- Nav Links -->
        <nav class="flex-1 space-y-1 p-4">
          <a data-page="dashboard" onclick="navigate('dashboard')"
             class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <span class="material-symbols-outlined">dashboard</span>
            Dashboard
          </a>
          <a data-page="frp-bypass" onclick="navigate('frp-bypass')"
             class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer bg-primary/10 text-primary text-sm font-semibold transition-colors">
            <span class="material-symbols-outlined filled">shield</span>
            FRP Bypass
          </a>
          <a data-page="flash-tool" onclick="navigate('flash-tool')"
             class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <span class="material-symbols-outlined">flash_on</span>
            Flash Tool
          </a>
          <a data-page="imei-repair" onclick="navigate('imei-repair')"
             class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <span class="material-symbols-outlined">dialpad</span>
            IMEI Repair
          </a>
        </nav>

        <!-- Settings (bottom) -->
        <div class="p-4 border-t border-slate-200">
          <a data-page="settings" onclick="navigate('settings')"
             class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <span class="material-symbols-outlined">settings</span>
            Settings
          </a>
        </div>
      </aside>

      <!-- Main Wrapper (header + content + footer) -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

        <!-- Header -->
        <header class="h-14 flex items-center justify-between px-6 border-b border-slate-200 bg-white flex-shrink-0">
          <div class="flex items-center gap-3 text-sm">
            <span class="text-slate-400">MTK Studio</span>
            <span class="text-slate-300">/</span>
            <span id="breadcrumb-page" class="font-semibold text-slate-700">FRP Bypass</span>
          </div>
          <div class="flex items-center gap-2">
            <button id="btn-toggle-console" onclick="Console.toggle()"
                    class="h-8 px-3 flex items-center gap-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors text-xs font-bold uppercase tracking-wider"
                    title="Toggle Output Logs">
              <span class="material-symbols-outlined" style="font-size: 16px;">terminal</span>
              <span class="hidden sm:inline">Logs</span>
            </button>
          </div>
        </header>

        <!-- Content + Console row -->
        <div class="flex-1 flex overflow-hidden">

          <!-- Scrollable page content -->
          <main class="flex-1 overflow-y-auto p-8 bg-slate-50" id="page-content">
            <div class="flex items-center justify-center h-full text-slate-400">Loading...</div>
          </main>

          <!-- Right Console Sidebar (Glassmorphism Dark) -->
          <aside id="console-sidebar"
                 class="w-80 border-l border-white/10 flex flex-col flex-shrink-0"
                 style="background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);">

            <!-- Console Header -->
            <div class="h-12 flex items-center justify-between px-4 border-b border-white/5 flex-shrink-0"
                 style="background: rgba(255,255,255,0.03);">
              <div class="flex items-center gap-2 text-slate-300">
                <span class="material-symbols-outlined" style="font-size: 16px;">terminal</span>
                <span class="text-[10px] uppercase tracking-widest font-black">Output Logs</span>
                <span id="console-entry-count" class="text-[10px] font-mono text-slate-600 ml-2">no entries</span>
              </div>
              <div class="flex items-center gap-1">
                <button onclick="Console.copyLogs()"
                        class="w-7 h-7 flex items-center justify-center hover:bg-white/10 rounded-lg text-slate-500 hover:text-slate-300 transition-colors"
                        title="Copy logs">
                  <span class="material-symbols-outlined" style="font-size: 14px;">content_copy</span>
                </button>
                <button onclick="Console.clearLogs()"
                        class="w-7 h-7 flex items-center justify-center hover:bg-white/10 rounded-lg text-slate-500 hover:text-slate-300 transition-colors"
                        title="Clear logs">
                  <span class="material-symbols-outlined" style="font-size: 14px;">delete_sweep</span>
                </button>
                <button onclick="Console.toggle()"
                        class="w-7 h-7 flex items-center justify-center hover:bg-white/10 rounded-lg text-slate-400 transition-colors"
                        title="Collapse panel">
                  <span id="console-toggle-icon" class="material-symbols-outlined" style="font-size: 18px;">chevron_right</span>
                </button>
              </div>
            </div>

            <!-- Live indicator -->
            <div class="flex items-center gap-2 px-4 py-2 border-b border-white/5 flex-shrink-0">
              <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 pulse-dot"></div>
              <span class="text-[9px] uppercase tracking-widest font-bold text-slate-500">Live</span>
              <span class="flex-1"></span>
              <span id="console-elapsed" class="text-[10px] font-mono text-slate-600">--:--</span>
            </div>

            <!-- Log entries -->
            <div id="console-log"
                 class="console-log flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed space-y-2">
              <div class="flex items-start gap-3 text-slate-600">
                <span class="material-symbols-outlined text-xs mt-0.5" style="font-size: 14px;">info</span>
                <span>Waiting for operation...</span>
              </div>
            </div>

          </aside>

        </div>

        <!-- Footer -->
        <footer class="h-10 bg-white border-t border-slate-200 flex items-center px-6 gap-6 flex-shrink-0">
          <span class="flex items-center gap-1.5">
            <span id="footer-dot" class="w-2 h-2 rounded-full bg-slate-300"></span>
            <span id="footer-status" class="text-[10px] font-bold uppercase tracking-widest text-slate-500">System Ready</span>
          </span>
          <span class="text-slate-200">|</span>
          <span class="flex items-center gap-1.5">
            <span class="material-symbols-outlined text-slate-400" style="font-size: 14px;">usb</span>
            <span id="footer-device" class="text-[10px] font-bold uppercase tracking-widest text-slate-500">No device connected</span>
          </span>
          <span class="flex-1"></span>
          <span id="footer-port" class="text-[10px] font-bold uppercase tracking-widest text-slate-500"></span>
        </footer>

      </div>
    </div>
  `;

  const hash = window.location.hash.replace('#/', '');
  loadPage(hash || 'frp-bypass');
});
