import { store } from './state.js';

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

export class AccountMenuFeatures {
  constructor() {
    this.backdrop = document.getElementById('accountModalBackdrop');
    this.authForm = document.getElementById('accountAuthForm');
    this.profileSection = document.getElementById('accountProfile');
    this.status = document.getElementById('accountStatus');
    this.signupMode = true;
    this.bindEvents();
    this.loadRestaurants();
    if (store.state.profile.accessToken) this.loadProfile();
    this.updateAccountButton();
  }

  bindEvents() {
    document.getElementById('accountOpenBtn')?.addEventListener('click', () => this.open());
    document.getElementById('accountModalClose')?.addEventListener('click', () => this.backdrop.classList.remove('open'));
    this.backdrop?.addEventListener('click', (event) => {
      if (event.target === this.backdrop) this.backdrop.classList.remove('open');
    });
    document.getElementById('accountModeBtn')?.addEventListener('click', () => this.setMode(!this.signupMode));
    this.authForm?.addEventListener('submit', (event) => this.submitAuth(event));
    document.getElementById('accountSignOutBtn')?.addEventListener('click', () => {
      store.setProfile(null, null);
      this.profileSection.hidden = true;
      this.authForm.hidden = false;
      this.setStatus('You are signed out.');
      this.updateAccountButton();
    });
    document.getElementById('addressForm')?.addEventListener('submit', (event) => this.addAddress(event));
    document.getElementById('profileDetailsForm')?.addEventListener('submit', (event) => this.saveProfile(event));
    document.getElementById('dietaryPreferencesForm')?.addEventListener('submit', (event) => this.savePreferences(event));
    document.getElementById('walletTopUpForm')?.addEventListener('submit', (event) => this.topUpTokens(event));
    document.getElementById('premiumActivateBtn')?.addEventListener('click', () => this.activatePremium());
    document.getElementById('dietaryTabs')?.addEventListener('click', (event) => {
      const button = event.target.closest('[data-dietary]');
      if (!button) return;
      document.querySelectorAll('.dietary-tab').forEach((tab) => tab.classList.toggle('active', tab === button));
      store.setDietaryType(button.dataset.dietary);
    });
    document.getElementById('restaurantGrid')?.addEventListener('click', (event) => {
      const button = event.target.closest('[data-restaurant]');
      if (!button) return;
      document.querySelectorAll('.restaurant-card').forEach((card) => card.classList.toggle('active', card === button));
      store.setRestaurant(button.dataset.restaurant === 'all' ? null : button.dataset.restaurant);
    });
    store.subscribe((state, event) => {
      if (event === 'PROFILE_UPDATED') this.updateAccountButton();
    });
  }

  open() {
    this.backdrop.classList.add('open');
    if (store.state.profile.accessToken) this.loadProfile();
  }

  setMode(signup) {
    this.signupMode = signup;
    const nameInput = this.authForm.elements.display_name;
    const phoneInput = this.authForm.elements.phone;
    nameInput.hidden = !signup;
    nameInput.required = signup;
    phoneInput.hidden = !signup;
    this.authForm.elements.password.autocomplete = signup ? 'new-password' : 'current-password';
    document.getElementById('accountModalTitle').textContent = signup ? 'Create your account' : 'Welcome back';
    document.getElementById('accountModalSubtitle').textContent = signup ? 'Your orders, preferences, and wallet in one place' : 'Sign in to manage your account';
    document.getElementById('accountSubmitBtn').textContent = signup ? 'Create account' : 'Sign in';
    document.getElementById('accountModeBtn').textContent = signup ? 'Already registered? Sign in' : 'New here? Create an account';
    this.setStatus('');
  }

  setStatus(message, isError = false) {
    if (!this.status) return;
    this.status.textContent = message;
    this.status.classList.toggle('is-error', isError);
  }

  async request(url, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (store.state.profile.accessToken) headers.Authorization = `Bearer ${store.state.profile.accessToken}`;
    const response = await fetch(url, { ...options, headers });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail?.message || data.detail || 'Request failed');
    return data;
  }

  async submitAuth(event) {
    event.preventDefault();
    const form = new FormData(this.authForm);
    const payload = Object.fromEntries(form.entries());
    try {
      const result = await this.request(`/api/v1/account/${this.signupMode ? 'signup' : 'login'}`, {
        method: 'POST', body: JSON.stringify(payload),
      });
      store.setProfile(result.access_token, result.user);
      await this.loadProfile();
      this.setStatus(`Welcome, ${result.user.display_name}.`);
      this.updateAccountButton();
    } catch (error) {
      this.setStatus(error.message, true);
    }
  }

  async loadProfile() {
    try {
      const profile = await this.request('/api/v1/account/me');
      store.updateProfile(profile);
      this.authForm.hidden = true;
      this.profileSection.hidden = false;
      this.renderProfile(profile);
    } catch (error) {
      store.setProfile(null, null);
      this.authForm.hidden = false;
      this.profileSection.hidden = true;
      this.setStatus(error.message, true);
    }
  }

  renderProfile(profile) {
    document.getElementById('walletBalance').textContent = `₹${Number(profile.wallet_tokens).toFixed(2)} tokens`;
    document.getElementById('premiumStatus').textContent = profile.premium ? `Premium · until ${new Date(profile.premium_until).toLocaleDateString('en-IN')}` : 'Standard';
    document.getElementById('premiumActivateBtn').textContent = profile.premium ? 'Premium active' : 'Activate 30-day Premium · 499 tokens';
    document.getElementById('premiumActivateBtn').disabled = profile.premium;
    document.querySelector('#profileDetailsForm [name="display_name"]').value = profile.display_name;
    document.querySelector('#profileDetailsForm [name="phone"]').value = profile.phone || '';
    const preferences = this.authForm.closest('.modal-card').querySelector('#dietaryPreferencesForm [name="dietary_preferences"]');
    [...preferences.options].forEach((option) => { option.selected = profile.dietary_preferences.includes(option.value); });
    document.getElementById('savedAddressList').innerHTML = profile.addresses.length
      ? profile.addresses.map((address) => `<div class="profile-list-row"><strong>${escapeHtml(address.label)}${address.is_default ? ' · Default' : ''}</strong><span>${escapeHtml(address.address)} ${escapeHtml(address.postal_code)}</span></div>`).join('')
      : '<p class="empty-profile-note">No saved addresses yet.</p>';
    document.getElementById('orderHistoryList').innerHTML = profile.orders.length
      ? profile.orders.map((order) => `<div class="profile-list-row"><div><strong>${escapeHtml(order.order_id)}</strong><span>${escapeHtml(order.status)} · ₹${Number(order.total_amount).toFixed(2)}</span></div><button type="button" class="text-action reorder-order" data-order="${escapeHtml(order.order_id)}">Reorder</button></div>`).join('')
      : '<p class="empty-profile-note">Your past orders will appear here.</p>';
    document.querySelectorAll('.reorder-order').forEach((button) => button.addEventListener('click', () => this.reorder(button.dataset.order)));
  }

  updateAccountButton() {
    const user = store.state.profile.user;
    document.getElementById('accountButtonLabel').textContent = user?.display_name || 'Sign in';
  }

  async addAddress(event) {
    event.preventDefault();
    try {
      await this.request('/api/v1/account/addresses', { method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(event.target).entries())) });
      event.target.reset();
      event.target.elements.label.value = 'Home';
      await this.loadProfile();
      this.setStatus('Address saved.');
    } catch (error) { this.setStatus(error.message, true); }
  }

  async savePreferences(event) {
    event.preventDefault();
    const selected = [...event.target.elements.dietary_preferences.selectedOptions].map((option) => option.value);
    try {
      const profile = await this.request('/api/v1/account/me', {
        method: 'PATCH', body: JSON.stringify({ dietary_preferences: selected }),
      });
      store.updateProfile(profile);
      await this.loadProfile();
      this.setStatus('Preferences saved.');
    } catch (error) { this.setStatus(error.message, true); }
  }

  async saveProfile(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.target).entries());
    try {
      const profile = await this.request('/api/v1/account/me', {
        method: 'PATCH', body: JSON.stringify(values),
      });
      store.updateProfile(profile);
      await this.loadProfile();
      this.setStatus('Profile saved.');
    } catch (error) { this.setStatus(error.message, true); }
  }

  async topUpTokens(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.target).entries());
    values.amount = Number(values.amount);
    try {
      const result = await this.request('/api/v1/account/tokens/top-up', { method: 'POST', body: JSON.stringify(values) });
      this.setStatus(`Top-up ${result.status}. Wallet tokens are added after payment confirmation.`);
    } catch (error) { this.setStatus(error.message, true); }
  }

  async activatePremium() {
    try {
      const profile = await this.request('/api/v1/account/premium', { method: 'POST', body: '{}' });
      store.updateProfile(profile);
      await this.loadProfile();
      this.setStatus('Premium active for 30 days.');
    } catch (error) { this.setStatus(error.message, true); }
  }

  async reorder(orderId) {
    try {
      const order = await this.request(`/api/v1/orders/${encodeURIComponent(orderId)}`);
      const menu = store.state.menuItems;
      for (const item of order.items) {
        const selections = item.selections || [];
        const dish = menu.find((candidate) => candidate.id === item.dish_id) || {
          id: item.dish_id,
          name: item.name,
          base_price: item.base_price ?? (item.unit_price - selections.reduce((sum, selection) => sum + selection.price, 0)),
          calories: item.calories || 0,
          image_url: item.image_url,
          prep_time_mins: item.prep_time_mins || 12,
          allergens: [],
        };
        await window.optimisticCart.addItem(dish, selections, item.quantity || 1);
      }
      this.backdrop.classList.remove('open');
      window.optimisticCart.openDrawer();
    } catch (error) { this.setStatus(error.message, true); }
  }

  async loadRestaurants() {
    try {
      const restaurants = await fetch('/api/v1/restaurants').then((response) => response.json());
      store.state.restaurants = restaurants;
      const grid = document.getElementById('restaurantGrid');
      grid.innerHTML = [
        '<button type="button" class="restaurant-card active" data-restaurant="all"><strong>All restaurants</strong><span>Browse every kitchen</span></button>',
        ...restaurants.map((restaurant) => `<button type="button" class="restaurant-card" data-restaurant="${escapeHtml(restaurant.id)}"><img src="${escapeHtml(restaurant.logo_url || restaurant.image_url)}" alt="" loading="lazy"><strong>${escapeHtml(restaurant.name)}</strong><span>${(restaurant.tags || restaurant.cuisine_tags).map(escapeHtml).join(' · ')}</span><small>★ ${Number(restaurant.rating).toFixed(1)} · ${restaurant.delivery_sla_mins} min · ${Number(restaurant.distance_km).toFixed(1)} km</small></button>`),
      ].join('');
    } catch (error) { console.warn('Restaurant list unavailable:', error); }
  }
}
