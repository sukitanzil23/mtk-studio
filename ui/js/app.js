// MTK Studio - Main App Router
const ROUTES = {
  'frp-bypass': 'pages/frp-bypass.html',
  'dashboard': 'pages/dashboard.html',
  'flash-tool': 'pages/flash-tool.html',
  'imei-repair': 'pages/imei-repair.html',
  'settings': 'pages/settings.html',
};

let currentPage = null;

// Pretty labels for breadcrumb and footer
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

    // Update breadcrumb
    const breadcrumb = document.getElementById('breadcrumb-page');
    if (breadcrumb) breadcrumb.textContent = PAGE_LABELS[pageName] || pageName;

    // Update footer status on navigation
    const footerStatus = document.getElementById('footer-status');
    if (footerStatus && pageName !== 'frp-bypass') {
      footerStatus.textContent = 'Ready';
    }

    // Execute inline <script> tags (innerHTML doesn't auto-execute them)
    container.querySelectorAll('script').forEach(oldScript => {
      const newScript = document.createElement('script');
      if (oldScript.src) {
        newScript.src = oldScript.src;
      } else {
        newScript.textContent = oldScript.textContent;
      }
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });

    // Init stepper after script execution for FRP page
    if (pageName === 'frp-bypass' && window.initStepper) {
      window.initStepper();
    }
  } catch (e) {
    console.error('Failed to load page:', e);
  }
}

function updateActiveNav(pageName) {
  document.querySelectorAll('[data-page]').forEach(el => {
    const active = el.dataset.page === pageName;
    el.classList.toggle('bg-blue-50', active);
    el.classList.toggle('text-blue-700', active);
    el.classList.toggle('text-slate-600', !active);
  });
}

function navigate(pageName) {
  window.location.hash = '/' + pageName;
}

window.addEventListener('hashchange', () => {
  const hash = window.location.hash.replace('#/', '');
  loadPage(hash || 'frp-bypass');
});

document.addEventListener('DOMContentLoaded', () => {
  // Remove loading screen, build shell
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="flex min-h-screen bg-slate-50">
      <!-- Sidebar -->
      <aside id="sidebar" class="w-60 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col">
        <div class="p-5 border-b border-slate-200">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"/></svg>
            </div>
            <div>
              <div class="text-base font-bold leading-none text-slate-900">MTK Studio</div>
              <div class="text-xs text-slate-500 mt-1">v1.0 Beta</div>
            </div>
          </div>
        </div>
        <nav class="flex-1 p-3 space-y-1">
          <a data-page="dashboard" onclick="navigate('dashboard')" class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18M3 12h18M3 17h18"/></svg>
            Dashboard
          </a>
          <a data-page="frp-bypass" onclick="navigate('frp-bypass')" class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer bg-blue-50 text-blue-700 text-sm font-medium transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            FRP Bypass
          </a>
          <a data-page="flash-tool" onclick="navigate('flash-tool')" class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            Flash Tool
          </a>
          <a data-page="imei-repair" onclick="navigate('imei-repair')" class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
            IMEI Repair
          </a>
        </nav>
        <div class="p-3 border-t border-slate-200">
          <a data-page="settings" onclick="navigate('settings')" class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            Settings
          </a>
        </div>
      </aside>

      <!-- Main area -->
      <div class="flex-1 flex flex-col min-h-screen">
        <!-- Header -->
        <header class="h-14 bg-white border-b border-slate-200 flex items-center px-6 flex-shrink-0">
          <div class="flex items-center gap-2 text-sm text-slate-500">
            <span id="breadcrumb-root" class="font-medium text-slate-900">MTK Studio</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
            <span id="breadcrumb-page">FRP Bypass</span>
          </div>
        </header>

        <!-- Page content -->
        <main class="flex-1 overflow-y-auto" id="page-content">
          <div class="flex items-center justify-center h-full text-slate-400">Loading...</div>
        </main>

        <!-- Footer -->
        <footer class="h-12 bg-white border-t border-slate-200 flex items-center px-6 gap-6 flex-shrink-0">
          <span id="footer-status" class="text-[10px] font-bold uppercase tracking-widest text-slate-500">Ready</span>
          <span class="text-slate-200">|</span>
          <span id="footer-device" class="text-[10px] font-bold uppercase tracking-widest text-slate-500">No device connected</span>
          <span class="flex-1"></span>
          <div class="flex items-center gap-2">
            <span id="footer-port" class="text-[10px] font-bold uppercase tracking-widest text-slate-500"></span>
            <div id="footer-dot" class="w-2 h-2 rounded-full bg-slate-300"></div>
          </div>
        </footer>
      </div>
    </div>
  `;

  // Load default page
  loadPage('frp-bypass');
});
