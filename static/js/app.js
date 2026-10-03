/**
 * Main Application Coordinator - Sushi Bistro & Poke Bowls
 * Coordinates the 3-column interactive slider, Allergen Shield,
 * Optimistic Cart, and Real-time WebSocket Drone Telemetry.
 */
import { store } from './state.js';
import { AllergenShieldEngine } from './allergenShield.js';
import { DishBuilder } from './dishBuilder.js';
import { optimisticCart } from './optimisticCart.js';
import { OrderTrackerWidget } from './orderTracker.js';
import { AccountMenuFeatures } from './accountMenu.js';
import { SpecialtyMenus } from './specialtyMenus.js';
import { tableReservationWidget } from './tableReservation.js';
import { BournetSectionComponent } from './bournetMenu.js';
import { ContinentalMenuComponent } from './continentalMenu.js';
import { AmbientAuraController } from './ambientAura.js';
import { formatINR } from './currency.js';

export const FEATURED_SLIDES = [
  {
    id: "featured-salmon-poke",
    badge: "Malabar Catch",
    heading: "Malabar Spiced Salmon Platter",
    breadcrumb: "FAURA > COASTAL SPECIALS",
    description: "Pan-roasted Atlantic salmon steeped in Malabar spices, fragrant basmati rice, Hass avocado, and fresh tempered coconut chutney.",
    basePrice: 18.50 * 83,
    image: "/static/assets/poke_bowl_transparent.png",
    addons: [
      { name: "EXTRA SALMON ₹1,245", label: "Extra Malabar Salmon", price: 1245.00, cals: 180 },
      { name: "EXTRA RICE ₹415", label: "Extra Saffron Basmati Rice", price: 415.00, cals: 160 },
      { name: "MANGO LASSI ₹249", label: "Alphonso Mango Lassi", price: 249.00, cals: 120 }
    ],
    nutrition: {
      country: "REGION: MALABAR COAST, INDIA • THIS THALI HAS",
      fat: "14 G",
      sodium: "520 MG",
      protein: "36 G",
      carbs: "58 G",
      desc: "Pan-roasted Atlantic salmon marinated with stone-ground coastal spices, fragrant coconut chutney, and tempered curry leaves over basmati."
    },
    allergens: ["fish"]
  },
  {
    id: "featured-tuna-sashimi",
    badge: "Tandoori Peshawari",
    heading: "Amritsari King Fish Tikka",
    breadcrumb: "FAURA > CLAY OVEN CHAR",
    description: "Fresh king fish steaks marinated in roasted carom seeds, Kashmiri chili, hung curd, and mustard oil, charred to perfection in our clay oven.",
    basePrice: 19.50 * 83,
    image: "/static/assets/tuna_poke_transparent.png",
    addons: [
      { name: "EXTRA FISH TIKKA ₹1,162", label: "Extra King Fish Tikka", price: 1162.00, cals: 170 },
      { name: "GARLIC NAAN ₹332", label: "Butter Garlic Naan", price: 332.00, cals: 180 },
      { name: "SPICED CHAAS ₹249", label: "Smoked Roasted Cumin Chaas", price: 249.00, cals: 65 }
    ],
    nutrition: {
      country: "REGION: PUNJAB, INDIA • THIS THALI HAS",
      fat: "11 G",
      sodium: "580 MG",
      protein: "42 G",
      carbs: "54 G",
      desc: "Prime king fish fillets steeped in mustard oil, cold-pressed spices, and roasted carom seeds, rich in lean marine protein."
    },
    allergens: ["fish", "dairy"]
  },
  {
    id: "featured-crispy-tofu",
    badge: "Shahi Awadh",
    heading: "Shahi Malai Paneer Angara",
    breadcrumb: "FAURA > ROYAL VEGETARIAN",
    description: "Organic cottage cheese cubes layered with smoked spices, roasted bell peppers, fresh mint chutney, and a velvety saffron cream drizzle.",
    basePrice: 15.50 * 83,
    image: "/static/assets/tofu_poke_transparent.png",
    addons: [
      { name: "EXTRA PANEER ₹664", label: "Extra Malai Paneer", price: 664.00, cals: 150 },
      { name: "LACCHA PARATHA ₹290.50", label: "Tandoori Laccha Paratha", price: 290.50, cals: 175 },
      { name: "BADAM MILK ₹332", label: "Kesar Badam Thandai", price: 332.00, cals: 140 }
    ],
    nutrition: {
      country: "REGION: AWADH, INDIA • THIS THALI HAS",
      fat: "16 G",
      sodium: "390 MG",
      protein: "24 G",
      carbs: "62 G",
      desc: "Slow-smoked malai paneer simmered in cashew-saffron gravy, rich in pure dairy calcium and comforting royal spices."
    },
    allergens: ["dairy"]
  },
  {
    id: "featured-unagi",
    badge: "Bengal Heritage",
    heading: "Smoked Bhetki Paturi",
    breadcrumb: "FAURA > EASTERN SPECIALS",
    description: "Tender bhetki fish fillet coated with fresh stone-ground mustard paste, wrapped in tender banana leaves and slow-smoked.",
    basePrice: 22.00 * 83,
    image: "/static/assets/unagi_poke_transparent.png",
    addons: [
      { name: "EXTRA BHETKI ₹1,328", label: "Extra Smoked Bhetki", price: 1328.00, cals: 210 },
      { name: "GOBINDOBHOG RICE ₹249", label: "Aged Gobindobhog Rice", price: 249.00, cals: 180 },
      { name: "GONDHORAJ COOLER ₹332", label: "Gondhoraj Lime Soda", price: 332.00, cals: 75 }
    ],
    nutrition: {
      country: "REGION: BENGAL, INDIA • THIS THALI HAS",
      fat: "22 G",
      sodium: "640 MG",
      protein: "38 G",
      carbs: "65 G",
      desc: "Delicate freshwater bhetki infused with cold-pressed mustard oil, green chilies, and turmeric, wrapped in tender plantain leaf."
    },
    allergens: ["fish"]
  },
  {
    id: "featured-chirashi",
    badge: "Nizami Royal",
    heading: "Royal Zafrani Gosht Thali",
    breadcrumb: "FAURA > DECCAN FEASTS",
    description: "Fragrant kachchi yakhni dum biryani served with mirchi ka salan, burani raita, and slow-cooked tender mountain mutton.",
    basePrice: 26.00 * 83,
    image: "/static/assets/chirashi_poke_transparent.png",
    addons: [
      { name: "EXTRA GOSHT ₹1,494", label: "Extra Lamb Shank Cut", price: 1494.00, cals: 240 },
      { name: "MIRCHI SALAN ₹415", label: "Extra Mirchi Ka Salan", price: 415.00, cals: 110 },
      { name: "ROSE PHIRNI ₹373.50", label: "Kashmiri Rose Phirni", price: 373.50, cals: 160 }
    ],
    nutrition: {
      country: "REGION: HYDERABAD, INDIA • THIS THALI HAS",
      fat: "15 G",
      sodium: "490 MG",
      protein: "44 G",
      carbs: "56 G",
      desc: "Heritage slow-dum cooked lamb shanks and long-grain aged basmati steeped with pure saffron, whole cardamom, and fried onions."
    },
    allergens: ["dairy", "eggs"]
  },
  {
    id: "featured-chicken-katsu",
    badge: "Lucknowi Murgh",
    heading: "Murgh Reshmi Kebab Platter",
    breadcrumb: "FAURA > AWADHI TANDOOR",
    description: "Melt-in-mouth chicken supreme marinated in cashew paste, cream, and mace, accompanied by flaky warqi parotta and mint dip.",
    basePrice: 18.50 * 83,
    image: "/static/assets/featured-chicken-katsu.png",
    addons: [
      { name: "EXTRA RESHMI ₹996", label: "Extra Reshmi Kebab", price: 996.00, cals: 220 },
      { name: "WARQI PAROTTA ₹332", label: "Flaky Warqi Parotta", price: 332.00, cals: 180 },
      { name: "ANARDANA DIP ₹166", label: "Pomegranate Mint Dip", price: 166.00, cals: 60 }
    ],
    nutrition: { country: "REGION: LUCKNOW, INDIA • THIS THALI HAS", fat: "18 G", sodium: "610 MG", protein: "38 G", carbs: "72 G", desc: "Velvety spiced chicken supreme steeped in roasted cashew puree and fragrant green cardamom." },
    allergens: ["dairy"]
  },
  {
    id: "featured-garden-quinoa",
    badge: "Kashmiri Subz",
    heading: "Zafrani Subz Pulao",
    breadcrumb: "FAURA > HIMALAYAN VEGAN",
    description: "Royal saffron basmati rice tossed with garden sweet peas, morel mushrooms, dried cranberries, and toasted walnuts.",
    basePrice: 16.50 * 83,
    image: "/static/assets/featured-garden-quinoa.png",
    addons: [
      { name: "MOREL MUSHROOMS ₹290.50", label: "Extra Morel Mushrooms", price: 290.50, cals: 110 },
      { name: "PULAO PORTION ₹249", label: "Extra Saffron Pulao", price: 249.00, cals: 120 },
      { name: "WALNUT CHUTNEY ₹124.50", label: "Kashmiri Walnut Chutney", price: 124.50, cals: 55 }
    ],
    nutrition: { country: "REGION: KASHMIR, INDIA • THIS THALI HAS", fat: "16 G", sodium: "390 MG", protein: "22 G", carbs: "64 G", desc: "A plant-forward royal pulao with Himalayan morels, saffron grains, green peas, and toasted walnuts." },
    allergens: []
  },
  {
    id: "featured-prawn-soba",
    badge: "Mangalore Coastal",
    heading: "Ghee Roast Tiger Prawns",
    breadcrumb: "FAURA > KARNATAKA COAST",
    description: "Jumbo coastal tiger prawns pan-tossed in fiery Byadgi chili paste, roasted cumin, and fragrant desi ghee with soft neer dosa.",
    basePrice: 21.00 * 83,
    image: "/static/assets/featured-prawn-soba.png",
    addons: [
      { name: "EXTRA PRAWNS ₹913", label: "Extra Ghee Roast Prawns", price: 913.00, cals: 150 },
      { name: "NEER DOSA ₹249", label: "Three Soft Neer Dosas", price: 249.00, cals: 140 },
      { name: "KOKUM COOLER ₹124.50", label: "Tangy Kokum Solkadhi", price: 124.50, cals: 45 }
    ],
    nutrition: { country: "REGION: MANGALORE, INDIA • THIS THALI HAS", fat: "12 G", sodium: "680 MG", protein: "35 G", carbs: "59 G", desc: "Wild tiger prawns slow-roasted in pure desi ghee, crushed black pepper, and stone-ground Byadgi chili paste." },
    allergens: ["shellfish", "dairy"]
  },
  {
    id: "featured-miso-mushroom",
    badge: "Awadhi Dhingri",
    heading: "Awadhi Dhingri Dolma",
    breadcrumb: "FAURA > VEGETARIAN GOURMET",
    description: "Wild Himalayan morels stuffed with spiced paneer and nuts, simmered in a silky almond-cardamom brown onion gravy.",
    basePrice: 15.00 * 83,
    image: "/static/assets/featured-miso-mushroom.png",
    addons: [
      { name: "EXTRA DOLMA ₹415", label: "Extra Stuffed Morel", price: 415.00, cals: 150 },
      { name: "KHAMIRI ROTI ₹249", label: "Leavened Khamiri Roti", price: 249.00, cals: 160 },
      { name: "ALMOND GRAVY ₹124.50", label: "Extra Shahi Badam Gravy", price: 124.50, cals: 70 }
    ],
    nutrition: { country: "REGION: AWADH, INDIA • THIS THALI HAS", fat: "15 G", sodium: "540 MG", protein: "25 G", carbs: "62 G", desc: "Stuffed wild mushrooms braised in aromatic almond and brown onion reduction with mace and saffron." },
    allergens: ["dairy"]
  },
  {
    id: "featured-jammy-egg",
    badge: "Dhabha Special",
    heading: "Dhabha Double Egg Curry",
    breadcrumb: "FAURA > HIGHWAY CLASSICS",
    description: "Crisp-edged browned farm eggs simmered in rustic roadside dhabha gravy with roasted cloves and cumin basmati.",
    basePrice: 13.50 * 83,
    image: "/static/assets/featured-jammy-egg.png",
    addons: [
      { name: "EXTRA EGG ₹166", label: "Extra browned egg", price: 166.00, cals: 70 },
      { name: "JEERA RICE ₹249", label: "Extra cumin basmati rice", price: 249.00, cals: 180 },
      { name: "SIRKA ONIONS ₹124.50", label: "Pickled Sirka Onions & Green Chili", price: 124.50, cals: 25 }
    ],
    nutrition: { country: "REGION: GRAND TRUNK ROAD • THIS THALI HAS", fat: "14 G", sodium: "490 MG", protein: "24 G", carbs: "58 G", desc: "Golden fried farm eggs slow-simmered in robust onion-tomato masala with black cardamom and roasted cloves." },
    allergens: ["eggs"]
  }
];

class AppController {
  constructor() {
    this.currentSlideIndex = 0;
    this.slideChangeTimer = null;
    this.revealFrameScheduled = false;

    // Elements
    this.dishBreadcrumb = document.getElementById('dishBreadcrumb');
    this.dishBadge = document.getElementById('dishBadge');
    this.dishHeading = document.getElementById('dishHeading');
    this.dishSubdesc = document.getElementById('dishSubdesc');
    this.showcaseDishImg = document.getElementById('showcaseDishImg');
    this.sliderDots = document.getElementById('sliderDots');
    if (this.sliderDots) {
      this.sliderDots.innerHTML = FEATURED_SLIDES.map((_, index) => `<span class="dot${index === 0 ? ' active' : ''}" data-index="${index}" role="button" tabindex="0" aria-label="Show dish ${index + 1}"></span>`).join('');
    }
    this.prevSlideBtn = document.getElementById('prevSlideBtn');
    this.nextSlideBtn = document.getElementById('nextSlideBtn');
    this.btnOrderNow = document.getElementById('btnOrderNow');

    // Addons
    this.addon1Title = document.getElementById('addon1Title');
    this.addon1Checkbox = document.getElementById('addon1Checkbox');
    this.addon2Title = document.getElementById('addon2Title');
    this.addon2Checkbox = document.getElementById('addon2Checkbox');
    this.addon3Title = document.getElementById('addon3Title');
    this.addon3Checkbox = document.getElementById('addon3Checkbox');

    // Nutrition elements
    this.nutritionCountry = document.getElementById('nutritionCountry');
    this.valFat = document.getElementById('valFat');
    this.valSodium = document.getElementById('valSodium');
    this.valProtein = document.getElementById('valProtein');
    this.valCarbs = document.getElementById('valCarbs');
    this.nutritionDesc = document.getElementById('nutritionDesc');
    this.btnMoreNutrition = document.getElementById('btnMoreNutrition');

    // Navigation and Catalog elements
    this.navMenuBtn = document.getElementById('navMenuBtn');
    this.navDeliveryBtn = document.getElementById('navDeliveryBtn');
    this.catalogSection = document.getElementById('catalogSection');
    this.dishGrid = document.getElementById('dishGrid');
    this.dishRevealObserver = 'IntersectionObserver' in window
      ? new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 })
      : null;
    this.searchInput = document.getElementById('searchInput');
    this.headerCartBtn = document.getElementById('headerCartBtn');
    this.headerCartCount = document.getElementById('headerCartCount');

    // Engines
    this.allergenShield = new AllergenShieldEngine();
    this.dishBuilder = new DishBuilder();
    this.orderTracker = new OrderTrackerWidget();
    this.accountFeatures = new AccountMenuFeatures();

    window.openCustomizerModal = (dish) => this.dishBuilder.open(dish);
    window.orderTrackerWidget = this.orderTracker;
    window.optimisticCart = optimisticCart;
    window.tableReservationWidget = tableReservationWidget;
    this.specialtyMenus = new SpecialtyMenus();
    this.tableReservation = tableReservationWidget;
    this.bournetSection = new BournetSectionComponent('bournetGrid');
    this.continentalSection = new ContinentalMenuComponent('continentalGrid');
    window.continentalMenu = this.continentalSection;
    this.ambientAura = new AmbientAuraController();
    window.ambientAura = this.ambientAura;

    this.bindEvents();
    this.renderSlide(0);
    this.fetchMenu();
  }

  bindEvents() {
    window.addEventListener('scroll', () => this.revealVisibleDishCards(), { passive: true });
    window.addEventListener('resize', () => this.revealVisibleDishCards());

    // Slider arrows
    if (this.prevSlideBtn) {
      this.prevSlideBtn.addEventListener('click', () => {
        this.currentSlideIndex = (this.currentSlideIndex - 1 + FEATURED_SLIDES.length) % FEATURED_SLIDES.length;
        this.renderSlide(this.currentSlideIndex);
      });
    }

    if (this.nextSlideBtn) {
      this.nextSlideBtn.addEventListener('click', () => {
        this.currentSlideIndex = (this.currentSlideIndex + 1) % FEATURED_SLIDES.length;
        this.renderSlide(this.currentSlideIndex);
      });
    }

    // Slider dots
    if (this.sliderDots) {
      this.sliderDots.querySelectorAll('.dot').forEach((dot) => {
        dot.addEventListener('click', () => {
          this.currentSlideIndex = parseInt(dot.dataset.index, 10);
          this.renderSlide(this.currentSlideIndex);
        });
      });
    }

    // Order Now from showcase
    if (this.btnOrderNow) {
      this.btnOrderNow.addEventListener('click', () => {
        this.orderFeaturedDish();
      });
    }

    // Header cart button
    if (this.headerCartBtn) {
      this.headerCartBtn.addEventListener('click', () => {
        optimisticCart.openDrawer();
      });
    }

    // Smooth navigation links
    if (this.navMenuBtn && this.catalogSection) {
      this.navMenuBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.catalogSection.scrollIntoView({ behavior: 'smooth' });
      });
    }

    if (this.btnMoreNutrition && this.catalogSection) {
      this.btnMoreNutrition.addEventListener('click', () => {
        this.catalogSection.scrollIntoView({ behavior: 'smooth' });
      });
    }

    if (this.navDeliveryBtn) {
      this.navDeliveryBtn.addEventListener('click', (e) => {
        e.preventDefault();
        optimisticCart.openDrawer();
      });
    }

    const navReservationBtn = document.getElementById('navReservationBtn');
    if (navReservationBtn) {
      navReservationBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.tableReservation.open();
      });
    }

    const navBournetBtn = document.getElementById('navBournetBtn');
    const bournetSectionEl = document.getElementById('bournetSection');
    if (navBournetBtn && bournetSectionEl) {
      navBournetBtn.addEventListener('click', (e) => {
        e.preventDefault();
        bournetSectionEl.scrollIntoView({ behavior: 'smooth' });
      });
    }

    // Search filter
    if (this.searchInput) {
      let debounce = null;
      this.searchInput.addEventListener('input', (e) => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
          store.setSearchQuery(e.target.value);
        }, 120);
      });
    }

    // Store subscription
    store.subscribe((state, event) => {
      if (['MENU_UPDATED', 'ALLERGENS_CHANGED', 'SEARCH_CHANGED', 'DIETARY_FILTER_CHANGED', 'RESTAURANT_FILTER_CHANGED'].includes(event)) {
        this.renderCatalogGrid();
        this.checkFeaturedDishAllergens();
      }
      if (event === 'RESTAURANT_FILTER_CHANGED') this.fetchMenu(state.selectedRestaurantId);
      if (event === 'CART_UPDATED') {
        if (this.headerCartCount) {
          this.headerCartCount.textContent = state.cartSummary.itemCount;
        }
      }
    });
  }

  renderSlide(index) {
    const dish = FEATURED_SLIDES[index];
    if (!dish) return;

    if (this.dishBreadcrumb) this.dishBreadcrumb.textContent = dish.breadcrumb;
    if (this.dishBadge) this.dishBadge.textContent = dish.badge;
    if (this.dishHeading) this.dishHeading.textContent = dish.heading;
    if (this.dishSubdesc) this.dishSubdesc.textContent = dish.description;

    // Center Image with smooth fade
    if (this.showcaseDishImg) {
      clearTimeout(this.slideChangeTimer);
      this.showcaseDishImg.style.opacity = '0';
      this.showcaseDishImg.style.transform = 'scale(0.92)';
      this.slideChangeTimer = setTimeout(() => {
        this.showcaseDishImg.src = dish.image;
        this.showcaseDishImg.alt = dish.heading;
        this.showcaseDishImg.style.opacity = '1';
        this.showcaseDishImg.style.transform = 'scale(1)';
      }, 150);
    }

    // Addons
    if (dish.addons[0] && this.addon1Title && this.addon1Checkbox) {
      this.addon1Title.textContent = dish.addons[0].name;
      this.addon1Checkbox.dataset.name = dish.addons[0].label;
      this.addon1Checkbox.dataset.price = dish.addons[0].price;
      this.addon1Checkbox.dataset.cals = dish.addons[0].cals;
      this.addon1Checkbox.checked = false;
    }
    if (dish.addons[1] && this.addon2Title && this.addon2Checkbox) {
      this.addon2Title.textContent = dish.addons[1].name;
      this.addon2Checkbox.dataset.name = dish.addons[1].label;
      this.addon2Checkbox.dataset.price = dish.addons[1].price;
      this.addon2Checkbox.dataset.cals = dish.addons[1].cals;
      this.addon2Checkbox.checked = false;
    }
    if (dish.addons[2] && this.addon3Title && this.addon3Checkbox) {
      this.addon3Title.textContent = dish.addons[2].name;
      this.addon3Checkbox.dataset.name = dish.addons[2].label;
      this.addon3Checkbox.dataset.price = dish.addons[2].price;
      this.addon3Checkbox.dataset.cals = dish.addons[2].cals;
      this.addon3Checkbox.checked = false;
    }

    // Nutritional Facts
    if (this.nutritionCountry) this.nutritionCountry.textContent = dish.nutrition.country;
    if (this.valFat) this.valFat.textContent = dish.nutrition.fat;
    if (this.valSodium) this.valSodium.textContent = dish.nutrition.sodium;
    if (this.valProtein) this.valProtein.textContent = dish.nutrition.protein;
    if (this.valCarbs) this.valCarbs.textContent = dish.nutrition.carbs;
    if (this.nutritionDesc) this.nutritionDesc.textContent = dish.nutrition.desc;

    // Dots
    if (this.sliderDots) {
      this.sliderDots.querySelectorAll('.dot').forEach((d, i) => {
        if (i === index) d.classList.add('active');
        else d.classList.remove('active');
      });
    }

    this.checkFeaturedDishAllergens();
  }

  checkFeaturedDishAllergens() {
    const dish = FEATURED_SLIDES[this.currentSlideIndex];
    if (!dish) return;

    const activeAllergens = [...store.state.activeAllergens];
    const conflicts = dish.allergens.filter(a => activeAllergens.includes(a.toLowerCase()));

    if (this.btnOrderNow) {
      if (conflicts.length > 0) {
        this.btnOrderNow.style.borderColor = 'var(--shield-coral)';
        this.btnOrderNow.style.color = 'var(--shield-coral)';
        this.btnOrderNow.textContent = `ORDER WITH SWAP (⚠️ ${conflicts.join(', ').toUpperCase()})`;
      } else {
        this.btnOrderNow.style.borderColor = 'var(--bistro-dark)';
        this.btnOrderNow.style.color = 'var(--bistro-dark)';
        this.btnOrderNow.textContent = "ORDER NOW";
      }
    }
  }

  orderFeaturedDish() {
    const dish = FEATURED_SLIDES[this.currentSlideIndex];
    if (!dish) return;

    // Collect selected addons
    const selections = [];
    [this.addon1Checkbox, this.addon2Checkbox, this.addon3Checkbox].forEach((chk, idx) => {
      if (chk && chk.checked) {
        selections.push({
          step_id: `addon-${idx+1}`,
          option_id: `opt-${idx+1}`,
          name: chk.dataset.name,
          price: parseFloat(chk.dataset.price),
          calories: parseInt(chk.dataset.cals, 10),
          allergens: []
        });
      }
    });

    const dishModel = {
      id: dish.id,
      name: `${dish.badge} ${dish.heading}`,
      base_price: dish.basePrice,
      calories: 540,
      image_url: dish.image,
      prep_time_mins: 12,
      allergens: dish.allergens
    };

    optimisticCart.addItem(dishModel, selections);
  }

  async fetchMenu(restaurantId = null) {
    try {
      const url = restaurantId
        ? `/api/restaurants/${encodeURIComponent(restaurantId)}/dishes`
        : '/api/v1/menu';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Menu fetch failed');
      const data = await res.json();
      store.setMenuItems(data);
    } catch (err) {
      console.warn('Backend fetch fallback:', err);
    }
  }

  renderCatalogGrid() {
    const items = store.state.filteredItems;
    if (!this.dishGrid) return;

    if (items.length === 0) {
      this.dishGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--bistro-gray-text);">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🍣</div>
          <h3 style="color: var(--bistro-dark); margin-bottom: 0.3rem;">No Dishes Match Your Shield Filter</h3>
          <p style="font-size: 0.85rem;">Try relaxing your allergen filters or adjusting your search.</p>
        </div>
      `;
      return;
    }

    this.dishGrid.innerHTML = items.map((dish) => {
      const detected = dish.detectedAllergens || [];
      const hasConflicts = detected.length > 0;
      const stateClass = hasConflicts ? 'state-unsafe' : 'state-safe';

      return `
        <div class="dish-card ${stateClass}" data-id="${dish.id}">
          <div class="card-image-wrap">
            <img src="${dish.image_url}" alt="${dish.name}" class="card-img" loading="lazy" onerror="this.closest('.dish-card')?.remove()">
          </div>
          <div class="card-content">
            <div class="card-title-row">
              <h3 class="dish-name">${dish.name}</h3>
              <span class="dish-price">${formatINR(dish.base_price)}</span>
            </div>
            <div class="dish-meta"><span>${(dish.dietary_type || 'veg').replace('-', ' ')}</span><span>${dish.rating.toFixed(1)} ★</span></div>
            <p class="dish-desc">${dish.description}</p>
            ${hasConflicts ? `
              <div class="allergen-alert-banner">
                <span>⚠️ Contains: ${detected.join(', ')}</span>
                <button class="btn-swap-trigger anim-bounce-click" data-id="${dish.id}">Swap</button>
              </div>
            ` : ''}
            <div style="margin-top: auto; display: flex; gap: 0.5rem;">
              <button class="btn-order-now anim-bounce-click btn-grid-add" data-id="${dish.id}" style="width: 100%; padding: 0.55rem; font-size: 0.75rem;">
                ${dish.customizable ? 'Build this meal' : '+ Add to Order'}
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    this.observeDishCards();

    // Attach click events
    this.dishGrid.querySelectorAll('.btn-grid-add').forEach((b) => {
      b.addEventListener('click', () => {
        const id = b.dataset.id;
        const item = store.state.menuItems.find(d => d.id === id);
        if (item?.customizable) this.dishBuilder.open(item);
        else if (item) optimisticCart.addItem(item);
      });
    });

    this.dishGrid.querySelectorAll('.btn-swap-trigger').forEach((b) => {
      b.addEventListener('click', () => {
        const id = b.dataset.id;
        const item = store.state.menuItems.find(d => d.id === id);
        if (item) this.allergenShield.openSwapModal(item);
      });
    });
  }

  observeDishCards() {
    this.dishGrid.querySelectorAll('.dish-card').forEach((card, index) => {
      card.classList.add('dish-card-reveal');
      card.style.setProperty('--dish-reveal-delay', `${(index % 4) * 55}ms`);
      if (this.dishRevealObserver) this.dishRevealObserver.observe(card);
      else card.classList.add('is-visible');
    });
    this.revealVisibleDishCards();
  }

  revealVisibleDishCards() {
    const viewportHeight = window.innerHeight;
    this.dishGrid.querySelectorAll('.dish-card-reveal:not(.is-visible)').forEach((card) => {
      const bounds = card.getBoundingClientRect();
      if (bounds.top < viewportHeight * 0.92 && bounds.bottom > 0) {
        card.classList.add('is-visible');
      }
    });
  }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', () => {
  new AppController();
});
