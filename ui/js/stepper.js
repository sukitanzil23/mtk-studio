// MTK Studio - FRP Wizard Stepper
const Stepper = {
  currentStep: 1,
  completedSteps: [],
  stepLabels: ['Setup', 'Connect', 'Detect', 'Bypass', 'Done'],

  init() {
    this.render();
    this.showStep(this.currentStep);
  },

  goToStep(n) {
    if (n < 1 || n > 5) return;
    this.currentStep = n;
    this.render();
    this.showStep(n);
  },

  completeStep(n) {
    if (!this.completedSteps.includes(n)) this.completedSteps.push(n);
    this.render();
  },

  reset() {
    this.currentStep = 1;
    this.completedSteps = [];
    this.render();
    this.showStep(1);
  },

  showStep(n) {
    document.querySelectorAll('.step-panel').forEach(el => el.classList.remove('active'));
    const panel = document.querySelector(`.step-panel[data-step="${n}"]`);
    if (panel) panel.classList.add('active');
  },

  render() {
    const container = document.getElementById('stepper-bar');
    if (!container) return;
    container.innerHTML = this.stepLabels.map((label, i) => {
      const n = i + 1;
      const isDone = this.completedSteps.includes(n);
      const isActive = this.currentStep === n;
      const circleClass = isDone ? 'bg-emerald-500 text-white' : isActive ? 'bg-blue-600 text-white ring-4 ring-blue-100' : 'bg-slate-200 text-slate-500';
      const labelClass = isDone ? 'text-xs font-medium text-slate-500' : isActive ? 'text-xs font-bold text-slate-900' : 'text-xs font-medium text-slate-400';
      const icon = isDone ? '\u2713' : n;
      const connector = n < 5 ? `<div class="flex-1 h-0.5 mx-2 ${isDone ? 'bg-emerald-500' : 'bg-slate-200'}"></div>` : '';
      return `
        <div class="flex items-center ${n < 5 ? 'flex-1' : ''}">
          <div class="flex flex-col items-center cursor-pointer" onclick="Stepper.goToStep(${n})">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${circleClass}">${icon}</div>
            <span class="${labelClass} mt-1 whitespace-nowrap">${label}</span>
          </div>
          ${connector}
        </div>`;
    }).join('');
  }
};

window.Stepper = Stepper;
