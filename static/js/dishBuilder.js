/**
 * Interactive Visual Dish Builder
 * Step-by-step modular customizer for bowls/pizzas with dynamic live price/calorie recalculation.
 */
import { store } from './state.js';
import { optimisticCart } from './optimisticCart.js';
import { formatINR } from './currency.js';

export class DishBuilder {
  constructor() {
    this.modalBackdrop = document.getElementById('customizerModalBackdrop');
    this.modalTitle = document.getElementById('customizerModalTitle');
    this.modalBody = document.getElementById('customizerModalBody');
    this.modalClose = document.getElementById('customizerModalClose');
    this.livePriceEl = document.getElementById('customizerLivePrice');
    this.liveCalsEl = document.getElementById('customizerLiveCals');
    this.addToCartBtn = document.getElementById('customizerAddToCartBtn');

    this.currentDish = null;
    this.selectedOptions = {}; // { step_id: [option_id, ...] }

    this.bindEvents();
  }

  bindEvents() {
    if (this.modalClose) {
      this.modalClose.addEventListener('click', () => this.close());
    }
    if (this.modalBackdrop) {
      this.modalBackdrop.addEventListener('click', (e) => {
        if (e.target === this.modalBackdrop) this.close();
      });
    }
    if (this.addToCartBtn) {
      this.addToCartBtn.addEventListener('click', () => this.submitCustomization());
    }
  }

  open(dish) {
    this.currentDish = dish;
    this.selectedOptions = {};

    // Select defaults for each step
    if (dish.customization_schema) {
      dish.customization_schema.forEach((step) => {
        // Pick first option as default for single select
        if (step.min_select > 0 && step.options.length > 0) {
          this.selectedOptions[step.step_id] = [step.options[0].id];
        } else {
          this.selectedOptions[step.step_id] = [];
        }
      });
    }

    if (this.modalTitle) {
      this.modalTitle.textContent = `Build Your ${dish.name}`;
    }

    this.renderSteps();
    this.updateLiveCalculations();
    this.modalBackdrop.classList.add('open');
  }

  close() {
    if (this.modalBackdrop) {
      this.modalBackdrop.classList.remove('open');
    }
  }

  renderSteps() {
    if (!this.modalBody || !this.currentDish.customization_schema) return;

    const activeAllergens = [...store.state.activeAllergens];
    const steps = this.currentDish.customization_schema;

    this.modalBody.innerHTML = steps.map((step, idx) => {
      const isMulti = step.max_select > 1;
      const currentSelected = this.selectedOptions[step.step_id] || [];

      return `
        <div class="customizer-step" data-step-id="${step.step_id}">
          <div class="step-heading">
            <span>${step.title}</span>
            <span style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">
              ${isMulti ? `Select up to ${step.max_select}` : (step.min_select === 0 ? 'Optional' : 'Required (Pick 1)')}
            </span>
          </div>
          ${step.description ? `<div class="step-desc">${step.description}</div>` : ''}
          <div class="options-group">
            ${step.options.map((opt) => {
              const isSelected = currentSelected.includes(opt.id);
              // Check if option introduces any active allergens
              const optionAllergenConflicts = opt.allergens ? opt.allergens.filter(a => activeAllergens.includes(a.toLowerCase())) : [];
              const hasConflict = optionAllergenConflicts.length > 0;

              return `
                <div class="option-choice-card anim-bounce-click ${isSelected ? 'selected' : ''}" 
                     data-step-id="${step.step_id}" 
                     data-option-id="${opt.id}" 
                     data-multi="${isMulti ? 'true' : 'false'}"
                     data-max="${step.max_select}">
                  <div class="option-left">
                    <div class="radio-indicator">
                      ${isSelected ? `<span style="font-size: 10px; color: #0F0F12;">✔</span>` : ''}
                    </div>
                    <div>
                      <span class="option-name">${opt.name}</span>
                      ${hasConflict ? `<span class="option-allergen-tag">⚠️ Contains ${optionAllergenConflicts.join(', ')}</span>` : ''}
                      ${opt.is_safe_swap ? `<span class="option-swap-tag">🛡️ Allergen Safe Swap</span>` : ''}
                    </div>
                  </div>
                  <div class="option-right">
                    <span>${opt.calories > 0 ? `+${opt.calories} cal` : ''}</span>
                    <span class="option-price-tag">${opt.price > 0 ? `+${formatINR(opt.price)}` : 'INCLUDED'}</span>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }).join('');

    // Attach click listeners to options
    this.modalBody.querySelectorAll('.option-choice-card').forEach((card) => {
      card.addEventListener('click', () => {
        const stepId = card.dataset.stepId;
        const optId = card.dataset.optionId;
        const isMulti = card.dataset.multi === 'true';
        const maxSelect = parseInt(card.dataset.max, 10);

        if (!this.selectedOptions[stepId]) {
          this.selectedOptions[stepId] = [];
        }

        if (isMulti) {
          const index = this.selectedOptions[stepId].indexOf(optId);
          if (index > -1) {
            this.selectedOptions[stepId].splice(index, 1);
          } else {
            if (this.selectedOptions[stepId].length < maxSelect) {
              this.selectedOptions[stepId].push(optId);
            }
          }
        } else {
          this.selectedOptions[stepId] = [optId];
        }

        this.renderSteps();
        this.updateLiveCalculations();
      });
    });
  }

  updateLiveCalculations() {
    if (!this.currentDish) return;

    let totalPrice = this.currentDish.base_price;
    let totalCals = this.currentDish.calories;

    if (this.currentDish.customization_schema) {
      this.currentDish.customization_schema.forEach((step) => {
        const selectedIds = this.selectedOptions[step.step_id] || [];
        step.options.forEach((opt) => {
          if (selectedIds.includes(opt.id)) {
            totalPrice += opt.price;
            totalCals += opt.calories;
          }
        });
      });
    }

    if (this.livePriceEl) {
      this.livePriceEl.textContent = formatINR(totalPrice);
    }
    if (this.liveCalsEl) {
      this.liveCalsEl.textContent = `${totalCals} TOTAL CALS`;
    }
  }

  submitCustomization() {
    if (!this.currentDish) return;

    const selectionsList = [];
    if (this.currentDish.customization_schema) {
      this.currentDish.customization_schema.forEach((step) => {
        const selectedIds = this.selectedOptions[step.step_id] || [];
        step.options.forEach((opt) => {
          if (selectedIds.includes(opt.id)) {
            selectionsList.push({
              step_id: step.step_id,
              option_id: opt.id,
              name: opt.name,
              price: opt.price,
              calories: opt.calories,
              allergens: opt.allergens || []
            });
          }
        });
      });
    }

    optimisticCart.addItem(this.currentDish, selectionsList);
    this.close();
  }
}
