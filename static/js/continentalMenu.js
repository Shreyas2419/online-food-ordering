/**
 * Continental Menu Section Component for Faura.
 * Renders European & Continental gastronomic delicacies (Pastas, Steaks, Bakes, Risotto, Seafood)
 * with category filtering and direct optimistic cart integration.
 */
import { optimisticCart } from './optimisticCart.js';

export const CONTINENTAL_ITEMS = [
  {
    id: "cont-pasta-01",
    name: "Truffle & Porcini Wild Mushroom Fettuccine",
    category: "pasta",
    dietary_type: "veg",
    description: "Hand-rolled ribbons of fresh fettuccine tossed in aromatic Umbrian black truffle butter, pan-roasted porcini mushrooms, baby thyme, and 24-month aged Parmigiano-Reggiano.",
    base_price: 890.00,
    calories: 620,
    protein_g: 22,
    prep_time_mins: 16,
    dietaryTags: ["Artisanal Pasta", "Umbrian Truffle", "Vegetarian", "Italian Classic"],
    imageUrl: "https://images.pexels.com/photos/1279330/pexels-photo-1279330.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Tuscany, Italy"
  },
  {
    id: "cont-salmon-02",
    name: "Pan-Seared Norwegian Herb Salmon",
    category: "seafood",
    dietary_type: "non-veg",
    description: "Crisp-skin Atlantic salmon rested on charred asparagus spears, silken parsnip-vanilla mousseline, and a fragrant caper-dill lemon noisette reduction.",
    base_price: 1250.00,
    calories: 540,
    protein_g: 42,
    prep_time_mins: 18,
    dietaryTags: ["Atlantic Catch", "Gluten-Free", "Rich Omega-3", "French Technique"],
    imageUrl: "https://images.pexels.com/photos/3655916/pexels-photo-3655916.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Nordic Fjord"
  },
  {
    id: "cont-steak-03",
    name: "Char-Grilled Rosemary Tenderloin Steak",
    category: "steak",
    dietary_type: "non-veg",
    description: "28-day dry-aged prime beef tenderloin flame-seared over rosemary embers, accompanied by roasted bone marrow jus, truffle-whipped Yukon gold mash, and glazed baby heirloom carrots.",
    base_price: 1450.00,
    calories: 760,
    protein_g: 52,
    prep_time_mins: 22,
    dietaryTags: ["Chef's Signature Cut", "Dry-Aged", "High Protein", "Bordelaise Glaze"],
    imageUrl: "https://images.pexels.com/photos/3535383/pexels-photo-3535383.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Bordeaux, France"
  },
  {
    id: "cont-bake-04",
    name: "Aubergine & Buffalo Mozzarella Parmigiana Bake",
    category: "bake",
    dietary_type: "veg",
    description: "Golden-crusted layers of sliced Italian aubergine, slow-simmered San Marzano tomato ragu, melted Campania buffalo mozzarella, and fresh sweet basil.",
    base_price: 740.00,
    calories: 580,
    protein_g: 24,
    prep_time_mins: 20,
    dietaryTags: ["Oven Baked", "Buffalo Mozzarella", "Vegetarian", "Campania Classic"],
    imageUrl: "https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Campania, Italy"
  },
  {
    id: "cont-risotto-05",
    name: "Saffron & Wild Mushroom Arborio Risotto",
    category: "bake",
    dietary_type: "veg",
    description: "Creamy slow-stirred Italian carnaroli rice infused with genuine saffron threads, white wine reduction, sautéed forest chanterelles, and crispy sage crisps.",
    base_price: 820.00,
    calories: 610,
    protein_g: 18,
    prep_time_mins: 19,
    dietaryTags: ["Carnaroli Arborio", "Kashmiri Saffron", "Gluten-Free", "Milanese Tradition"],
    imageUrl: "https://images.pexels.com/photos/5638527/pexels-photo-5638527.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Milan, Italy"
  },
  {
    id: "cont-gratin-06",
    name: "Oven-Roasted Mediterranean Vegetable Gratin",
    category: "bake",
    dietary_type: "veg",
    description: "Layered zucchini, sweet bell peppers, artichoke hearts, and sliced potatoes baked in seasoned herb cream under a bubbling golden Gruyère crust.",
    base_price: 690.00,
    calories: 520,
    protein_g: 16,
    prep_time_mins: 20,
    dietaryTags: ["French Gratin", "Gruyère Crust", "Provençal Herbs", "Vegetarian"],
    imageUrl: "https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Provence, France"
  },
  {
    id: "cont-chicken-07",
    name: "Tuscan Herb-Roasted Corn-Fed Chicken Supreme",
    category: "steak",
    dietary_type: "non-veg",
    description: "Pan-roasted tender chicken supreme with crisp skin, creamy mascarpone polenta, blistered balsamic cherry tomatoes, and Meyer lemon sage pan sauce.",
    base_price: 790.00,
    calories: 590,
    protein_g: 44,
    prep_time_mins: 17,
    dietaryTags: ["Corn-Fed Supreme", "Creamy Polenta", "Balsamic Jus", "Tuscan Grill"],
    imageUrl: "https://images.pexels.com/photos/2338407/pexels-photo-2338407.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Tuscany, Italy"
  },
  {
    id: "cont-seabass-08",
    name: "Pan-Seared Sea Bass with Lemon Caper Butter",
    category: "seafood",
    dietary_type: "non-veg",
    description: "Flaky Mediterranean sea bass seared in browned beurre noisette, served with sautéed baby zucchini coins, confit crushed garlic, and charred lemon wedges.",
    base_price: 1180.00,
    calories: 480,
    protein_g: 38,
    prep_time_mins: 15,
    dietaryTags: ["Mediterranean Catch", "Caper Butter", "Garlic Confit", "Light & Fresh"],
    imageUrl: "https://images.pexels.com/photos/262959/pexels-photo-262959.jpeg?auto=compress&cs=tinysrgb&w=1000",
    origin: "Riviera Coastal"
  }
];

export class ContinentalMenuComponent {
  constructor(containerId = 'continentalGrid') {
    this.container = document.getElementById(containerId);
    this.tabsContainer = document.getElementById('continentalTabs');
    this.dishes = CONTINENTAL_ITEMS;
    this.activeFilter = 'all';

    this.init();
  }

  async init() {
    this.bindTabEvents();
    this.attachEventListeners();

    // Fetch live backend data if available, maintaining fallback resilience
    try {
      const res = await fetch('/api/v1/menu/continental');
      if (res.ok) {
        const liveData = await res.json();
        if (Array.isArray(liveData) && liveData.length > 0) {
          this.dishes = liveData;
          this.render();
        }
      }
    } catch {
      // Continue seamlessly using preloaded dishes
    }
  }

  bindTabEvents() {
    if (!this.tabsContainer) return;

    this.tabsContainer.querySelectorAll('.continental-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        this.tabsContainer.querySelectorAll('.continental-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.activeFilter = tab.getAttribute('data-category') || 'all';
        this.render();
      });
    });
  }

  getFilteredDishes() {
    if (!this.activeFilter || this.activeFilter === 'all') return this.dishes;
    return this.dishes.filter(d => {
      if (d.category === this.activeFilter || d.sub_category === this.activeFilter) return true;
      const lowerId = (d.id || '').toLowerCase();
      const lowerName = (d.name || '').toLowerCase();
      if (this.activeFilter === 'pasta') {
        return lowerId.includes('pasta') || lowerName.includes('fettuccine') || lowerName.includes('cannelloni') || lowerName.includes('pasta');
      }
      if (this.activeFilter === 'steak') {
        return lowerId.includes('steak') || lowerId.includes('chicken') || lowerName.includes('steak') || lowerName.includes('tenderloin') || lowerName.includes('chicken');
      }
      if (this.activeFilter === 'bake') {
        return lowerId.includes('bake') || lowerId.includes('pie') || lowerId.includes('risotto') || lowerId.includes('gratin') || lowerName.includes('bake') || lowerName.includes('risotto') || lowerName.includes('pie') || lowerName.includes('gratin');
      }
      if (this.activeFilter === 'seafood') {
        return lowerId.includes('salmon') || lowerId.includes('seabass') || lowerName.includes('salmon') || lowerName.includes('sea bass') || lowerName.includes('seafood');
      }
      return false;
    });
  }

  render() {
    if (!this.container) return;
    const filtered = this.getFilteredDishes();

    this.container.innerHTML = filtered.map(dish => this.renderDishCard(dish)).join('');
    this.attachEventListeners();
  }

  renderDishCard(dish) {
    const isVeg = dish.dietary_type === 'veg';
    const badgeClass = isVeg ? 'dietary-badge-veg' : 'dietary-badge-nonveg';
    const badgeIcon = isVeg ? '🥦' : '🍗';
    const badgeLabel = isVeg ? 'Vegetarian' : 'Non-Veg';
    const imgUrl = dish.imageUrl || dish.image_url;

    const tagsHtml = (dish.dietaryTags || []).map(tag => 
      `<span class="bournet-tag">${escapeHtml(tag)}</span>`
    ).join('');

    return `
      <article class="dish-card continental-dish-card anim-fade-in" id="card-${escapeHtml(dish.id)}" data-dish-id="${escapeHtml(dish.id)}">
        <div class="dish-card-image-wrap">
          <img src="${escapeHtml(imgUrl)}" alt="${escapeHtml(dish.name)}" class="dish-card-img" loading="lazy">
          <div class="continental-badge-overlay">
            <span class="${badgeClass}">
              <span aria-hidden="true">${badgeIcon}</span> ${badgeLabel}
            </span>
          </div>
          <span class="continental-cuisine-tag">${escapeHtml(dish.origin || 'Continental')}</span>
        </div>

        <div class="dish-card-content">
          <div class="bournet-tags-row">
            ${tagsHtml}
          </div>

          <h3 class="dish-card-title">${escapeHtml(dish.name)}</h3>
          <p class="dish-card-description">${escapeHtml(dish.description)}</p>

          <div class="dish-meta-row">
            <span class="dish-meta-pill">🔥 ${dish.calories} kcal</span>
            <span class="dish-meta-pill">⚡ ${dish.protein_g}g protein</span>
            <span class="dish-meta-pill">⏱️ ${dish.prep_time_mins}m</span>
          </div>

          <div class="dish-card-footer">
            <div class="dish-price-block">
              <span class="dish-price-currency">₹</span>
              <span class="dish-price-value">${Number(dish.base_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>

            <button type="button" class="btn-order-now btn-add-continental anim-bounce-click" data-dish-id="${escapeHtml(dish.id)}">
              <span>+ Add to Order</span>
            </button>
          </div>
        </div>
      </article>
    `;
  }

  attachEventListeners() {
    if (!this.container) return;

    this.container.querySelectorAll('.btn-add-continental').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const dishId = e.currentTarget.getAttribute('data-dish-id');
        this.handleAddToCart(dishId, e.currentTarget);
      });
    });
  }

  handleAddToCart(dishId, btnElement) {
    const dish = this.dishes.find(d => d.id === dishId);
    if (!dish) return;

    // Direct integration with Faura optimistic cart
    optimisticCart.addItem({
      id: dish.id,
      name: dish.name,
      base_price: dish.base_price,
      image_url: dish.imageUrl || dish.image_url,
      calories: dish.calories || 550,
      prep_time_mins: dish.prep_time_mins || 18,
    });

    // Provide visual feedback
    const originalText = btnElement.innerHTML;
    btnElement.innerHTML = `<span>Added ✓</span>`;
    btnElement.style.background = '#2E7D32';
    btnElement.style.borderColor = '#2E7D32';

    setTimeout(() => {
      btnElement.innerHTML = originalText;
      btnElement.style.background = '';
      btnElement.style.borderColor = '';
    }, 1400);
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
