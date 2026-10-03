/**
 * Anti-Gravity State Management Store
 * Reactive state container with subscription pattern & local persistence.
 */

class AppStore {
  constructor() {
    this.state = {
      menuItems: [],
      filteredItems: [],
      activeAllergens: new Set(this.loadInitialAllergens()),
      selectedCategory: 'all',
      selectedDietaryType: 'all',
      searchQuery: '',
      cart: this.loadInitialCart(),
      cartSummary: {
        itemCount: 0,
        subtotal: 0.0,
        deliveryFee: 0.0,
        freeDeliveryThreshold: 25.00,
        amountNeededForFreeDelivery: 25.00,
        isFreeDelivery: false,
        total: 0.0,
        codFee: 0.0,
        expressFee: 0.0,
        tokenDiscount: 0.0,
        paymentMethod: 'upi',
        deliveryMode: 'standard',
        etaMinutes: 24,
        prepTimeMins: 12,
        activeKitchenQueue: 3,
        transitTimeMins: 8
      },
      distanceKm: 3.5,
      paymentMethod: 'upi',
      deliveryMode: 'standard',
      profile: this.loadProfile(),
      restaurants: [],
      activeOrder: null,
      isSimulatingFailure: false, // For testing rollback on failure
      isCustomizerOpen: false,
      activeCustomizerDish: null,
      isCartDrawerOpen: false,
      isTrackerOpen: false,
      isSwapModalOpen: false,
      activeSwapDish: null,
    };

    this.listeners = new Set();
  }

  loadInitialAllergens() {
    try {
      const saved = localStorage.getItem('zg_allergens');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  }

  loadInitialCart() {
    try {
      const saved = localStorage.getItem('zg_cart');
      if (!saved) return [];
      const parsed = JSON.parse(saved);
      if (!Array.isArray(parsed)) return Array.isArray(parsed.items) ? parsed.items : [];
      return parsed.map((item) => ({
        ...item,
        base_price: Number(item.base_price) * 83,
        unit_price: Number(item.unit_price) * 83,
        selections: (item.selections || []).map((selection) => ({
          ...selection,
          price: Number(selection.price || 0) * 83,
        })),
        currency: 'INR',
      }));
    } catch {
      return [];
    }
  }

  loadProfile() {
    try {
      return {
        accessToken: localStorage.getItem('zg_access_token'),
        user: JSON.parse(localStorage.getItem('zg_profile') || 'null'),
      };
    } catch {
      return { accessToken: null, user: null };
    }
  }

  setProfile(accessToken, user) {
    this.state.profile = { accessToken, user };
    try {
      if (accessToken) localStorage.setItem('zg_access_token', accessToken);
      else localStorage.removeItem('zg_access_token');
      if (user) localStorage.setItem('zg_profile', JSON.stringify(user));
      else localStorage.removeItem('zg_profile');
    } catch {}
    this.notify('PROFILE_UPDATED');
  }

  updateProfile(user) {
    this.state.profile.user = user;
    try {
      localStorage.setItem('zg_profile', JSON.stringify(user));
    } catch {}
    this.notify('PROFILE_UPDATED');
  }

  setDietaryType(type) {
    this.state.selectedDietaryType = type;
    this.recomputeFilteredItems();
    this.notify('DIETARY_FILTER_CHANGED', type);
  }

  setRestaurant(restaurantId) {
    this.state.selectedRestaurantId = restaurantId;
    this.recomputeFilteredItems();
    this.notify('RESTAURANT_FILTER_CHANGED', restaurantId);
  }

  setPaymentMethod(method) {
    this.state.paymentMethod = method;
    this.notify('CHECKOUT_OPTIONS_CHANGED');
  }

  setDeliveryMode(mode) {
    this.state.deliveryMode = mode;
    this.notify('CHECKOUT_OPTIONS_CHANGED');
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify(event, payload) {
    this.listeners.forEach((cb) => cb(this.state, event, payload));
  }

  setMenuItems(items) {
    this.state.menuItems = items;
    this.recomputeFilteredItems();
    this.notify('MENU_UPDATED');
  }

  toggleAllergen(allergen) {
    const key = allergen.toLowerCase();
    if (this.state.activeAllergens.has(key)) {
      this.state.activeAllergens.delete(key);
    } else {
      this.state.activeAllergens.add(key);
    }
    try {
      localStorage.setItem('zg_allergens', JSON.stringify([...this.state.activeAllergens]));
    } catch {}
    this.recomputeFilteredItems();
    this.notify('ALLERGENS_CHANGED', key);
  }

  clearAllergens() {
    this.state.activeAllergens.clear();
    try {
      localStorage.removeItem('zg_allergens');
    } catch {}
    this.recomputeFilteredItems();
    this.notify('ALLERGENS_CHANGED');
  }

  setCategory(category) {
    this.state.selectedCategory = category;
    this.recomputeFilteredItems();
    this.notify('CATEGORY_CHANGED', category);
  }

  setSearchQuery(query) {
    this.state.searchQuery = query.toLowerCase().trim();
    this.recomputeFilteredItems();
    this.notify('SEARCH_CHANGED', this.state.searchQuery);
  }

  setDistance(dist) {
    this.state.distanceKm = parseFloat(dist);
    this.notify('DISTANCE_CHANGED', this.state.distanceKm);
  }

  recomputeFilteredItems() {
    const { menuItems, selectedCategory, selectedDietaryType, selectedRestaurantId, searchQuery, activeAllergens } = this.state;
    const activeAllergenList = [...activeAllergens];

    this.state.filteredItems = menuItems.filter((dish) => {
      // Category check
      if (selectedCategory !== 'all' && dish.category.toLowerCase() !== selectedCategory.toLowerCase()) {
        return false;
      }
      if (selectedDietaryType !== 'all' && dish.dietary_type !== selectedDietaryType) return false;
      if (selectedRestaurantId && dish.restaurant_id !== selectedRestaurantId) return false;
      // Query check
      if (searchQuery) {
        const matchName = dish.name.toLowerCase().includes(searchQuery);
        const matchDesc = dish.description.toLowerCase().includes(searchQuery);
        const matchIngr = dish.ingredients && dish.ingredients.some((i) => i.toLowerCase().includes(searchQuery));
        if (!matchName && !matchDesc && !matchIngr) return false;
      }
      return true;
    }).map((dish) => {
      // Allergen evaluation
      const detected = dish.allergens ? dish.allergens.filter((a) => activeAllergenList.includes(a.toLowerCase())) : [];
      const isSafe = detected.length === 0;
      const riskLevel = isSafe ? 'safe' : (detected.length >= 2 || detected.includes('peanuts') || detected.includes('shellfish') ? 'high_risk' : 'warning');
      
      return {
        ...dish,
        safe: isSafe,
        detectedAllergens: detected,
        riskLevel
      };
    });
  }

  saveCart() {
    try {
      localStorage.setItem('zg_cart', JSON.stringify({ currency: 'INR', items: this.state.cart }));
    } catch {}
  }
}

export const store = new AppStore();
