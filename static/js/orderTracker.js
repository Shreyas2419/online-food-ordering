/**
 * WebSocket Real-Time Order Tracker Widget
 * Manages live WebSocket lifecycle, stage stepper, and telemetry streams.
 */
import { MicroMapCanvas } from './microMap.js';

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

export class OrderTrackerWidget {
  constructor() {
    this.modalBackdrop = document.getElementById('trackerModalBackdrop');
    this.modalClose = document.getElementById('trackerModalClose');
    this.orderIdLabel = document.getElementById('trackerOrderIdLabel');
    this.stageDesc = document.getElementById('trackerStageDesc');
    this.etaClock = document.getElementById('trackerEtaClock');
    this.progressFill = document.getElementById('trackerProgressFill');

    // Telemetry HUD
    this.hudSpeed = document.getElementById('hudSpeed');
    this.hudAltitude = document.getElementById('hudAltitude');
    this.hudBattery = document.getElementById('hudBattery');
    this.hudDistance = document.getElementById('hudDistance');

    this.stepperNodes = document.querySelectorAll('.step-node');
    this.microMap = new MicroMapCanvas('microMapCanvas');
    this.ws = null;
    this.orderId = null;
    this.supportBtn = document.getElementById('trackerSupportBtn');
    this.supportForm = document.getElementById('trackerSupportForm');
    this.driverInfo = document.getElementById('trackerDriverInfo');
    this.receiptBackdrop = document.getElementById('orderReceiptBackdrop');
    this.receiptItems = document.getElementById('receiptItems');
    this.receiptOrder = null;
    this.pollTimer = null;
    this.polling = false;

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

    const resetBtn = document.getElementById('trackerResetBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.close();
        this.stopPolling();
        if (this.ws) this.ws.close();
      });
    }
    this.supportBtn?.addEventListener('click', () => {
      this.supportForm.hidden = !this.supportForm.hidden;
      if (!this.supportForm.hidden) this.supportForm.querySelector('textarea')?.focus();
    });
    this.supportForm?.addEventListener('submit', (event) => this.createSupportTicket(event));
    document.getElementById('receiptCloseBtn')?.addEventListener('click', () => this.closeReceipt());
    this.receiptBackdrop?.addEventListener('click', (event) => {
      if (event.target === this.receiptBackdrop) this.closeReceipt();
    });
    document.getElementById('receiptTrackBtn')?.addEventListener('click', () => {
      const order = this.receiptOrder;
      this.closeReceipt();
      if (order) this.open(order.order_id, order.status, order.payment_status);
    });
  }

  open(orderId, status = 'received') {
    this.orderId = orderId;
    if (this.orderIdLabel) {
      this.orderIdLabel.textContent = `Order #${orderId}`;
    }
    this.modalBackdrop.classList.add('open');
    if (this.supportBtn) this.supportBtn.hidden = !['received', 'booked', 'preparing', 'active', 'out_for_delivery'].includes(status);
    if (this.supportForm) this.supportForm.hidden = true;

    // Initialize canvas sizing after opening modal
    setTimeout(() => {
      if (this.microMap) this.microMap.resize();
    }, 150);

    this.startPolling(orderId);
  }

  showReceipt(order) {
    this.receiptOrder = order;
    document.getElementById('receiptOrderId').textContent = `Order ${order.order_id}`;
    this.receiptItems.innerHTML = order.items.map((item) => `
      <div class="receipt-item"><span>${escapeHtml(item.name)} × ${Number(item.quantity)}</span><span>₹${Number(item.total_price).toFixed(2)}</span></div>`).join('');
    document.getElementById('receiptSubtotal').textContent = `₹${Number(order.subtotal).toFixed(2)}`;
    document.getElementById('receiptDelivery').textContent = `₹${Number(order.delivery_fee).toFixed(2)}`;
    document.getElementById('receiptCod').textContent = `₹${Number(order.cod_fee || 0).toFixed(2)}`;
    document.getElementById('receiptExpress').textContent = `₹${Number(order.express_fee || 0).toFixed(2)}`;
    document.getElementById('receiptDiscount').textContent = `−₹${Number(order.token_discount || 0).toFixed(2)}`;
    document.getElementById('receiptPayment').textContent = `${order.payment_method.toUpperCase()} · ${order.payment_status}`;
    document.getElementById('receiptTotal').textContent = `₹${Number(order.total_amount).toFixed(2)}`;
    document.getElementById('receiptEta').textContent = `${Number(order.eta_minutes)} minutes`;
    const codNotice = document.getElementById('receiptCodNotice');
    if (codNotice) {
      codNotice.style.display = (order.payment_method?.toLowerCase() === 'cod') ? 'flex' : 'none';
    }
    this.receiptBackdrop.classList.add('open');
  }

  closeReceipt() {
    this.receiptBackdrop?.classList.remove('open');
  }

  async createSupportTicket(event) {
    event.preventDefault();
    const submitButton = this.supportForm.querySelector('button[type="submit"]');
    const status = document.getElementById('supportTicketStatus');
    const message = new FormData(this.supportForm).get('message');
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('zg_access_token');
    if (token) headers.Authorization = `Bearer ${token}`;
    submitButton.disabled = true;
    try {
      const response = await fetch(`/api/v1/orders/${encodeURIComponent(this.orderId)}/support`, {
        method: 'POST', headers, body: JSON.stringify({ message }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not create support ticket');
      status.textContent = `Ticket ${data.ticket_id} created for order ${data.order_id}.`;
      this.supportForm.reset();
    } catch (error) {
      status.textContent = error.message;
    } finally {
      submitButton.disabled = false;
    }
  }

  close() {
    if (this.modalBackdrop) {
      this.modalBackdrop.classList.remove('open');
    }
    this.stopPolling();
  }

  startPolling(orderId) {
    this.stopPolling();
    this.pollTracking(orderId);
    this.pollTimer = setInterval(() => this.pollTracking(orderId), 3000);
  }

  stopPolling() {
    if (this.pollTimer) clearInterval(this.pollTimer);
    this.pollTimer = null;
  }

  async pollTracking(orderId) {
    if (this.polling || this.orderId !== orderId) return;
    this.polling = true;
    try {
      const headers = {};
      const token = localStorage.getItem('zg_access_token');
      if (token) headers.Authorization = `Bearer ${token}`;
      const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}/track`, { headers });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Tracking update unavailable');
      this.handleTracking(data);
      if (data.status === 'delivered') this.stopPolling();
    } catch (error) {
      if (this.stageDesc) this.stageDesc.textContent = error.message;
    } finally {
      this.polling = false;
    }
  }

  handleTracking(data) {
    const stageByStatus = { placed: 0, payment_pending: 0, preparing: 1, out_for_delivery: 2, delivered: 3 };
    const stageIndex = stageByStatus[data.status] ?? 0;
    const driver = data.driver || {};
    this.handleTelemetry({
      stage_index: stageIndex,
      stage_description: data.status === 'payment_pending'
        ? 'Payment confirmation is pending. Delivery preparation will begin once it clears.'
        : `Order ${data.status.replaceAll('_', ' ')}. ${driver.name ? `${driver.name} is assigned to your delivery.` : ''}`,
      progress_percent: data.progress_percent,
      eta_minutes: data.eta_minutes,
      distance_km: data.distance_km,
      courier: { flight_ratio: data.progress_percent / 100 },
    });
    if (this.driverInfo) {
      this.driverInfo.textContent = driver.name
        ? `Driver ${driver.name} · ${driver.phone} · ${driver.vehicle} · ★${Number(driver.rating).toFixed(1)} · GPS ${data.location.latitude}, ${data.location.longitude}`
        : 'Driver assignment pending.';
    }
    if (this.supportBtn) this.supportBtn.hidden = data.status === 'delivered';
  }

  connectWebSocket(orderId) {
    if (this.ws) {
      try { this.ws.close(); } catch {}
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/order-tracking/${orderId}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'TELEMETRY_UPDATE') {
          this.handleTelemetry(data);
        }
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket encountered error, falling back to simulated stream:', err);
      };

      this.ws.onclose = () => {
        console.log('Order tracking WebSocket connection closed');
      };
    } catch (err) {
      console.error('Failed to open WS socket:', err);
    }
  }

  handleTelemetry(data) {
    // 1. Update stepper
    const stageIdx = data.stage_index;
    const progress = Math.max(0, Math.min(100, Number(data.progress_percent) || 0));
    this.stepperNodes.forEach((node, i) => {
      node.classList.remove('active', 'completed');
      if (i < stageIdx) {
        node.classList.add('completed');
      } else if (i === stageIdx) {
        node.classList.add('active');
      }
    });

    // 2. Update Progress fill
    if (this.progressFill) {
      this.progressFill.style.width = `${progress}%`;
      this.progressFill.parentElement?.setAttribute('aria-valuenow', String(progress));
    }

    // 3. Update descriptions & ETA
    if (this.stageDesc) {
      this.stageDesc.textContent = data.stage_description;
    }
    if (this.etaClock) {
      this.etaClock.textContent = data.eta_minutes > 0 ? `${data.eta_minutes}m` : '0m (ARRIVED)';
    }

    // 4. Update HUD
    const courier = data.courier || {};
    if (this.hudSpeed && courier.speed_kmh !== undefined) {
      this.hudSpeed.textContent = `${courier.speed_kmh} km/h`;
    }
    if (this.hudAltitude && courier.altitude_m !== undefined) {
      this.hudAltitude.textContent = `${courier.altitude_m}m`;
    }
    if (this.hudBattery && courier.battery_pct !== undefined) {
      this.hudBattery.textContent = `${courier.battery_pct}%`;
    }
    if (this.hudDistance) {
      this.hudDistance.textContent = `${data.distance_km} km`;
    }

    // 5. Update Micro Map Drone
    if (this.microMap) {
      if (courier.flight_ratio !== undefined) {
        this.microMap.setFlightProgress(courier.flight_ratio);
      } else if (stageIdx === 0) {
        this.microMap.setFlightProgress(0.04);
      } else if (stageIdx === 1) {
        this.microMap.setFlightProgress(0.12);
      } else if (stageIdx >= 3) {
        this.microMap.setFlightProgress(1.0);
      }
    }
  }
}
