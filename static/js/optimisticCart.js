/**
 * Optimistic Cart Engine & Floating Capsule
 * Handles instantaneous UI state updates with rollback resilience and dynamic SLA calculations.
 */
import { store } from './state.js';
import { formatINR } from './currency.js';
import { couponManager } from './couponManager.js';

export class OptimisticCartEngine {
  constructor() {
    this.capsule = document.getElementById('floatingCartCapsule');
    this.badgeCount = document.getElementById('cartBadgeCount');
    this.capsuleSubtotal = document.getElementById('cartCapsuleSubtotal');
    this.thresholdLabel = document.getElementById('thresholdLabel');
    this.thresholdFill = document.getElementById('thresholdProgressFill');
    this.openCartBtn = document.getElementById('openCartBtn');

    // Drawer elements
    this.drawerBackdrop = document.getElementById('cartDrawerBackdrop');
    this.drawerClose = document.getElementById('cartDrawerClose');
    this.drawerItemsList = document.getElementById('drawerItemsList');
    this.drawerSubtotal = document.getElementById('drawerSubtotal');
    this.drawerDeliveryFee = document.getElementById('drawerDeliveryFee');
    this.drawerTotal = document.getElementById('drawerTotal');
    this.drawerEta = document.getElementById('drawerEta');
    this.drawerCodCancellationBanner = document.getElementById('drawerCodCancellationBanner');
    this.placeOrderBtn = document.getElementById('placeOrderBtn');
    this.codFeeRow = document.getElementById('drawerCodFeeRow');
    this.expressFeeRow = document.getElementById('drawerExpressFeeRow');
    this.tokenDiscountRow = document.getElementById('drawerTokenDiscountRow');
    this.paymentInputs = document.querySelectorAll('input[name="paymentMethod"]');
    this.deliveryInputs = document.querySelectorAll('input[name="deliveryMode"]');

    // Feature 2: Promo Code / Coupon Elements
    this.promoToggle = document.getElementById('promoToggleBtn');
    this.promoInputGroup = document.getElementById('promoInputGroup');
    this.promoInput = document.getElementById('promoCodeInput');
    this.promoApplyBtn = document.getElementById('promoApplyBtn');
    this.promoStatusMsg = document.getElementById('promoStatusMsg');
    this.drawerCouponRow = document.getElementById('drawerCouponRow');
    this.drawerCouponDiscount = document.getElementById('drawerCouponDiscount');

    this.bindEvents();
    this.recalculateLocally();
    this.syncWithBackend();
  }

  bindEvents() {
    if (this.openCartBtn) {
      this.openCartBtn.addEventListener('click', () => this.openDrawer());
    }
    if (this.drawerClose) {
      this.drawerClose.addEventListener('click', () => this.closeDrawer());
    }
    if (this.drawerBackdrop) {
      this.drawerBackdrop.addEventListener('click', (e) => {
        if (e.target === this.drawerBackdrop) this.closeDrawer();
      });
    }



    if (this.placeOrderBtn) {
      this.placeOrderBtn.addEventListener('click', () => this.placeOrder());
    }
    this.paymentInputs.forEach((input) => input.addEventListener('change', () => {
      store.setPaymentMethod(input.value);
      if (this.drawerCodCancellationBanner) {
        this.drawerCodCancellationBanner.style.display = input.value === 'cod' ? 'flex' : 'none';
      }
      this.recalculateLocally();
      this.syncWithBackend().catch((error) => this.showToast(error.message, 'coral'));
    }));
    this.deliveryInputs.forEach((input) => input.addEventListener('change', () => {
      store.setDeliveryMode(input.value);
      this.recalculateLocally();
      this.syncWithBackend().catch((error) => this.showToast(error.message, 'coral'));
    }));

    // Promo code event bindings
    if (this.promoToggle && this.promoInputGroup) {
      this.promoToggle.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = window.getComputedStyle(this.promoInputGroup).display === 'none';
        this.promoInputGroup.style.display = isHidden ? 'flex' : 'none';
        if (isHidden && this.promoInput) this.promoInput.focus();
      });
    }

    if (this.promoApplyBtn && this.promoInput) {
      this.promoApplyBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleApplyPromo();
      });
      this.promoInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.handleApplyPromo();
        }
      });
    }

    document.querySelectorAll('.promo-chip-btn').forEach((chip) => {
      chip.addEventListener('click', (e) => {
        e.preventDefault();
        if (this.promoInput) {
          this.promoInput.value = chip.dataset.code;
          if (this.promoInputGroup) this.promoInputGroup.style.display = 'flex';
          this.handleApplyPromo();
        }
      });
    });

    // Subscribe to store updates
    store.subscribe((state, event) => {
      if (event === 'CART_UPDATED' || event === 'ALLERGENS_CHANGED' || event === 'COUPON_APPLIED' || event === 'COUPON_REMOVED') {
        this.renderCapsule();
        this.renderDrawer();
      }
      if (event === 'PROFILE_UPDATED') {
        this.recalculateLocally();
        this.syncWithBackend().catch((error) => this.showToast(error.message, 'coral'));
      }
    });
  }

  async handleApplyPromo() {
    const code = this.promoInput?.value?.trim();
    const subtotal = store.state.cartSummary?.subtotal || 0;
    if (!code) return;

    if (this.promoApplyBtn) {
      this.promoApplyBtn.disabled = true;
      this.promoApplyBtn.textContent = 'Verifying...';
    }

    const result = await couponManager.applyCoupon(code, subtotal);
    if (this.promoApplyBtn) {
      this.promoApplyBtn.disabled = false;
      this.promoApplyBtn.textContent = 'Apply';
    }

    if (result.success) {
      if (this.promoStatusMsg) {
        this.promoStatusMsg.className = 'promo-status-msg success';
        this.promoStatusMsg.innerHTML = `<span>✓ <strong>${result.coupon.code}</strong> applied! ${result.message}</span> <button type="button" class="btn-remove-promo" id="removePromoBtn">✕ Remove</button>`;
        this.promoStatusMsg.style.display = 'flex';
        document.getElementById('removePromoBtn')?.addEventListener('click', () => {
          couponManager.removeCoupon();
          if (this.promoInput) this.promoInput.value = '';
          this.promoStatusMsg.style.display = 'none';
          this.recalculateLocally();
          this.syncWithBackend().catch(() => {});
        });
      }
      this.showToast(`Promo ${result.coupon.code} Applied!`, 'lime');
    } else {
      if (this.promoStatusMsg) {
        this.promoStatusMsg.className = 'promo-status-msg error';
        this.promoStatusMsg.innerHTML = `<span>⚠️ ${result.message}</span>`;
        this.promoStatusMsg.style.display = 'block';
      }
      this.showToast(result.message, 'coral');
    }

    this.recalculateLocally();
    this.syncWithBackend().catch(() => {});
  }

  openDrawer() {
    if (this.drawerBackdrop) {
      this.renderDrawer();
      this.drawerBackdrop.classList.add('open');
    }
  }

  closeDrawer() {
    if (this.drawerBackdrop) {
      this.drawerBackdrop.classList.remove('open');
    }
  }

  /**
   * Optimistically add item to cart with immediate UI increment.
   */
  async addItem(dish, selections = [], quantity = 1) {
    const previousCartState = JSON.parse(JSON.stringify(store.state.cart));

    // Calculate item pricing
    let unitPrice = dish.base_price;
    let itemCals = dish.calories;
    const selectionsSummary = [];

    selections.forEach(sel => {
      unitPrice += sel.price;
      itemCals += sel.calories;
      selectionsSummary.push(sel.name);
    });

    const cartKey = `${dish.id}-${selections.map(s => s.option_id).sort().join('|')}`;
    const existingIndex = store.state.cart.findIndex(i => i.cartKey === cartKey);

    if (existingIndex > -1) {
      store.state.cart[existingIndex].quantity += quantity;
    } else {
      store.state.cart.push({
        cartKey,
        dishId: dish.id,
        name: dish.name,
        image_url: dish.image_url,
        base_price: dish.base_price,
        unit_price: roundPrice(unitPrice),
        calories: itemCals,
        prep_time_mins: dish.prep_time_mins || 12,
        selections: selections,
        selectionsSummary,
        quantity: quantity
      });
    }

    // Trigger instant optimistic update
    store.saveCart();
    this.recalculateLocally();
    this.triggerCapsuleBounce();
    this.showToast(`Added ${dish.name} to Faura Order!`, 'lime');

    // Authoritative backend sync with rollback safety
    try {
      await this.syncWithBackend();
    } catch (err) {
      console.warn('Cart backend sync failed, rolling back state:', err);
      store.state.cart = previousCartState;
      store.saveCart();
      this.recalculateLocally();
      this.showToast('Network error: Cart state restored', 'coral');
    }
  }

  updateQuantity(cartKey, delta) {
    const previousCartState = JSON.parse(JSON.stringify(store.state.cart));
    const index = store.state.cart.findIndex(i => i.cartKey === cartKey);
    if (index === -1) return;

    store.state.cart[index].quantity += delta;
    if (store.state.cart[index].quantity <= 0) {
      store.state.cart.splice(index, 1);
    }

    store.saveCart();
    this.recalculateLocally();
    this.triggerCapsuleBounce();

    this.syncWithBackend().catch(() => {
      store.state.cart = previousCartState;
      store.saveCart();
      this.recalculateLocally();
      this.showToast('Failed to sync item count with server', 'coral');
    });
  }

  /**
   * Fast, synchronous client-side calculation for immediate 60fps response.
   */
  recalculateLocally() {
    const cart = store.state.cart;
    const queue = 3; // simulated active queue

    let subtotal = 0.0;
    let itemCount = 0;
    let maxPrep = 12;

    cart.forEach(item => {
      subtotal += item.unit_price * item.quantity;
      itemCount += item.quantity;
      maxPrep = Math.max(maxPrep, item.prep_time_mins || 12);
    });

    subtotal = roundPrice(subtotal);
    const threshold = 2075.00;
    const isPremium = Boolean(store.state.profile.user?.premium);
    const isFree = (subtotal >= threshold || isPremium) && subtotal > 0;
    const baseFee = 49.00;
    const deliveryFee = (isFree || itemCount === 0) ? 0.0 : baseFee;
    const codFee = store.state.paymentMethod === 'cod' && itemCount > 0 ? 10.0 : 0.0;
    const expressFee = store.state.deliveryMode === 'express' && itemCount > 0
      ? roundPrice(79.00 * (isPremium ? 0.9 : 1)) : 0.0;
    const tokenDiscount = isPremium && store.state.paymentMethod === 'tokens' ? roundPrice(subtotal * 0.1) : 0.0;

    // Feature 2: Active coupon evaluation
    const activeCoupon = couponManager.getActiveCoupon();
    let couponDiscount = 0.0;
    if (activeCoupon && subtotal >= (activeCoupon.minOrderValue || 0)) {
      if (activeCoupon.discountType === 'percentage') {
        const raw = subtotal * (activeCoupon.discountValue / 100);
        couponDiscount = roundPrice(activeCoupon.maxDiscountAmount ? Math.min(raw, activeCoupon.maxDiscountAmount) : raw);
      } else {
        couponDiscount = roundPrice(Math.min(activeCoupon.discountValue, subtotal));
      }
    }

    const amountNeeded = Math.max(0.0, roundPrice(threshold - subtotal));
    const total = roundPrice(Math.max(0.0, subtotal + deliveryFee + codFee + expressFee - tokenDiscount - couponDiscount));

    const transitMins = 10;
    const eta = maxPrep + (queue * 2) + (store.state.deliveryMode === 'express' ? 5 : transitMins);

    store.state.cartSummary = {
      itemCount,
      subtotal,
      deliveryFee,
      freeDeliveryThreshold: threshold,
      amountNeededForFreeDelivery: amountNeeded,
      isFreeDelivery: isFree,
      total,
      codFee,
      expressFee,
      tokenDiscount,
      couponCode: activeCoupon?.code || null,
      couponDiscount,
      paymentMethod: store.state.paymentMethod,
      deliveryMode: store.state.deliveryMode,
      etaMinutes: eta,
      prepTimeMins: maxPrep,
      activeKitchenQueue: queue,
      transitTimeMins: transitMins
    };

    store.notify('CART_UPDATED');
  }

  /**
   * Authoritative backend API sync with `/api/v1/cart`
   */
  async syncWithBackend() {
    const payload = {
      items: store.state.cart.map(i => ({
        dish_id: i.dishId,
        quantity: i.quantity,
        selections: i.selections || []
      })),
      active_allergens: [...store.state.activeAllergens],
      payment_method: store.state.paymentMethod,
      delivery_mode: store.state.deliveryMode,
      coupon_code: couponManager.getActiveCoupon()?.code || null,
    };

    const headers = { 'Content-Type': 'application/json' };
    if (store.state.profile.accessToken) headers.Authorization = `Bearer ${store.state.profile.accessToken}`;
    const res = await fetch('/api/v1/cart', {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Cart API validation failed');
    const data = await res.json();

    // Reconcile server verified pricing & ETA
    store.state.cartSummary = {
      itemCount: data.item_count,
      subtotal: data.subtotal,
      deliveryFee: data.delivery_fee,
      freeDeliveryThreshold: data.free_delivery_threshold,
      amountNeededForFreeDelivery: data.amount_needed_for_free_delivery,
      isFreeDelivery: data.is_free_delivery,
      total: data.total,
      codFee: data.cod_fee,
      expressFee: data.express_fee,
      tokenDiscount: data.token_discount,
      couponCode: data.coupon_code,
      couponDiscount: data.coupon_discount || 0.0,
      paymentMethod: data.payment_method,
      deliveryMode: data.delivery_mode,
      etaMinutes: data.eta_minutes,
      prepTimeMins: data.prep_time_mins,
      activeKitchenQueue: data.active_kitchen_queue,
      transitTimeMins: data.transit_time_mins
    };

    store.notify('CART_UPDATED');
  }

  renderCapsule() {
    const summary = store.state.cartSummary;
    if (!this.capsule) return;

    if (summary.itemCount === 0) {
      this.capsule.style.transform = 'translate(-50%, 120px)';
      this.capsule.style.opacity = '0';
      this.capsule.style.pointerEvents = 'none';
      return;
    }

    this.capsule.style.transform = 'translate(-50%, 0)';
    this.capsule.style.opacity = '1';
    this.capsule.style.pointerEvents = 'auto';

    if (this.badgeCount) this.badgeCount.textContent = summary.itemCount;
    if (this.capsuleSubtotal) this.capsuleSubtotal.textContent = formatINR(summary.subtotal);

    // Free delivery progress
    const progressPct = Math.min(100, Math.round((summary.subtotal / summary.freeDeliveryThreshold) * 100));
    if (this.thresholdFill) {
      this.thresholdFill.style.width = `${progressPct}%`;
    }

    if (this.thresholdLabel) {
      if (summary.isFreeDelivery) {
        this.thresholdLabel.innerHTML = `✨ <strong>Free Faura Delivery Unlocked!</strong>`;
      } else {
        this.thresholdLabel.innerHTML = `Add <span class="highlight-amount">${formatINR(summary.amountNeededForFreeDelivery)}</span> more for <strong>FREE Delivery</strong>`;
      }
    }
  }

  renderDrawer() {
    const cart = store.state.cart;
    const summary = store.state.cartSummary;

    if (!this.drawerItemsList) return;

    if (cart.length === 0) {
      this.drawerItemsList.innerHTML = `
        <div style="text-align: center; padding: 3rem 1rem; color: var(--bistro-gray-text);">
          <div style="font-size: 3rem; margin-bottom: 0.8rem;">🍲</div>
          <h4 style="color: var(--bistro-dark); margin-bottom: 0.4rem;">Your Faura Cart is Empty</h4>
          <p style="font-size: 0.8rem;">Explore our regional Indian and Continental menus to begin.</p>
        </div>
      `;
      if (this.placeOrderBtn) this.placeOrderBtn.disabled = true;
    } else {
      if (this.placeOrderBtn) this.placeOrderBtn.disabled = false;
      this.drawerItemsList.innerHTML = cart.map(item => `
        <div class="cart-item-row">
          <img src="${item.image_url}" alt="${item.name}" class="cart-item-img">
          <div class="cart-item-details">
            <div>
              <div class="cart-item-title">${item.name}</div>
              ${item.selectionsSummary && item.selectionsSummary.length > 0 ? `
                <div class="cart-item-selections">
                  ${item.selectionsSummary.join(' • ')}
                </div>
              ` : ''}
            </div>
            <div class="cart-item-controls">
              <div class="qty-counter">
                <button class="qty-btn btn-qty-dec anim-bounce-click" data-key="${item.cartKey}">−</button>
                <span class="qty-number">${item.quantity}</span>
                <button class="qty-btn btn-qty-inc anim-bounce-click" data-key="${item.cartKey}">+</button>
              </div>
              <div class="cart-item-price">${formatINR(item.unit_price * item.quantity)}</div>
            </div>
          </div>
        </div>
      `).join('');

      this.drawerItemsList.querySelectorAll('.btn-qty-dec').forEach(b => {
        b.addEventListener('click', () => this.updateQuantity(b.dataset.key, -1));
      });
      this.drawerItemsList.querySelectorAll('.btn-qty-inc').forEach(b => {
        b.addEventListener('click', () => this.updateQuantity(b.dataset.key, 1));
      });
    }

    // Update totals and SLA
    if (this.drawerSubtotal) this.drawerSubtotal.textContent = formatINR(summary.subtotal);
    if (this.drawerDeliveryFee) {
      this.drawerDeliveryFee.innerHTML = summary.isFreeDelivery ?
        '<span class="free-badge">FREE DELIVERY</span>' :
        formatINR(summary.deliveryFee);
    }
    document.getElementById('drawerCodFee').textContent = formatINR(summary.codFee || 0);
    document.getElementById('drawerExpressFee').textContent = formatINR(summary.expressFee || 0);
    if (this.codFeeRow) this.codFeeRow.hidden = !summary.codFee;
    if (this.expressFeeRow) this.expressFeeRow.hidden = !summary.expressFee;
    document.getElementById('drawerTokenDiscount').textContent = `−${formatINR(summary.tokenDiscount || 0)}`;
    if (this.tokenDiscountRow) this.tokenDiscountRow.hidden = !summary.tokenDiscount;
    if (this.drawerCouponRow && this.drawerCouponDiscount) {
      if (summary.couponDiscount > 0) {
        this.drawerCouponRow.hidden = false;
        this.drawerCouponDiscount.textContent = `−${formatINR(summary.couponDiscount)}`;
      } else {
        this.drawerCouponRow.hidden = true;
      }
    }
    if (this.drawerTotal) this.drawerTotal.textContent = formatINR(summary.total);
    if (this.drawerEta) this.drawerEta.textContent = `${summary.etaMinutes} mins`;
    if (this.drawerCodCancellationBanner) {
      this.drawerCodCancellationBanner.style.display = store.state.paymentMethod === 'cod' ? 'flex' : 'none';
    }
  }

  triggerCapsuleBounce() {
    if (!this.capsule) return;
    this.capsule.classList.remove('cart-bounce');
    void this.capsule.offsetWidth; // force reflow
    this.capsule.classList.add('cart-bounce');
  }

  showToast(message, type = 'lime') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span>${type === 'lime' ? '⚡' : '⚠️'}</span>
      <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  async placeOrder() {
    if (store.state.cart.length === 0) return;

    const payload = {
      customer_name: store.state.profile.user?.display_name || 'Guest',
      delivery_address: store.state.profile.user?.addresses?.find((address) => address.is_default)?.address || 'Address to be confirmed',
      items: store.state.cart.map(i => ({
        dish_id: i.dishId,
        quantity: i.quantity,
        selections: i.selections || []
      })),
      active_allergens: [...store.state.activeAllergens],
      payment_method: store.state.paymentMethod,
      delivery_mode: store.state.deliveryMode,
      coupon_code: couponManager.getActiveCoupon()?.code || null,
    };

    try {
      this.placeOrderBtn.disabled = true;
      this.placeOrderBtn.textContent = "Transmitting to Faura Kitchen...";

      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(store.state.profile.accessToken ? { Authorization: `Bearer ${store.state.profile.accessToken}` } : {}),
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Order creation failed');
      const orderData = await res.json();

      // Clear cart & promo code
      store.state.cart = [];
      store.saveCart();
      couponManager.removeCoupon();
      if (this.promoInput) this.promoInput.value = '';
      if (this.promoStatusMsg) this.promoStatusMsg.style.display = 'none';
      this.recalculateLocally();
      this.closeDrawer();

      window.orderTrackerWidget.showReceipt(orderData);
    } catch (err) {
      console.error(err);
      this.showToast('Order failed to transmit. Please retry.', 'coral');
    } finally {
      if (this.placeOrderBtn) {
        this.placeOrderBtn.disabled = false;
        this.placeOrderBtn.textContent = "Confirm Faura Order ✨";
      }
    }
  }
}

function roundPrice(val) {
  return Math.round(val * 100) / 100;
}

export const optimisticCart = new OptimisticCartEngine();
