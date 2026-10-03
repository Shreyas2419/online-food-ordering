/**
 * Feature 1: Premium Table Reservation System Module
 * Interactive visual table booking widget, conflict resolution, VIP deposit checkout,
 * and confirmation lifecycle management.
 */
import { formatINR } from './currency.js';
import { store } from './state.js';

export class TableReservationWidget {
  constructor() {
    this.modalBackdrop = document.getElementById('reservationModalBackdrop');
    this.openButtons = document.querySelectorAll('[data-open-reservation]');
    this.closeBtn = document.getElementById('reservationModalClose');
    
    // Controls
    this.dateInput = document.getElementById('resDateInput');
    this.timeSlotsContainer = document.getElementById('resTimeSlots');
    this.partySizeSelector = document.getElementById('resPartySizeSelector');
    this.tablesGrid = document.getElementById('resTablesGrid');
    this.depositStepContainer = document.getElementById('resDepositStep');
    this.submitBtn = document.getElementById('resSubmitBtn');
    this.statusMessage = document.getElementById('resStatusMessage');
    this.confirmationModal = document.getElementById('resConfirmationModal');

    // State
    this.selectedDate = this.getDefaultDate();
    this.selectedTime = '19:30';
    this.selectedPartySize = 2;
    this.selectedTable = null;
    this.tables = [];
    this.selectedPaymentMethod = 'upi';
    this.isSubmitting = false;

    this.TIME_SLOTS = [
      '12:30', '13:00', '13:30', '14:00',
      '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'
    ];

    this.init();
  }

  getDefaultDate() {
    const today = new Date();
    today.setDate(today.getDate() + 1); // default to tomorrow for dining reservations
    return today.toISOString().split('T')[0];
  }

  init() {
    if (!this.modalBackdrop) return;

    // Attach open triggers (e.g. from nav header)
    this.openButtons.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.open();
      });
    });

    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }

    if (this.modalBackdrop) {
      this.modalBackdrop.addEventListener('click', (e) => {
        if (e.target === this.modalBackdrop) this.close();
      });
    }

    if (this.dateInput) {
      this.dateInput.value = this.selectedDate;
      this.dateInput.min = new Date().toISOString().split('T')[0];
      this.dateInput.addEventListener('change', (e) => {
        this.selectedDate = e.target.value;
        this.fetchTablesAndAvailability();
      });
    }

    this.renderTimeSlots();
    this.renderPartySizeSelector();
    this.bindSubmit();
  }

  open() {
    if (this.modalBackdrop) {
      this.modalBackdrop.classList.add('open');
      this.modalBackdrop.setAttribute('aria-hidden', 'false');
      this.fetchTablesAndAvailability();
    }
  }

  close() {
    if (this.modalBackdrop) {
      this.modalBackdrop.classList.remove('open');
      this.modalBackdrop.setAttribute('aria-hidden', 'true');
    }
  }

  renderTimeSlots() {
    if (!this.timeSlotsContainer) return;
    this.timeSlotsContainer.innerHTML = this.TIME_SLOTS.map((time) => `
      <button type="button" class="res-time-pill ${time === this.selectedTime ? 'active' : ''}" data-time="${time}">
        ${time}
      </button>
    `).join('');

    this.timeSlotsContainer.querySelectorAll('.res-time-pill').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.selectedTime = btn.dataset.time;
        this.renderTimeSlots();
        this.fetchTablesAndAvailability();
      });
    });
  }

  renderPartySizeSelector() {
    if (!this.partySizeSelector) return;
    const sizes = [1, 2, 3, 4, 5, 6, 8];
    this.partySizeSelector.innerHTML = sizes.map((size) => `
      <button type="button" class="res-party-pill ${size === this.selectedPartySize ? 'active' : ''}" data-size="${size}">
        ${size} ${size === 1 ? 'Guest' : 'Guests'}
      </button>
    `).join('');

    this.partySizeSelector.querySelectorAll('.res-party-pill').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.selectedPartySize = parseInt(btn.dataset.size, 10);
        this.renderPartySizeSelector();
        this.fetchTablesAndAvailability();
      });
    });
  }

  async fetchTablesAndAvailability() {
    if (!this.tablesGrid) return;
    this.tablesGrid.innerHTML = `
      <div class="res-loading-state">
        <div class="spinner-ring"></div>
        <p>Scanning VIP tables &amp; verifying floor plan availability...</p>
      </div>
    `;

    try {
      const url = `/api/v1/reservations/availability?date=${this.selectedDate}&time_slot=${encodeURIComponent(this.selectedTime)}&party_size=${this.selectedPartySize}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Could not fetch real-time table availability.');

      const data = await response.json();
      this.tables = data.tables || [];
      this.renderTablesList();
    } catch (err) {
      this.tablesGrid.innerHTML = `<p class="res-error-notice">${err.message}</p>`;
    }
  }

  renderTablesList() {
    if (!this.tablesGrid) return;

    if (this.tables.length === 0) {
      this.tablesGrid.innerHTML = `<p class="res-empty-notice">No tables available matching your party size.</p>`;
      return;
    }

    // Sort VIP tables first
    const sorted = [...this.tables].sort((a, b) => (b.is_premium ? 1 : 0) - (a.is_premium ? 1 : 0));

    this.tablesGrid.innerHTML = sorted.map((tbl) => {
      const isSelected = this.selectedTable && this.selectedTable.id === tbl.id;
      const isUnavailable = !tbl.is_available;

      return `
        <div class="res-table-card ${tbl.is_premium ? 'is-vip' : 'is-standard'} ${isSelected ? 'selected' : ''} ${isUnavailable ? 'disabled' : ''}" data-table-id="${tbl.id}">
          <div class="res-card-top">
            <span class="res-type-badge ${tbl.is_premium ? 'badge-gold' : 'badge-neutral'}">
              ${tbl.is_premium ? '★ VIP / PREMIUM' : 'STANDARD BISTRO'}
            </span>
            <span class="res-capacity-badge">Seats up to ${tbl.capacity}</span>
          </div>

          <h4 class="res-table-name">${tbl.name}</h4>
          <p class="res-table-loc">📍 ${tbl.location_tag}</p>
          <p class="res-table-desc">${tbl.description}</p>

          <div class="res-perks-list">
            ${(tbl.features || []).map((f) => `<span class="res-perk-item">✓ ${f}</span>`).join('')}
          </div>

          <div class="res-card-footer">
            <div class="res-fee-block">
              <span class="res-fee-label">Deposit Fee:</span>
              <strong class="res-fee-val ${tbl.reservation_fee > 0 ? 'highlight-gold' : 'highlight-free'}">
                ${tbl.reservation_fee > 0 ? formatINR(tbl.reservation_fee) : 'Free Reservation'}
              </strong>
            </div>

            <button type="button" class="btn-res-select ${isSelected ? 'selected' : ''}" ${isUnavailable ? 'disabled' : ''}>
              ${isUnavailable ? 'Reserved' : (isSelected ? 'Selected ✓' : 'Select Table')}
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Bind card selection
    this.tablesGrid.querySelectorAll('.res-table-card:not(.disabled)').forEach((card) => {
      card.addEventListener('click', () => {
        const tableId = card.dataset.tableId;
        this.selectedTable = this.tables.find((t) => t.id === tableId);
        this.renderTablesList();
        this.renderDepositStep();
        this.updateSubmitState();
      });
    });
  }

  renderDepositStep() {
    if (!this.depositStepContainer) return;

    if (!this.selectedTable) {
      this.depositStepContainer.innerHTML = '';
      this.depositStepContainer.style.display = 'none';
      return;
    }

    if (this.selectedTable.is_premium && this.selectedTable.reservation_fee > 0) {
      this.depositStepContainer.style.display = 'block';
      this.depositStepContainer.innerHTML = `
        <div class="res-deposit-card">
          <div class="res-deposit-header">
            <div class="vip-crown">👑</div>
            <div>
              <h5>VIP Reservation Deposit</h5>
              <p>This table requires a <strong>${formatINR(this.selectedTable.reservation_fee)}</strong> reservation deposit to guarantee your private seating and chef prep. Full amount adjusted in your dining bill.</p>
            </div>
          </div>
          <div class="res-payment-options">
            <label class="res-pay-choice">
              <input type="radio" name="resPaymentMethod" value="upi" checked>
              <span>Instant UPI (GPay / PhonePe / Paytm)</span>
            </label>
            <label class="res-pay-choice">
              <input type="radio" name="resPaymentMethod" value="card">
              <span>Credit / Debit Card (Visa, Mastercard, Amex)</span>
            </label>
            <label class="res-pay-choice">
              <input type="radio" name="resPaymentMethod" value="tokens">
              <span>Wallet Tokens</span>
            </label>
          </div>
        </div>
      `;

      this.depositStepContainer.querySelectorAll('input[name="resPaymentMethod"]').forEach((input) => {
        input.addEventListener('change', () => {
          this.selectedPaymentMethod = input.value;
        });
      });
    } else {
      this.depositStepContainer.style.display = 'block';
      this.depositStepContainer.innerHTML = `
        <div class="res-standard-notice">
          <span>✨ Standard bistro table reservation: <strong>₹0.00 deposit</strong>. Table held for 15 minutes past arrival.</span>
        </div>
      `;
    }
  }

  updateSubmitState() {
    if (!this.submitBtn) return;
    if (!this.selectedTable) {
      this.submitBtn.disabled = true;
      this.submitBtn.textContent = 'Select a Table to Continue';
    } else if (this.selectedTable.is_premium && this.selectedTable.reservation_fee > 0) {
      this.submitBtn.disabled = false;
      this.submitBtn.textContent = `Confirm VIP Table & Pay Deposit (${formatINR(this.selectedTable.reservation_fee)}) ➔`;
    } else {
      this.submitBtn.disabled = false;
      this.submitBtn.textContent = `Confirm Free Reservation ➔`;
    }
  }

  bindSubmit() {
    const form = document.getElementById('tableReservationForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!this.selectedTable || this.isSubmitting) return;

      const nameInput = document.getElementById('resCustomerName');
      const emailInput = document.getElementById('resCustomerEmail');
      const phoneInput = document.getElementById('resCustomerPhone');
      const notesInput = document.getElementById('resSpecialRequests');

      const payload = {
        table_id: this.selectedTable.id,
        customer_name: nameInput?.value?.trim() || 'Valued Guest',
        customer_email: emailInput?.value?.trim() || 'guest@example.com',
        customer_phone: phoneInput?.value?.trim() || '+91 98765 43210',
        reservation_date: this.selectedDate,
        time_slot: this.selectedTime,
        party_size: this.selectedPartySize,
        special_requests: notesInput?.value?.trim() || '',
        payment_method: this.selectedTable.is_premium ? this.selectedPaymentMethod : 'at_venue',
      };

      this.isSubmitting = true;
      if (this.submitBtn) {
        this.submitBtn.disabled = true;
        this.submitBtn.textContent = 'Securing Table & Validating Availability...';
      }

      try {
        const response = await fetch('/api/v1/reservations/book', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(store.state.profile.accessToken ? { Authorization: `Bearer ${store.state.profile.accessToken}` } : {}),
          },
          body: JSON.stringify(payload),
        });

        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.detail || 'Could not complete reservation.');
        }

        // Show Confirmation Receipt
        this.showConfirmation(result);
        this.close();
      } catch (err) {
        if (this.statusMessage) {
          this.statusMessage.className = 'res-status-msg error';
          this.statusMessage.textContent = `⚠️ ${err.message}`;
          this.statusMessage.style.display = 'block';
        }
      } finally {
        this.isSubmitting = false;
        this.updateSubmitState();
      }
    });
  }

  showConfirmation(data) {
    const confirmationBackdrop = document.getElementById('reservationReceiptBackdrop');
    if (!confirmationBackdrop) {
      alert(`🎉 Reservation Confirmed!\nConfirmation: ${data.confirmation_code}\nTable: ${data.table_name}\nDate: ${data.reservation_date} at ${data.time_slot}`);
      return;
    }

    document.getElementById('resReceiptCode').textContent = data.confirmation_code;
    document.getElementById('resReceiptTable').textContent = data.table_name;
    document.getElementById('resReceiptDate').textContent = `${data.reservation_date} at ${data.time_slot}`;
    document.getElementById('resReceiptParty').textContent = `${data.party_size} Guests`;
    document.getElementById('resReceiptDeposit').textContent = data.deposit_amount > 0 ? formatINR(data.deposit_amount) : 'Free Reservation';
    document.getElementById('resReceiptNotes').textContent = data.notes;

    confirmationBackdrop.classList.add('open');
    const closeBtn = document.getElementById('resReceiptClose');
    if (closeBtn) {
      closeBtn.onclick = () => confirmationBackdrop.classList.remove('open');
    }
  }
}

export const tableReservationWidget = new TableReservationWidget();
