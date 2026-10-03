# 🛸 ZERO-G KITCHEN: Anti-Gravity Single-Page Food Ordering Engine

A high-performance, single-page online food ordering application designed with an **Anti-Gravity Floating Aesthetic** tailored for Gen-Z. Built using Vanilla HTML5, modern CSS3 Custom Properties (Variables), ES6+ JavaScript, and a high-throughput Python FastAPI backend with Async SQLAlchemy, Pydantic v2, and real-time WebSockets.

---

## 🎨 Design Language & UI/UX System

1. **Zero-G Kitchen Bistro Theme**:
  - Cream-white canvas (`#F9F9FB`) with sushi-orange accents (`#F37021`), charcoal text, and restrained glass effects.
  - Rounded food cards and focused overlays keep the menu, order drawer, and tracker legible.
  - Display typography uses Google Fonts *Jost*.

2. **Micro-Interactions & Physics (60 FPS Performance)**:
   - **Elastic Spring Hover**: Cards float up on hover using `transform: translateY(-8px) scale(1.02)` with `cubic-bezier(0.34, 1.56, 0.64, 1)`.
   - **Haptic Micro-Bounces**: Interactive buttons and pills bounce with `transform: scale(0.95)` on tap/click.
   - **Zero Layout Shift (CLS)**: Shimmer skeleton loaders prevent Cumulative Layout Shift during initial data hydration.

---

## 🛡️ Core Features

### 1. Allergic Ingredient Shield & Engine
- **Floating Pill Toggles**: Real-time toggles for major allergens:
  - 🥜 Peanut-Free
  - 🌾 Gluten-Free
  - 🥛 Dairy-Free
  - 🌱 Soy-Free
  - 🦐 Shellfish-Free
- **Dynamic Safe / Unsafe Card Separation**:
  - **Safe Items**: Displayed with glowing green borders and an `"Allergen Shield: Safe"` badge.
  - **High-Risk Items**: Highlighted with an animated glowing Neon Coral border, explicit alert badges (e.g., `⚠️ Contains Peanuts & Soy`), and an interactive `"Exclude / Swap Ingredient"` drawer trigger.
- **Client State Management**:
  - Filter menu items in real-time instantly without re-rendering or page reloads.

### 2. Optimistic Cart & Modular Dish Builder
- **Interactive Visual Dish Builder**:
  - Step-by-step modular customizer modal for build-your-own bowls and pizzas.
  - Dynamic topping selection with allergen guard tags and safe substitute recommendations.
  - Live calorie & price recalculator in the modal footer.
- **Optimistic UI Updates**:
  - Immediate bottom cart count and subtotal increment with server sync and rollback handling.
- **Floating Glass Bottom Cart Capsule**:
  - Persistent capsule displaying item count, subtotal, and dynamic free delivery progress bar:
    - *Example*: `"Add ₹290.50 more for FREE Zero-G Delivery!"` or `"✨ Free Zero-G Delivery Unlocked!"`
- **Slide-Up Order Drawer**:
  - Quantity increment/decrement, live subtotal, and interactive distance slider (0.5 km – 15 km).

### 3. Real-Time Tracking & Dynamic ETA
- **Distance & SLA ETA Engine**:
  - Calculates ETA dynamically:
    $$\text{ETA} = \text{Prep Time} + (\text{Active Kitchen Queue} \times 2\text{ mins}) + \text{Transit Time}$$
- **WebSocket Live Telemetry & Micro-Map Widget**:
  - Connects to `/ws/order-tracking/{order_id}`.
  - 4-stage stepper: **Received** ➔ **Preparing** ➔ **Out for Delivery** ➔ **Delivered**.
  - **HTML5 Canvas Micro-Map**: 60 FPS cyber-grid with launch pad, destination beacon, radar sweep, and animated autonomous quadcopter drone with thruster glow.
  - Live HUD telemetry: Drone Velocity, Altitude, Battery %, and Distance Remaining.

---

## 🛠️ Technical Architecture

```
online_food_ordering/
├── app/
│   ├── main.py              # FastAPI app, lifespan setup, static mounting
│   ├── database.py          # Async SQLAlchemy 2.0 engine + aiosqlite
│   ├── models.py            # DishModel and OrderModel ORM tables
│   ├── schemas.py           # Pydantic v2 validation models
│   ├── initial_data.py      # Seed data with 50+ dishes per dietary filter
│   └── routers/
│       ├── menu.py          # /api/v1/menu and /api/v1/menu/safe-search
│       ├── cart.py          # /api/v1/cart SLA engine & validation
│       └── order.py         # /api/v1/orders and /ws/order-tracking/{order_id}
├── static/
│   ├── index.html           # Single-Page Application HTML5 structure
│   ├── css/
│   │   ├── variables.css    # Color tokens, spring curves, elevation shadows
│   │   ├── animations.css   # Keyframe levitation, radar sweeps, skeletons
│   │   ├── components.css   # Allergen pills, cards, capsule, modals, HUD
│   │   └── main.css         # Dark obsidian cyber-grid layout
│   └── js/
│       ├── app.js           # App coordinator & card renderer
│       ├── state.js         # Reactive store with localStorage persistence
│       ├── allergenShield.js# Dynamic allergen filter engine & swap drawer
│       ├── dishBuilder.js   # Step-by-step modular customizer modal
│       ├── optimisticCart.js# Optimistic cart state & SLA calculator
│       ├── microMap.js      # 60 FPS HTML5 Canvas micro-map illustration
│       └── orderTracker.js  # WebSocket client & stage stepper sync
├── tests/
│   └── test_system.py       # Integration tests for all endpoints & WS
├── run.sh                   # Startup script
└── README.md
```

---

## 🚀 Running the Application

1. **Activate the Virtual Environment & Run**:
   ```bash
   ./run.sh
   ```
   Or:
   ```bash
   .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open in Browser**:
   Navigate to:
   ```
   http://localhost:8000/
   ```

3. **Run Automated Integration Tests**:
   ```bash
   PYTHONPATH=. .venv/bin/python tests/test_system.py
   ```

## Local Configuration

The FastAPI service serves the static frontend and API from the same origin; no separate Node/React client process is required. For a fresh environment, create a virtual environment and install the dependency manifest:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

Optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | SQLite file at `app/food_ordering.db` | SQLAlchemy async URL; use `sqlite+aiosqlite:///...` or a compatible async PostgreSQL driver URL. |
| `DATABASE_PATH` | `app/food_ordering.db` | Alternate SQLite file path when `DATABASE_URL` is not set. |
| `APP_SECRET_KEY` | Development-only fallback | Set a long random secret before deployment; used to sign account tokens. |
| `CORS_ORIGINS` | `http://localhost:8000,http://127.0.0.1:8000` | Comma-separated allowed browser origins. |
| `PAYMENT_WEBHOOK_SECRET` | Unset | HMAC-SHA256 secret required to settle online payment events. |

Example local startup:

```bash
APP_SECRET_KEY="replace-with-a-long-random-secret" CORS_ORIGINS="http://localhost:8000" ./run.sh
```

On startup, tables are created/migrated and seed data is reconciled idempotently. The seed includes seven restaurant profiles, premium items, and distinct real Pexels food photos for every menu/gourmet dish, plus database-backed custom-builder options. Dish photo IDs are curated in `app/food_photos.py`; image-load failures remove that card instead of showing a repeated placeholder.

The ten featured hero dishes use original transparent PNG illustrations with a shared bowl-and-chopsticks composition and dish-specific ingredients. Regenerate them with `python3 scripts/generate_featured_dish_art.py` on a machine with ImageMagick installed.

### REST API

- `POST /api/v1/account/signup`, `POST /api/v1/account/login`, and authenticated account/address endpoints manage users and saved addresses.
- `GET /api/dishes/premium` returns curated premium dishes from SQLite.
- `GET /api/restaurants` and `GET /api/restaurants/{id}/dishes` return restaurant profiles and their database-linked menu.
- `GET /api/custom-builder/options` returns priced builder ingredients; `POST /api/cart/add-custom` validates combinations and resolves prices on the server before the item enters the browser cart.
- `POST /api/orders` places an order; `GET /api/orders/{orderId}/track` returns its progress, assigned driver, and latest coordinates. The client polls every three seconds. Existing `/api/v1` endpoints and the WebSocket tracker remain available for compatibility.

Online UPI/card/net-banking payments are recorded as pending until a real payment provider calls the signed webhook. Driver status and coordinates in the local seeded/demo application are generated by the backend tracking state machine; production dispatch should replace that simulator with the delivery provider's verified webhook or GPS feed. Use managed database migrations before deploying schema changes to an existing production database.

## India Checkout & Accounts

- The app displays and stores prices in INR. Existing USD seed prices are converted once using the fixed `USD_TO_INR = 83.0` value in `app/pricing.py`; adjust that constant before reseeding if a different menu conversion is needed.
- Set `APP_SECRET_KEY` to a long random value in production. The development fallback is not suitable for deployment.
- Signup grants 500 demo wallet tokens. Premium costs 499 tokens for 30 days; it provides free standard delivery, queue priority, and 10% off token payments.
- UPI/card/net-banking checkout records payment as `pending`. A real gateway is not bundled. Configure the provider to call `POST /api/v1/account/payments/webhook` after setting `PAYMENT_WEBHOOK_SECRET`.
- The webhook expects an `X-Payment-Signature` header containing HMAC-SHA256 of the normalized, compact JSON request body. Verified `paid` events settle wallet top-ups or release online orders to the kitchen; duplicate callbacks are idempotent.
- `/api/v1/account/tokens/top-up` creates a pending transaction and never credits tokens by itself.
