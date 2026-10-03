import { formatINR } from './currency.js';

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

const CATEGORY_LABELS = {
  base: '1 · Choose a base',
  protein: '2 · Choose a protein',
  topping: '3 · Choose 1–3 toppings',
  dressing: '4 · Choose a dressing',
};

export class SpecialtyMenus {
  constructor() {
    this.premiumGrid = document.getElementById('premiumDishGrid');
    this.builderOptions = document.getElementById('customBuilderOptions');
    this.builderForm = document.getElementById('customMealForm');
    this.builderStatus = document.getElementById('customBuilderStatus');
    this.builderPrice = document.getElementById('customBuilderPrice');
    this.builderButton = document.getElementById('customBuilderAddBtn');
    this.options = [];
    this.dish = null;
    this.loadPremium();
    this.loadBuilder();
    this.premiumGrid?.addEventListener('click', (event) => this.addPremiumDish(event));
    this.builderOptions?.addEventListener('change', (event) => this.onBuilderChange(event));
    this.builderForm?.addEventListener('submit', (event) => this.addCustomMeal(event));
  }

  async loadPremium() {
    try {
      const response = await fetch('/api/dishes/premium');
      if (!response.ok) throw new Error('Premium selection is unavailable.');
      const dishes = await response.json();
      this.premiumGrid.innerHTML = dishes.map((dish) => `
        <article class="dish-card premium-card">
          <span class="premium-badge">Gourmet · Chef selected</span>
          <div class="card-image-wrap"><img class="card-img" src="${escapeHtml(dish.image_url)}" alt="${escapeHtml(dish.name)}" loading="lazy" onerror="this.closest('.dish-card')?.remove()"></div>
          <div class="card-content">
            <div class="card-title-row"><h3 class="dish-name">${escapeHtml(dish.name)}</h3><span class="dish-price">${formatINR(dish.base_price)}</span></div>
            <div class="dish-meta"><span>${escapeHtml(dish.category)}</span><span>${Number(dish.rating).toFixed(1)} ★</span></div>
            <p class="dish-desc">${escapeHtml(dish.description)}</p>
            <button class="btn-order-now" type="button" data-premium-id="${escapeHtml(dish.id)}">Add to order</button>
          </div>
        </article>`).join('');
    } catch (error) {
      this.premiumGrid.innerHTML = `<p role="status">${escapeHtml(error.message)}</p>`;
    }
  }

  async addPremiumDish(event) {
    const button = event.target.closest('[data-premium-id]');
    if (!button) return;
    const dishId = button.dataset.premiumId;
    try {
      const response = await fetch('/api/dishes/premium');
      if (!response.ok) throw new Error('Could not load gourmet dishes.');
      const dish = (await response.json()).find((item) => item.id === dishId);
      if (!dish) throw new Error('This dish is no longer available.');
      await window.optimisticCart.addItem(dish);
    } catch (error) {
      document.getElementById('customBuilderStatus').textContent = error.message;
    }
  }

  async loadBuilder() {
    try {
      const response = await fetch('/api/custom-builder/options');
      if (!response.ok) throw new Error('Meal builder is unavailable.');
      const data = await response.json();
      this.dish = data.dish;
      this.options = data.options;
      this.renderBuilder();
      this.builderStatus.textContent = 'Select one base, one protein, one to three toppings, and one dressing.';
      this.updateBuilderTotal();
    } catch (error) {
      this.builderStatus.textContent = error.message;
    }
  }

  renderBuilder() {
    const categories = ['base', 'protein', 'topping', 'dressing'];
    this.builderOptions.innerHTML = categories.map((category) => {
      const multi = category === 'topping';
      return `<fieldset class="custom-builder-group"><legend>${CATEGORY_LABELS[category]}</legend>${this.options
        .filter((option) => option.category === category)
        .map((option) => `<label class="custom-builder-choice">
          <input type="${multi ? 'checkbox' : 'radio'}" name="builder-${category}" value="${escapeHtml(option.id)}" data-price="${Number(option.price)}" ${multi ? 'data-topping="true"' : ''}>
          <span>${escapeHtml(option.name)}${option.allergens.length ? ` · contains ${escapeHtml(option.allergens.join(', '))}` : ''}</span>
          <strong>${option.price ? `+${formatINR(option.price)}` : 'Included'}</strong>
        </label>`).join('')}</fieldset>`;
    }).join('');
  }

  onBuilderChange(event) {
    if (event.target.matches('[data-topping]:checked')) {
      const selectedToppings = this.builderOptions.querySelectorAll('[data-topping]:checked');
      if (selectedToppings.length > 3) {
        event.target.checked = false;
        this.builderStatus.textContent = 'Choose no more than three toppings.';
      }
    }
    this.updateBuilderTotal();
  }

  updateBuilderTotal() {
    if (!this.dish) return;
    const selected = [...this.builderOptions.querySelectorAll('input:checked')];
    const total = this.dish.base_price + selected.reduce((sum, input) => sum + Number(input.dataset.price), 0);
    const categories = ['base', 'protein', 'topping', 'dressing'];
    const valid = categories.every((category) => this.builderOptions.querySelectorAll(`input[name="builder-${category}"]:checked`).length > 0);
    this.builderPrice.textContent = formatINR(total);
    this.builderButton.disabled = !valid;
  }

  async addCustomMeal(event) {
    event.preventDefault();
    const optionIds = [...this.builderOptions.querySelectorAll('input:checked')].map((input) => input.value);
    this.builderButton.disabled = true;
    this.builderStatus.textContent = 'Confirming your ingredient prices…';
    try {
      const response = await fetch('/api/cart/add-custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option_ids: optionIds, quantity: 1 }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not add this custom meal.');
      await window.optimisticCart.addItem(data.dish, data.selections, data.quantity);
      this.builderStatus.textContent = 'Your custom bowl is in the cart.';
    } catch (error) {
      this.builderStatus.textContent = error.message;
    } finally {
      this.updateBuilderTotal();
    }
  }
}