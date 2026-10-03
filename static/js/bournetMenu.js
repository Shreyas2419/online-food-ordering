/**
 * Feature 3: Bournet (Gourmet) Section Component
 * Renders the 6 haute cuisine dishes in a responsive luxury grid layout
 * with dietary pills, engaging descriptions, and direct cart integration.
 */
import { formatINR } from './currency.js';
import { optimisticCart } from './optimisticCart.js';

export const BOURNET_ITEMS = [
  {
    id: "bournet-wagyu-01",
    name: "Truffle Glazed Wagyu A5 Striploin",
    description: "Pan-seared Miyazaki Wagyu A5 basted in winter black truffle shoyu glaze, served alongside smoked shiitake puree, bone marrow jus reduction, and edible 24-karat gold leaf flakes.",
    price: 3499.00,
    dietaryTags: ["Chef's Signature", "Dairy-Free", "Rich Umami", "Gluten-Free Option"],
    imageUrl: "https://images.unsplash.com/photo-1544025162-d76694265947?w=900&auto=format&fit=crop&q=85",
  },
  {
    id: "bournet-lobster-02",
    name: "Lobster Thermidor & Caviar Donburi",
    description: "Butter-poached Maine lobster tail and claw medallions resting over seasoned Koshihikari rice, crowned with Royal Oscietra caviar, yuzu sabayon, and charred scallion-infused oil.",
    price: 2899.00,
    dietaryTags: ["Shellfish", "Premium Marine", "Egg", "Rich Omega-3"],
    imageUrl: "https://images.unsplash.com/photo-1559847844-5315695dadae?w=900&auto=format&fit=crop&q=85",
  },
  {
    id: "bournet-saffron-03",
    name: "Imperial Saffron & Wild Morel Risotto",
    description: "Acquerello aged carnaroli rice simmered with rare Persian saffron threads, wild Himalayan morel mushrooms, 36-month Parmigiano-Reggiano crisps, and cold-pressed herb oil.",
    price: 1899.00,
    dietaryTags: ["Vegetarian", "Gluten-Free", "Gourmet Garden", "Nut-Free"],
    imageUrl: "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?w=900&auto=format&fit=crop&q=85",
  },
  {
    id: "bournet-cod-04",
    name: "Smoked Miso Black Cod with Edamame Velouté",
    description: "72-hour Kyoto saikyo miso marinated Alaskan black cod, blistered over binchotan charcoal and accompanied by silky edamame velouté, pickled lotus root, and shiso flowers.",
    price: 2499.00,
    dietaryTags: ["Pescatarian", "Gluten-Free", "Dairy-Free", "High Protein"],
    imageUrl: "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=900&auto=format&fit=crop&q=85",
  },
  {
    id: "bournet-scallop-05",
    name: "24k Gold Leaf Hokkaido Scallop Crudo",
    description: "Hand-dived sashimi-grade Hokkaido sea scallops sliced paper-thin, accented with white truffle oil emulsion, Australian finger lime pearls, pink peppercorns, and micro-herbs.",
    price: 2299.00,
    dietaryTags: ["Raw Bar", "Shellfish", "Gluten-Free", "Low Carb"],
    imageUrl: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=900&auto=format&fit=crop&q=85",
  },
  {
    id: "bournet-terrine-06",
    name: "Artisanal Wild Truffle & Mushroom Terrine",
    description: "Layered terrine of French chanterelles, porcini, and black trumpet mushrooms infused with fresh thyme, served with toasted sourdough brioche points and shallot-fig relish.",
    price: 1699.00,
    dietaryTags: ["100% Vegan", "Plant-Forward", "Nut-Free", "Earth Harvest"],
    imageUrl: "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=900&auto=format&fit=crop&q=85",
  },
];

export class BournetSectionComponent {
  constructor(containerId = 'bournetGrid') {
    this.container = document.getElementById(containerId);
    this.items = BOURNET_ITEMS;
    this.init();
  }

  async init() {
    // Attempt live fetch from backend or fallback to authoritative local data
    try {
      const res = await fetch('/api/v1/menu/bournet');
      if (res.ok) {
        this.items = await res.json();
      }
    } catch {
      // Fallback to static items
    }
    this.render();
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = this.items.map((dish) => `
      <article class="bournet-card" data-dish-id="${dish.id}">
        <div class="bournet-card-media">
          <img src="${dish.imageUrl}" alt="${dish.name}" class="bournet-img" loading="lazy">
          <span class="bournet-exclusive-badge">👑 Bournet Privé</span>
        </div>

        <div class="bournet-card-body">
          <div class="bournet-tags-row">
            ${(dish.dietaryTags || []).map(tag => `<span class="bournet-tag-pill">${tag}</span>`).join('')}
          </div>

          <div class="bournet-header-row">
            <h3 class="bournet-title">${dish.name}</h3>
            <span class="bournet-price">${formatINR(dish.price)}</span>
          </div>

          <p class="bournet-desc">${dish.description}</p>

          <div class="bournet-action-row">
            <span class="bournet-prep-sla">⏱️ 18-22 mins chef plating</span>
            <button type="button" class="btn-bournet-order anim-bounce-click" data-action="order-bournet" data-id="${dish.id}">
              Add to Bistro Order ➔
            </button>
          </div>
        </div>
      </article>
    `).join('');

    // Attach order event listeners
    this.container.querySelectorAll('[data-action="order-bournet"]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const dishId = e.currentTarget.dataset.id;
        const item = this.items.find((d) => d.id === dishId);
        if (item) {
          optimisticCart.addItem({
            id: item.id,
            name: item.name,
            base_price: item.price,
            image_url: item.imageUrl,
            calories: 650,
            prep_time_mins: 20,
          });
        }
      });
    });
  }
}
