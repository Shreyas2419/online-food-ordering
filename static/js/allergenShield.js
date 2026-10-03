/**
 * Allergen Shield Engine & Dynamic Card Separation
 */
import { store } from './state.js';
import { optimisticCart } from './optimisticCart.js';
import { formatINR } from './currency.js';

export class AllergenShieldEngine {
  constructor() {
    this.pillsContainer = document.getElementById('allergenPills');
    this.statusIndicator = document.getElementById('shieldStatusIndicator');
    this.clearBtn = document.getElementById('clearShieldBtn');
    this.swapModalBackdrop = document.getElementById('swapModalBackdrop');
    this.swapModalBody = document.getElementById('swapModalBody');
    this.swapModalClose = document.getElementById('swapModalClose');

    this.bindEvents();
    this.renderPills();
  }

  bindEvents() {
    if (this.clearBtn) {
      this.clearBtn.addEventListener('click', () => {
        store.clearAllergens();
      });
    }

    if (this.swapModalClose) {
      this.swapModalClose.addEventListener('click', () => {
        this.closeSwapModal();
      });
    }

    if (this.swapModalBackdrop) {
      this.swapModalBackdrop.addEventListener('click', (e) => {
        if (e.target === this.swapModalBackdrop) {
          this.closeSwapModal();
        }
      });
    }

    // Subscribe to store updates
    store.subscribe((state, event) => {
      if (event === 'ALLERGENS_CHANGED' || event === 'MENU_UPDATED') {
        this.updatePillStates();
        this.updateStatusIndicator();
      }
    });
  }

  renderPills() {
    const categories = [
      { id: 'peanuts', label: 'Peanut-Free', icon: '🥜' },
      { id: 'gluten', label: 'Gluten-Free', icon: '🌾' },
      { id: 'dairy', label: 'Dairy-Free', icon: '🥛' },
      { id: 'soy', label: 'Soy-Free', icon: '🌱' },
      { id: 'shellfish', label: 'Shellfish-Free', icon: '🦐' }
    ];

    if (!this.pillsContainer) return;

    this.pillsContainer.innerHTML = categories.map((cat) => `
      <button class="allergen-pill anim-bounce-click" data-allergen="${cat.id}">
        <span class="pill-icon">${cat.icon}</span>
        <span>${cat.label}</span>
      </button>
    `).join('');

    this.pillsContainer.querySelectorAll('.allergen-pill').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const allergen = btn.dataset.allergen;
        store.toggleAllergen(allergen);
      });
    });

    this.updatePillStates();
    this.updateStatusIndicator();
  }

  updatePillStates() {
    if (!this.pillsContainer) return;
    const active = store.state.activeAllergens;
    this.pillsContainer.querySelectorAll('.allergen-pill').forEach((btn) => {
      const id = btn.dataset.allergen;
      if (active.has(id)) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  updateStatusIndicator() {
    if (!this.statusIndicator) return;
    const count = store.state.activeAllergens.size;
    const items = store.state.filteredItems;
    const safeCount = items.filter(i => i.safe).length;
    const unsafeCount = items.length - safeCount;

    if (count === 0) {
      this.statusIndicator.classList.remove('active');
      this.statusIndicator.innerHTML = `<span>🛡️ Shield Inactive (Tap pills to guard)</span>`;
      if (this.clearBtn) this.clearBtn.style.display = 'none';
    } else {
      this.statusIndicator.classList.add('active');
      this.statusIndicator.innerHTML = `
        <span>🛡️ <strong>${count} Filter${count > 1 ? 's' : ''} Active:</strong> ${safeCount} Safe • ${unsafeCount} High-Risk Alerted</span>
      `;
      if (this.clearBtn) this.clearBtn.style.display = 'inline-block';
    }
  }

  /**
   * Opens the Exclude / Swap Ingredient Request Modal
   */
  openSwapModal(dish) {
    if (!this.swapModalBackdrop || !this.swapModalBody) return;

    const detected = dish.detectedAllergens || [];
    const detectedNames = detected.map(d => d.toUpperCase()).join(', ');

    let swapsHtml = '';
    if (dish.customizable && dish.customization_schema) {
      swapsHtml = `
        <div style="margin-top: 1rem; padding: 1rem; background: rgba(204, 255, 0, 0.08); border: 1px solid var(--accent-lime); border-radius: var(--radius-md);">
          <h4 style="color: var(--accent-lime); margin-bottom: 0.4rem; font-size: 0.95rem;">✨ Full Customizer Available!</h4>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.8rem;">
            This dish is fully modular. You can substitute crusts, bases, or crunch layers in our 3D Bowl/Pizza Builder.
          </p>
          <button id="openCustomizerFromSwapBtn" class="btn-action-primary" style="font-size: 0.85rem; padding: 0.6rem 1rem;">
            Open Visual Builder for ${dish.name}
          </button>
        </div>
      `;
    } else {
      swapsHtml = `
        <div style="margin-top: 1.25rem;">
          <h4 style="font-size: 0.95rem; margin-bottom: 0.6rem; color: var(--text-main);">Available Zero-G Safe Kitchen Swaps:</h4>
          <div style="display: flex; flex-direction: column; gap: 0.6rem;">
            ${detected.map(allergen => `
              <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--glass-white-border); padding: 0.8rem; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: space-between;">
                <div>
                  <div style="font-weight: 700; font-size: 0.85rem; color: var(--accent-coral);">Exclude ${allergen.toUpperCase()}</div>
                  <div style="font-size: 0.78rem; color: var(--text-muted);">Replace with allergen-free roasted seeds & chef dressing</div>
                </div>
                <button class="btn-swap-apply btn-action-primary anim-bounce-click" data-allergen="${allergen}" style="padding: 0.4rem 0.8rem; font-size: 0.78rem; width: auto;">
                  Apply & Add (${formatINR(dish.base_price)})
                </button>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    this.swapModalBody.innerHTML = `
      <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 1.25rem;">
        <img src="${dish.image_url}" alt="${dish.name}" style="width: 75px; height: 75px; border-radius: var(--radius-md); object-fit: cover;">
        <div>
          <h3 style="font-family: var(--font-display); font-size: 1.15rem; margin-bottom: 0.25rem;">${dish.name}</h3>
          <div style="color: var(--accent-coral); font-size: 0.82rem; font-weight: 700;">
            ⚠️ Conflicts with your Allergen Shield: ${detectedNames}
          </div>
        </div>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.45;">
        ${dish.description}
      </p>
      ${swapsHtml}
    `;

    // Hook up buttons inside modal
    const customizerBtn = document.getElementById('openCustomizerFromSwapBtn');
    if (customizerBtn) {
      customizerBtn.addEventListener('click', () => {
        this.closeSwapModal();
        window.openCustomizerModal(dish);
      });
    }

    this.swapModalBody.querySelectorAll('.btn-swap-apply').forEach(btn => {
      btn.addEventListener('click', () => {
        const allergen = btn.dataset.allergen;
        optimisticCart.addItem(dish, [
          {
            step_id: 'allergen_swap',
            option_id: `exclude-${allergen}`,
            name: `Zero-G Safe Modification: Exclude ${allergen.toUpperCase()}`,
            price: 0.0,
            calories: -10,
            allergens: []
          }
        ]);
        this.closeSwapModal();
      });
    });

    this.swapModalBackdrop.classList.add('open');
  }

  closeSwapModal() {
    if (this.swapModalBackdrop) {
      this.swapModalBackdrop.classList.remove('open');
    }
  }
}
