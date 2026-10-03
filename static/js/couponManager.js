/**
 * Feature 2: Discount Coupon Integration Module
 * Provides client-side validation logic, real-time UI feedback, and checkout state sync.
 */
import { formatINR } from './currency.js';
import { store } from './state.js';

export class CouponManager {
  constructor() {
    this.activeCoupon = null;
    this.validationCache = new Map();
    this.isApplying = false;
  }

  /**
   * Client-side quick pre-validation utility.
   * Checks existence of input, basic format, and subtotal threshold.
   */
  validateCouponInput(rawCode, subtotal) {
    const code = String(rawCode || '').trim().toUpperCase();
    if (!code) {
      return { isValid: false, message: 'Please enter a coupon code.' };
    }
    if (code.length < 3 || code.length > 20) {
      return { isValid: false, message: 'Coupon code must be between 3 and 20 characters.' };
    }
    if (subtotal <= 0) {
      return { isValid: false, message: 'Add items to your cart before applying a coupon.' };
    }
    return { isValid: true, code };
  }

  /**
   * Asynchronous server-authoritative coupon validation.
   */
  async applyCoupon(rawCode, subtotal) {
    const preCheck = this.validateCouponInput(rawCode, subtotal);
    if (!preCheck.isValid) {
      return { success: false, message: preCheck.message };
    }

    this.isApplying = true;
    try {
      const response = await fetch('/api/v1/coupons/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: preCheck.code, subtotal }),
      });

      if (!response.ok) {
        throw new Error('Unable to validate coupon at this time. Please try again.');
      }

      const data = await response.json();
      if (data.is_valid) {
        this.activeCoupon = {
          code: data.code,
          discountAmount: data.discount_amount,
          discountType: data.discount_type,
          discountValue: data.discount_value,
          message: data.message,
          minOrderValue: data.min_order_value,
        };
        store.state.activeCoupon = this.activeCoupon;
        store.notify('COUPON_APPLIED');
        return { success: true, coupon: this.activeCoupon, message: data.message };
      } else {
        this.activeCoupon = null;
        store.state.activeCoupon = null;
        store.notify('COUPON_REMOVED');
        return { success: false, message: data.message || 'Invalid coupon code.' };
      }
    } catch (err) {
      return { success: false, message: err.message || 'Network error verifying promo code.' };
    } finally {
      this.isApplying = false;
    }
  }

  /**
   * Remove active coupon.
   */
  removeCoupon() {
    this.activeCoupon = null;
    store.state.activeCoupon = null;
    store.notify('COUPON_REMOVED');
  }

  /**
   * Get active coupon details.
   */
  getActiveCoupon() {
    return this.activeCoupon;
  }
}

export const couponManager = new CouponManager();
