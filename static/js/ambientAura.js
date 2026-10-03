/**
 * Ambient Aura & Highlightable Background Controller for Faura.
 * Controls the luminous radiant background layer behind the master card container,
 * with interactive cursor spotlight tracking and switchable color themes (Saffron, Gold, Terracotta, Emerald, Pulse).
 */
export class AmbientAuraController {
  constructor() {
    this.body = document.body;
    this.spotlight = document.getElementById('ambientAuraSpotlight');
    this.toolbar = document.getElementById('auraHighlightToolbar');
    this.buttons = document.querySelectorAll('.aura-btn');
    this.currentTheme = localStorage.getItem('faura_aura_theme') || 'saffron';

    this.init();
  }

  init() {
    this.setTheme(this.currentTheme);
    this.bindPointerTracking();
    this.bindToolbarEvents();
    this.bindBackdropClick();
  }

  setTheme(theme) {
    this.currentTheme = theme;
    this.body.setAttribute('data-aura', theme);
    localStorage.setItem('faura_aura_theme', theme);

    this.buttons.forEach(btn => {
      const isSelected = btn.getAttribute('data-aura') === theme;
      btn.classList.toggle('active', isSelected);
      btn.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
    });
  }

  bindToolbarEvents() {
    this.buttons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const theme = btn.getAttribute('data-aura');
        if (theme) this.setTheme(theme);
      });
    });
  }

  bindPointerTracking() {
    let ticking = false;

    window.addEventListener('pointermove', (e) => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const xPercent = (e.clientX / window.innerWidth) * 100;
          const yPercent = (e.clientY / window.innerHeight) * 100;

          document.documentElement.style.setProperty('--mouse-x', `${xPercent.toFixed(1)}%`);
          document.documentElement.style.setProperty('--mouse-y', `${yPercent.toFixed(1)}%`);
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  bindBackdropClick() {
    // Clicking outside the main card container cycles or triggers highlight pulse
    window.addEventListener('click', (e) => {
      if (e.target === document.body || e.target.classList.contains('main-backdrop-highlight')) {
        const themes = ['saffron', 'gold', 'terracotta', 'emerald', 'pulse'];
        const nextIndex = (themes.indexOf(this.currentTheme) + 1) % themes.length;
        this.setTheme(themes[nextIndex]);
      }
    });
  }
}
