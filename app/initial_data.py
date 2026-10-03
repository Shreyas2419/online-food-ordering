"""
Initial seed data with rich allergen metadata, ingredients, and customizer schemas.
"""
import json
import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from app.food_photos import DISH_PHOTO_OVERRIDES, PEXELS_FOOD_PHOTO_IDS, pexels_food_photo_url


RESTAURANT_PROFILES = [
    ("restaurant-zero-g", "Faura Royal Rasoi", ["North Indian", "Awadhi", "Mughlai"], "Royal dum biryanis, slow-cooked makhani gravies, and tandoor-charred kebabs.", 4.9, 25, "1540420773420-3366772f4999"),
    ("restaurant-fire-bowl", "Forno Rosso Continental", ["Continental", "Pasta", "Steak"], "Handmade artisan pastas, dry-aged flame steaks, and slow-baked cannelloni.", 4.8, 30, "1513104890138-7c749659a591"),
    ("restaurant-mexican", "Dakshin Coastal Lounge", ["South Indian", "Chettinad", "Malabar"], "Freshly ground pepper roasts, lacy appams, and coastal coconut seafood curries.", 4.9, 28, "1552332386-f8dd00dc2f85"),
    ("restaurant-indian", "Saffron Route Haveli", ["North Indian", "Punjabi", "Tandoor"], "Stone-ground heritage spices, hand-stretched kulchas, and Bukhara dal makhani.", 4.8, 32, "1565557623262-b51c2513a641"),
    ("restaurant-american", "Bengal Bay & Beyond", ["East Indian", "Bengali", "Bihari"], "Royal Kolkata biryani, kosha mangsho, litti chokha, and authentic mishti doi.", 4.7, 30, "1568901346375-23c9450c58cd"),
    ("restaurant-mediterranean", "Western Ghats Bistro", ["West Indian", "Goan", "Maharashtrian"], "Fiery prawn balchão, buttery pav bhaji, dal baati churma, and malvani curries.", 4.8, 26, "1547592180-85f173990554"),
    ("restaurant-thai", "Chai & Chaat Court", ["Street Food", "Snacks", "Mithai"], "Crisp kachoris, live chaat counters, steaming masala chai, and artisanal Indian sweets.", 4.7, 20, "1559847844-5315695dadae"),
]

PREMIUM_DISH_IDS = {"dish-bowl-03", "dish-pizza-02", "featured-chirashi", "featured-unagi"}
FEATURED_IMAGE_PATHS = {
    dish_id: f"/static/assets/{dish_id}.png"
    for dish_id in (
        "featured-salmon-poke", "featured-tuna-sashimi", "featured-crispy-tofu",
        "featured-unagi", "featured-chirashi", "featured-chicken-katsu",
        "featured-garden-quinoa", "featured-prawn-soba", "featured-miso-mushroom",
        "featured-jammy-egg",
    )
}


def unique_dish_image_url(image_url: str, dish_id: str) -> str:
    """Retain the curated Unsplash source while making each catalog URL stable and unique."""
    parts = urlsplit(image_url)
    query = dict(parse_qsl(parts.query))
    query["dish"] = dish_id
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

DISHES_SEED = [
    {
        "id": "dish-bowl-01",
        "name": "Old Delhi Murgh Makhani Rice Bowl",
        "slug": "old-delhi-murgh-makhani-bowl",
        "category": "bowls",
        "description": "Slow-simmered tender chicken pieces in velvety tomato-cashew makhani gravy over fragrant aged basmati rice, scented with kasoori methi, ginger juliennes, and white butter.",
        "base_price": 14.50,
        "calories": 580,
        "protein_g": 28,
        "prep_time_mins": 10,
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&auto=format&fit=crop&q=80",
        "allergens": ["dairy"],
        "ingredients": ["Tender Chicken", "Aged Basmati Rice", "Makhani Gravy", "Kasoori Methi", "White Butter", "Ginger Juliennes"],
        "customizable": True,
        "is_popular": True,
        "rating": 4.95,
        "review_count": 284,
        "customization_schema": [
            {
                "step_id": "base",
                "title": "1. Select Heritage Grain Base",
                "description": "Choose your primary foundation",
                "min_select": 1,
                "max_select": 1,
                "options": [
                    {"id": "base-quinoa", "name": "Aged Basmati Jeera Rice (Gluten-Free)", "price": 0.0, "calories": 160, "allergens": []},
                    {"id": "base-cauli", "name": "Kashmiri Zafrani Saffron Pulao", "price": 1.0, "calories": 180, "allergens": []},
                    {"id": "base-wild-rice", "name": "Foxtail Millet Pilaf (Healthy Grain)", "price": 1.5, "calories": 140, "allergens": []}
                ]
            },
            {
                "step_id": "protein",
                "title": "2. Select Regional Indian Protein",
                "description": "Power-packed protein selection",
                "min_select": 1,
                "max_select": 1,
                "options": [
                    {"id": "prot-tofu", "name": "Charred Malai Paneer Tikka", "price": 0.0, "calories": 190, "allergens": ["dairy"]},
                    {"id": "prot-chicken", "name": "Old Delhi Tandoori Murgh", "price": 3.0, "calories": 210, "allergens": []},
                    {"id": "prot-salmon", "name": "Malabar Coastal Spiced Fish", "price": 4.5, "calories": 220, "allergens": ["fish"]},
                    {"id": "prot-chickpea", "name": "Amritsari Pindi Chole (Vegan)", "price": 0.0, "calories": 150, "allergens": []}
                ]
            },
            {
                "step_id": "crunch",
                "title": "3. Accompaniments & Crunch",
                "description": "Select artisanal regional accents",
                "min_select": 1,
                "max_select": 3,
                "options": [
                    {"id": "top-peanuts", "name": "Spiced Roasted Peanuts with Chaat Masala", "price": 0.0, "calories": 90, "allergens": ["peanuts"]},
                    {"id": "top-sunflower", "name": "Toasted Pumpkin & Flax Crunch (Peanut-Free)", "price": 0.0, "calories": 85, "allergens": [], "is_safe_swap": True, "swap_for": "peanuts"},
                    {"id": "top-edamame", "name": "Kachumber Salad (Cucumber, Onion, Tomato)", "price": 0.5, "calories": 30, "allergens": []},
                    {"id": "top-cucumbers", "name": "Pickled Sirka Shallots & Green Chili", "price": 0.0, "calories": 20, "allergens": []},
                    {"id": "top-avocado", "name": "Crispy Crushed Papad & Boondi", "price": 1.0, "calories": 75, "allergens": []}
                ]
            },
            {
                "step_id": "dressing",
                "title": "4. Royal Gravy & Chutney",
                "description": "Infuse rich depth & aroma",
                "min_select": 1,
                "max_select": 1,
                "options": [
                    {"id": "dr-lime-ginger", "name": "Velvety Makhani Gravy (Dairy)", "price": 0.0, "calories": 80, "allergens": ["dairy"]},
                    {"id": "dr-tahini-lemon", "name": "Spicy Chettinad Pepper Curry (Dairy-Free)", "price": 0.0, "calories": 70, "allergens": [], "is_safe_swap": True, "swap_for": "dairy"},
                    {"id": "dr-sriracha-mayo", "name": "Tangy Mint & Anardana Chutney", "price": 0.5, "calories": 40, "allergens": []}
                ]
            }
        ]
    },
    {
        "id": "dish-bowl-02",
        "name": "Malabar Coastal Prawn & Coconut Curry Bowl",
        "slug": "malabar-coastal-prawn-curry-bowl",
        "category": "bowls",
        "description": "Wild-caught coastal tiger prawns simmered in freshly pressed coconut milk, tangy kokum, curry leaves, and green chilies over steaming red matta rice.",
        "base_price": 16.50,
        "calories": 520,
        "protein_g": 34,
        "prep_time_mins": 11,
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&auto=format&fit=crop&q=80",
        "allergens": ["shellfish"],
        "ingredients": ["Coastal Tiger Prawns", "Fresh Coconut Milk", "Kokum", "Curry Leaves", "Kerala Matta Rice", "Mustard Tempering"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.91,
        "review_count": 192
    },
    {
        "id": "dish-bowl-03",
        "name": "Kashmiri Wazwan Gosht Rogan Josh Bowl",
        "slug": "kashmiri-wazwan-gosht-rogan-josh",
        "category": "bowls",
        "description": "Tender mountain lamb shanks slow-braised in authentic Kashmiri ratanjot, mawal flower extract, saffron, and fennel-scented gravy over royal basmati.",
        "base_price": 22.00,
        "calories": 740,
        "protein_g": 42,
        "prep_time_mins": 14,
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&auto=format&fit=crop&q=80",
        "allergens": ["dairy"],
        "ingredients": ["Prime Lamb Shanks", "Aged Basmati Rice", "Ratanjot Bark", "Kashmiri Deggi Mirch", "Fennel Powder", "Desi Ghee"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.95,
        "review_count": 142
    },
    {
        "id": "dish-pizza-01",
        "name": "Amritsari Paneer Tikka Tandoori Naan-Za",
        "slug": "amritsari-paneer-tikka-naan-za",
        "category": "pizzas",
        "description": "Clay-oven baked leavened naan crust topped with rich makhani sauce, char-grilled malai paneer cubes, roasted bell peppers, and melted mozzarella.",
        "base_price": 15.00,
        "calories": 680,
        "protein_g": 26,
        "prep_time_mins": 12,
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&auto=format&fit=crop&q=80",
        "allergens": ["gluten", "dairy"],
        "ingredients": ["Tandoori Naan Crust", "Makhani Sauce", "Malai Paneer", "Mozzarella", "Bell Peppers", "Kasoori Methi"],
        "customizable": True,
        "is_popular": True,
        "rating": 4.96,
        "review_count": 430,
        "customization_schema": [
            {
                "step_id": "crust",
                "title": "1. Choose Tandoori Crust",
                "description": "Hand-stretched artisan tandoori bread",
                "min_select": 1,
                "max_select": 1,
                "options": [
                    {"id": "crust-sourdough", "name": "Butter Garlic Naan Crust (Contains Gluten)", "price": 0.0, "calories": 420, "allergens": ["gluten"]},
                    {"id": "crust-cauli-gf", "name": "Gluten-Free Crisp Millet Flatbread", "price": 2.50, "calories": 280, "allergens": [], "is_safe_swap": True, "swap_for": "gluten"}
                ]
            },
            {
                "step_id": "cheese",
                "title": "2. Select Paneer & Melt",
                "description": "Artisan dairy or Plant-Based",
                "min_select": 1,
                "max_select": 1,
                "options": [
                    {"id": "cheese-mozzarella", "name": "Fresh Buffalo Mozzarella & Paneer (Dairy)", "price": 0.0, "calories": 220, "allergens": ["dairy"]},
                    {"id": "cheese-cashew-melt", "name": "Cultured Cashew Silk Mozzarella (Dairy-Free)", "price": 2.00, "calories": 160, "allergens": [], "is_safe_swap": True, "swap_for": "dairy"}
                ]
            },
            {
                "step_id": "toppings",
                "title": "3. Finishing Spices & Herbs",
                "description": "Select up to 3 regional accents",
                "min_select": 0,
                "max_select": 3,
                "options": [
                    {"id": "top-basil", "name": "Fresh Coriander & Kasoori Methi", "price": 0.0, "calories": 5, "allergens": []},
                    {"id": "top-hot-honey", "name": "Mathania Chili Spiced Honey Glaze", "price": 1.5, "calories": 60, "allergens": []},
                    {"id": "top-mushrooms", "name": "Tandoori Roasted Button Mushrooms", "price": 2.0, "calories": 45, "allergens": []}
                ]
            }
        ]
    },
    {
        "id": "dish-pizza-02",
        "name": "Awadhi Spiced Lamb & Burrata Flatbread",
        "slug": "awadhi-spiced-lamb-burrata-flatbread",
        "category": "pizzas",
        "description": "Crisp tandoori-baked flatbread topped with slow-braised Awadhi spiced lamb mince, fresh creamy burrata, pomegranate pearls, and fresh mint chutney.",
        "base_price": 17.50,
        "calories": 820,
        "protein_g": 36,
        "prep_time_mins": 13,
        "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800&auto=format&fit=crop&q=80",
        "allergens": ["gluten", "dairy"],
        "ingredients": ["Crisp Flatbread", "Spiced Lamb Mince", "Fresh Burrata", "Pomegranate Pearls", "Mint Chutney", "Pickled Onions"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.97,
        "review_count": 218
    },
    {
        "id": "dish-burger-01",
        "name": "Mumbai Kolhapuri Spiced Mutton Pav Slider",
        "slug": "mumbai-kolhapuri-mutton-pav-slider",
        "category": "burgers",
        "description": "Slow-braised spiced tender mutton patty infused with roasted Kolhapuri spices, pickled shallots, and garlic thecha chutney in warm buttered pav.",
        "base_price": 16.00,
        "calories": 760,
        "protein_g": 38,
        "prep_time_mins": 11,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&auto=format&fit=crop&q=80",
        "allergens": ["gluten", "dairy"],
        "ingredients": ["Spiced Mutton Patty", "Buttered Pav (Gluten)", "Garlic Thecha", "Pickled Shallots", "Amul Butter"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.98,
        "review_count": 512
    },
    {
        "id": "dish-burger-02",
        "name": "Amritsari Crispy Paneer Tikka Bun",
        "slug": "amritsari-crispy-paneer-tikka-bun",
        "category": "burgers",
        "description": "Crispy panko-coated malai paneer steak, crunchy laccha onion slaw, mint chutney aioli, served on a toasted sesame brioche bun.",
        "base_price": 14.50,
        "calories": 610,
        "protein_g": 24,
        "prep_time_mins": 10,
        "image_url": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=800&auto=format&fit=crop&q=80",
        "allergens": ["dairy", "gluten", "sesame"],
        "ingredients": ["Crispy Paneer Patty", "Sesame Brioche Bun", "Laccha Onions", "Mint Aioli", "Chaat Masala"],
        "customizable": False,
        "is_popular": False,
        "rating": 4.89,
        "review_count": 96
    },
    {
        "id": "dish-burger-03",
        "name": "Bihari Charred Sattu & Beetroot Vegan Tikki",
        "slug": "bihari-charred-sattu-beetroot-tikki",
        "category": "burgers",
        "description": "Gluten-free roasted gram flour sattu and ruby beetroot cutlet, avocado mash, amchur chutney, and roasted cumin in a crisp lettuce wrap.",
        "base_price": 13.50,
        "calories": 440,
        "protein_g": 18,
        "prep_time_mins": 9,
        "image_url": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800&auto=format&fit=crop&q=80",
        "allergens": [],
        "ingredients": ["Roasted Sattu & Beetroot Patty", "Avocado Mash", "Amchur Chutney", "Iceberg Lettuce Wrap", "Roasted Cumin"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.90,
        "review_count": 144
    },
    {
        "id": "dish-side-01",
        "name": "Amritsari Kurkuri Bhindi & Sweet Potato Crisps",
        "slug": "amritsari-kurkuri-bhindi-crisps",
        "category": "sides",
        "description": "Extra crisp spiced okra fries and sweet potato wedges dusted in chatpata amchur, ajwain, and rock salt, served with tangy mint chutney.",
        "base_price": 6.50,
        "calories": 320,
        "protein_g": 6,
        "prep_time_mins": 7,
        "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=800&auto=format&fit=crop&q=80",
        "allergens": [],
        "ingredients": ["Crispy Okra", "Sweet Potato Wedges", "Amchur", "Ajwain Carom Seeds", "Mint Chutney"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.94,
        "review_count": 310
    },
    {
        "id": "dish-side-02",
        "name": "Koliwada Crispy Pomfret & Calamari Bites",
        "slug": "koliwada-crispy-pomfret-calamari",
        "category": "sides",
        "description": "Fresh coastal seafood marinated in ginger, garlic, carom seeds, and Byadgi chili, flash-fried in crisp gram flour coating with lemon wedges.",
        "base_price": 11.50,
        "calories": 420,
        "protein_g": 28,
        "prep_time_mins": 9,
        "image_url": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=800&auto=format&fit=crop&q=80",
        "allergens": ["shellfish", "fish"],
        "ingredients": ["Fresh Pomfret & Squid", "Gram Flour Batter", "Byadgi Chili Paste", "Carom Seeds", "Tamarind Chutney"],
        "customizable": False,
        "is_popular": False,
        "rating": 4.89,
        "review_count": 89
    },
    {
        "id": "dish-side-03",
        "name": "Dhabha Tandoori Charred Corn & Edamame Chaat",
        "slug": "dhabha-tandoori-charred-corn-chaat",
        "category": "sides",
        "description": "Sweet yellow corn and green edamame blistered in clay oven, tossed with fresh lime juice, chaat masala, pomegranate seeds, and fresh mint.",
        "base_price": 7.00,
        "calories": 190,
        "protein_g": 12,
        "prep_time_mins": 6,
        "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=800&auto=format&fit=crop&q=80",
        "allergens": ["soy"],
        "ingredients": ["Sweet Corn", "Edamame (Soy)", "Pomegranate Pearls", "Chaat Masala", "Fresh Mint"],
        "customizable": False,
        "is_popular": False,
        "rating": 4.82,
        "review_count": 64
    },
    {
        "id": "dish-drink-01",
        "name": "Kesariya Badam Saffron Royal Thandai",
        "slug": "kesariya-badam-saffron-thandai",
        "category": "drinks",
        "description": "Chilled almond milk infused with Kashmiri saffron threads, crushed green cardamom, fennel seeds, and toasted pistachio flakes.",
        "base_price": 6.50,
        "calories": 160,
        "protein_g": 6,
        "prep_time_mins": 4,
        "image_url": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=800&auto=format&fit=crop&q=80",
        "allergens": ["dairy"],
        "ingredients": ["Almond Milk", "Kashmiri Saffron", "Cardamom", "Fennel Seeds", "Pistachio Flakes"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.97,
        "review_count": 420
    },
    {
        "id": "dish-drink-02",
        "name": "Alphonso Mango & Cardamom Royal Lassi",
        "slug": "alphonso-mango-cardamom-lassi",
        "category": "drinks",
        "description": "Hand-churned thick curd whipped with sweet Ratnagiri Alphonso mango pulp, green cardamom, and a drizzle of organic wild honey.",
        "base_price": 5.50,
        "calories": 180,
        "protein_g": 7,
        "prep_time_mins": 3,
        "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=800&auto=format&fit=crop&q=80",
        "allergens": ["dairy"],
        "ingredients": ["Cultured Curd (Dairy)", "Alphonso Mango Pulp", "Green Cardamom", "Wild Honey"],
        "customizable": False,
        "is_popular": True,
        "rating": 4.95,
        "review_count": 215
    },
    {
        "id": "dish-build-meal",
        "name": "Faura Royal Build-Your-Own Indian Feast Bowl",
        "slug": "faura-build-your-own-indian-feast",
        "category": "build-your-own",
        "description": "Custom royal Indian feast: select your heritage grain base, regional protein, crispy accompaniments, and aromatic gravy.",
        "base_price": 0.95,
        "calories": 0,
        "protein_g": 0,
        "prep_time_mins": 15,
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&auto=format&fit=crop&q=80",
        "allergens": [],
        "ingredients": ["Basmati Rice", "Roti", "Saffron Pulao", "Paneer", "Murgh", "Accompaniments", "Royal Gravy"],
        "customizable": True,
        "is_popular": True,
        "rating": 4.9,
        "review_count": 1,
        "customization_schema": [
            {"step_id": "base", "title": "1. Choose your base", "description": "Start with grains or breads", "min_select": 1, "max_select": 1, "options": [
                {"id": "base-rice", "name": "Steamed basmati rice", "price": 0, "calories": 210, "allergens": []},
                {"id": "base-roti", "name": "Whole-wheat butter roti", "price": 0.36, "calories": 170, "allergens": ["gluten"]},
                {"id": "base-quinoa", "name": "Kashmiri saffron pulao", "price": 1.2, "calories": 185, "allergens": []},
                {"id": "base-greens", "name": "Fresh market greens", "price": 0.24, "calories": 45, "allergens": []}
            ]},
            {"step_id": "protein", "title": "2. Choose a protein", "description": "One regional Indian protein", "min_select": 0, "max_select": 1, "options": [
                {"id": "protein-paneer", "name": "Malai paneer tikka", "price": 1.2, "calories": 240, "allergens": ["dairy"]},
                {"id": "protein-tofu", "name": "Tandoori smoked tofu", "price": 1, "calories": 180, "allergens": ["soy"]},
                {"id": "protein-chicken", "name": "Old Delhi tandoori chicken", "price": 1.7, "calories": 230, "allergens": []},
                {"id": "protein-eggs", "name": "Two boiled spiced eggs", "price": 0.6, "calories": 140, "allergens": ["eggs"]},
                {"id": "protein-beans", "name": "Amritsari pindi chole", "price": 0.8, "calories": 160, "allergens": []}
            ]},
            {"step_id": "mixins", "title": "3. Add vegetables & mix-ins", "description": "Choose up to four", "min_select": 0, "max_select": 4, "options": [
                {"id": "mix-avocado", "name": "Kachumber salad", "price": 0.45, "calories": 80, "allergens": []},
                {"id": "mix-cucumber", "name": "Pickled sirka onions", "price": 0.2, "calories": 18, "allergens": []},
                {"id": "mix-pickles", "name": "Crispy papad churi", "price": 0.25, "calories": 30, "allergens": []},
                {"id": "mix-edamame", "name": "Boondi raita mix", "price": 0.35, "calories": 90, "allergens": ["dairy"]},
                {"id": "mix-sesame", "name": "Toasted cumin crunch", "price": 0.15, "calories": 55, "allergens": []}
            ]},
            {"step_id": "dressing", "title": "4. Finish with a gravy", "description": "Choose one", "min_select": 0, "max_select": 1, "options": [
                {"id": "sauce-yuzu", "name": "Velvety makhani gravy", "price": 0.2, "calories": 35, "allergens": ["dairy"]},
                {"id": "sauce-tahini", "name": "Chettinad pepper curry", "price": 0.3, "calories": 90, "allergens": []},
                {"id": "sauce-chili", "name": "Mint anardana chutney", "price": 0.25, "calories": 65, "allergens": []}
            ]}
        ]
    },
    {
        "id": "dish-egg-01",
        "name": "Kolkata Royal Egg Masala & Flaky Parotta Box",
        "slug": "kolkata-royal-egg-masala-parotta",
        "category": "bowls",
        "description": "Two golden browned farm eggs simmered in rich caramelized onion, ginger, and panch phoron gravy, served with hand-rolled flaky layered parottas.",
        "base_price": 13.50,
        "calories": 510,
        "protein_g": 22,
        "prep_time_mins": 11,
        "image_url": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=800&auto=format&fit=crop&q=80",
        "allergens": ["eggs", "gluten"],
        "ingredients": ["Browned Farm Eggs", "Flaky Parotta (Gluten)", "Kolkata Gravy", "Panch Phoron", "Green Chilies"],
        "customizable": False,
        "is_popular": False,
        "rating": 4.88,
        "review_count": 1
    }
]

FEATURED_DISHES = [
    {"id": "featured-salmon-poke", "name": "Coastal Malabar Spiced Salmon Platter", "slug": "coastal-malabar-salmon", "category": "bowls", "base_price": 18.5, "description": "Pan-roasted Atlantic salmon steeped in Malabar spices, basmati rice, Hass avocado, and fresh tempered coconut chutney.", "calories": 540, "image_url": "/static/assets/poke_bowl_transparent.png", "allergens": ["fish"], "ingredients": ["Salmon", "Rice", "Avocado", "Coconut"], "dietary_type": "non-veg"},
    {"id": "featured-tuna-sashimi", "name": "Amritsari Tandoori King Fish Tikka", "slug": "amritsari-tandoori-king-fish", "category": "bowls", "base_price": 19.5, "description": "Fresh king fish steaks marinated in roasted carom seeds, Kashmiri chili, hung curd, and mustard oil, charred in clay oven.", "calories": 520, "image_url": "/static/assets/tuna_poke_transparent.png", "allergens": ["fish", "dairy"], "ingredients": ["King Fish", "Rice", "Mustard Oil", "Mint"], "dietary_type": "non-veg"},
    {"id": "featured-crispy-tofu", "name": "Shahi Malai Paneer Angara", "slug": "shahi-malai-paneer-angara", "category": "bowls", "base_price": 15.5, "description": "Organic cottage cheese cubes layered with smoked spices, roasted bell peppers, fresh mint chutney, and saffron cream.", "calories": 480, "image_url": "/static/assets/tofu_poke_transparent.png", "allergens": ["dairy"], "ingredients": ["Malai Paneer", "Saffron Cream", "Bell Peppers", "Mint"], "dietary_type": "veg"},
    {"id": "featured-unagi", "name": "Bengali Smoked Bhetki Paturi", "slug": "bengali-smoked-bhetki-paturi", "category": "bowls", "base_price": 22.0, "description": "Tender bhetki fish fillet coated with fresh stone-ground mustard paste, wrapped in tender banana leaves and slow-smoked.", "calories": 610, "image_url": "/static/assets/unagi_poke_transparent.png", "allergens": ["fish"], "ingredients": ["Bhetki Fish", "Rice", "Mustard Paste", "Banana Leaf"], "dietary_type": "non-veg"},
    {"id": "featured-chirashi", "name": "Royal Hyderabadi Zafrani Gosht Thali", "slug": "royal-hyderabadi-zafrani-gosht", "category": "bowls", "base_price": 26.0, "description": "Fragrant kachchi yakhni dum biryani served with mirchi ka salan, burani raita, and slow-cooked tender mutton shanks.", "calories": 590, "image_url": "/static/assets/chirashi_poke_transparent.png", "allergens": ["dairy", "eggs"], "ingredients": ["Mutton", "Basmati Rice", "Mirchi Salan", "Burani Raita", "Egg"], "dietary_type": "non-veg"},
    {"id": "featured-chicken-katsu", "name": "Lucknowi Murgh Reshmi Kebab Platter", "slug": "lucknowi-murgh-reshmi-kebab", "category": "bowls", "base_price": 18.5, "description": "Melt-in-mouth chicken supreme marinated in cashew paste, cream, and mace, accompanied by flaky warqi parotta and mint dip.", "calories": 680, "image_url": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=900&auto=format&fit=crop&q=85", "allergens": ["dairy", "gluten"], "ingredients": ["Chicken", "Warqi Parotta", "Cashew Cream", "Mint Dip"], "dietary_type": "non-veg"},
    {"id": "featured-garden-quinoa", "name": "Kashmiri Zafrani Subz Pulao", "slug": "kashmiri-zafrani-subz-pulao", "category": "bowls", "base_price": 16.5, "description": "Royal saffron basmati rice tossed with garden sweet peas, morel mushrooms, dried cranberries, and toasted walnuts.", "calories": 510, "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=900&auto=format&fit=crop&q=85", "allergens": [], "ingredients": ["Saffron Rice", "Morel Mushrooms", "Green Peas", "Walnuts"], "dietary_type": "vegan"},
    {"id": "featured-prawn-soba", "name": "Mangalorean Ghee Roast Prawns", "slug": "mangalorean-ghee-roast-prawns", "category": "bowls", "base_price": 21.0, "description": "Jumbo coastal prawns tossed in fiery Byadgi chili paste, roasted cumin, and fragrant desi ghee with soft neer dosa.", "calories": 560, "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=900&auto=format&fit=crop&q=85", "allergens": ["shellfish", "dairy"], "ingredients": ["Tiger Prawns", "Byadgi Chili Paste", "Desi Ghee", "Neer Dosa"], "dietary_type": "non-veg"},
    {"id": "featured-miso-mushroom", "name": "Awadhi Dhingri Dolma (Charred Morels)", "slug": "awadhi-dhingri-dolma-morels", "category": "bowls", "base_price": 15.0, "description": "Wild Himalayan morels stuffed with spiced paneer and nuts, simmered in a silky almond-cardamom brown onion gravy.", "calories": 530, "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=900&auto=format&fit=crop&q=85", "allergens": ["dairy"], "ingredients": ["Morel Mushrooms", "Spiced Paneer", "Almond Gravy", "Cardamom"], "dietary_type": "veg"},
    {"id": "featured-jammy-egg", "name": "Dhabha Double Egg Curry with Jeera Rice", "slug": "dhabha-double-egg-curry", "category": "bowls", "base_price": 13.5, "description": "Crisp-edged browned farm eggs simmered in rustic roadside dhabha gravy with roasted cloves and cumin basmati.", "calories": 490, "image_url": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=900&auto=format&fit=crop&q=85", "allergens": ["eggs"], "ingredients": ["Farm Eggs", "Jeera Rice", "Dhabha Gravy", "Pickled Onions"], "dietary_type": "egg"},
]

FOOD_PHOTO_IDS = {
    "veg": ["1546069901-ba9599a7e63c", "1512621776951-a57141f2eefd", "1520072959219-c595dc870360", "1586190848861-99aa4a171e90"],
    "non-veg": ["1540420773420-3366772f4999", "1579871494447-9811cf80d66c", "1617196034796-73dfa7b1fd56", "1599488615731-7e5c2823ff28", "1604908176997-125f25cc6f3d", "1569718212165-3a8278d5f624"],
    "egg": ["1516684732162-798a0062be99", "1546069901-ba9599a7e63c", "1512621776951-a57141f2eefd"],
    "vegan": ["1512621776951-a57141f2eefd", "1546069901-ba9599a7e63c", "1520072959219-c595dc870360", "1586190848861-99aa4a171e90"],
}


def food_photo_url(dietary_type: str, sequence: int) -> str:
    photos = FOOD_PHOTO_IDS.get(dietary_type, FOOD_PHOTO_IDS["veg"])
    photo_id = photos[(sequence - 1) % len(photos)]
    return f"https://images.unsplash.com/photo-{photo_id}?w=800&auto=format&fit=crop&q=80"


def infer_dietary_type(text: str) -> str:
    normalized = text.lower()
    if any(term in normalized for term in (
        "chicken", "salmon", "tuna", "sashimi", "unagi", "wagyu", "prawn", "crab",
        "seafood", "calamari", "pepperoni", "beef", "pork", "shrimp", "anchovy",
    )):
        return "non-veg"
    if any(term in normalized for term in ("egg", "tamagoyaki")):
        return "egg"
    if any(term in normalized for term in ("tofu", "vegan", "plant-based", "plant based")) and not any(
        term in normalized for term in ("dairy", "cheese", "egg", "honey", "butter")
    ):
        return "vegan"
    return "veg"


def generated_dietary_dish(dietary_type: str, sequence: int) -> dict:
    proteins = {
        "veg": [
            ("Malai Paneer Tikka", ["dairy"], "Hand-cut malai paneer steeped in yellow chili, ajwain, and saffron yogurt"),
            ("Amritsari Pindi Chole", [], "Dark spiced chickpeas slow-simmered with dried anardana and black cardamom"),
            ("Charred Morel Mushrooms", [], "Wild Himalayan morels filled with spiced cottage cheese and toasted pine nuts"),
            ("Kashmiri Dum Aloo", ["dairy"], "Baby potatoes simmered in stone-ground fennel, dry ginger, and slow-whisked yogurt"),
            ("Crispy Palak Kofta", [], "Crisp fenugreek and spinach dumplings nestled in silky cashew-tomato gravy"),
        ],
        "non-veg": [
            ("Old Delhi Murgh Tikka", ["dairy"], "Tender chicken fillets basted with cold-pressed mustard oil, mace, and roasted gram flour"),
            ("Malabar Coastal Fish", ["fish"], "Fresh catch of seer fish stewed in fresh coconut milk, green chilies, and sour kokum"),
            ("Kashmiri Mutton Rogan Josh", [], "Slow-braised mountain mutton infused with ratanjot bark and aromatic wazwan spices"),
            ("Mangalorean Ghee Roast Prawns", ["shellfish", "dairy"], "Wild tiger prawns pan-tossed in fiery Byadgi chili paste, roasted coriander, and desi ghee"),
            ("Chettinad Country Chicken", [], "Free-range chicken dry-roasted with black peppercorns, star anise, and fresh curry leaves"),
        ],
        "egg": [
            ("Kolkata Street Egg Masala", ["eggs"], "Hard-boiled eggs browned in turmeric oil, simmered in thick onion-tomato gravy with kalonji"),
            ("Parsi Akuri Scramble", ["eggs"], "Soft, velvety scrambled eggs gently spiced with ginger, green chilies, and fresh coriander"),
            ("Malabar Spiced Egg Roast", ["eggs"], "Caramelized shallot and crushed pepper roasted eggs served with coconut gravy"),
            ("Dhabha Double Egg Curry", ["eggs"], "Golden fried eggs bathed in a robust roadside dhabha gravy with roasted cloves"),
            ("Chettinad Boiled Egg Sukka", ["eggs"], "Boiled eggs tossed in dry-roasted southern spices, shredded coconut, and mustard seeds"),
        ],
        "vegan": [
            ("Tandoori Soya Chaap", ["soy"], "Smoked plant-based soya skewers marinated in spiced mustard oil, lemon, and kasoori methi"),
            ("Rajasthani Gatte Ke Saag", [], "Steamed spiced gram-flour dumplings stewed in tangy kokum and roasted cumin broth"),
            ("Kathal (Raw Jackfruit) Dum", [], "Tender raw baby jackfruit braised like pulled meat with whole cloves, cinnamon, and onions"),
            ("Tadkewali Panchmel Dal", [], "Five royal lentils tempered with cumin, asafoetida, dried red chilies, and fresh ginger"),
            ("Bihari Baingan Bharta", [], "Clay-oven charred smoked aubergine mashed with raw mustard oil, garlic, and green chilies"),
        ],
    }
    styles = [
        "Amritsari Royal", "Kashmiri Zafrani", "Chettinad Spiced", "Malabar Coastal",
        "Awadhi Shahi Dum", "Kolkata Panch Phoron", "Goan Balchão", "Rajasthani Mathania",
        "Hyderabadi Nizami", "Kolhapuri Lavangi",
    ]
    bases = [
        "Aged Basmati Jeera Rice", "Saffron Pulao", "Hyderabadi Biryani Rice", "Amritsari Butter Kulcha",
        "Kerala Malabar Parotta", "Steamed Basmati Rice", "Foxtail Millet Upma", "Tandoori Wholewheat Roti",
        "Lemon Turmeric Rice", "Brown Basmati Pilaf",
    ]
    allergens = {"soy", "sesame", "gluten", "dairy", "eggs", "fish", "shellfish", "peanuts"}
    index = sequence - 1
    protein, protein_allergens, ingredient = proteins[dietary_type][index // len(styles)]
    style = styles[index % len(styles)]
    base = bases[(index * 3 + sequence // len(styles)) % len(bases)]
    dish_id = f"generated-{dietary_type}-{sequence:03d}"
    name = f"{style} {protein} with {base}"
    dish_allergens = set(protein_allergens)
    if "Sesame" in base or "Sesame" in style:
        dish_allergens.add("sesame")
    if "Kulcha" in base or "Parotta" in base or "Roti" in base:
        dish_allergens.add("gluten")
    if "Butter" in base or "Ghee" in style:
        if dietary_type != "vegan":
            dish_allergens.add("dairy")
    return {
        "id": dish_id,
        "name": name,
        "slug": f"{dish_id}-regional-feast",
        "category": "bowls",
        "dietary_type": dietary_type,
        "restaurant_id": "restaurant-zero-g" if sequence % 2 else "restaurant-fire-bowl",
        "description": f"{ingredient}, served alongside {base.lower()} and garnished with fresh coriander, ginger juliennes, and artisanal regional tempering.",
        "base_price": round(10.5 + (sequence % 10) * 0.65, 2),
        "calories": 420 + (sequence * 37) % 370,
        "protein_g": 14 + (sequence * 5) % 31,
        "prep_time_mins": 9 + sequence % 8,
        "image_url": food_photo_url(dietary_type, sequence),
        "allergens": sorted(dish_allergens & allergens),
        "ingredients": [ingredient, base, f"{style} gravy & vegetables", "Artisanal tempering"],
        "customizable": False,
        "is_popular": sequence % 10 == 0,
        "rating": round(4.3 + (sequence % 8) * 0.1, 1),
        "review_count": 18 + sequence * 7,
    }


TABLES_SEED = [
    {
        "id": "tbl-vip-01",
        "name": "Skyline Window Booth A1 (Panoramic)",
        "table_type": "window_seat",
        "capacity": 4,
        "is_premium": True,
        "reservation_fee": 500.0,
        "location_tag": "Floor 42 · Panoramic Sunset Skyline",
        "description": "Premium floor-to-ceiling curved window booth overlooking the city skyline. Ideal for romantic dinners or celebrations.",
        "features": ["Floor-to-ceiling skyline views", "Complimentary chef welcome amuses", "Dedicated private sommelier service"],
    },
    {
        "id": "tbl-vip-02",
        "name": "Chef's Omakase Counter C1",
        "table_type": "chefs_counter",
        "capacity": 2,
        "is_premium": True,
        "reservation_fee": 1000.0,
        "location_tag": "Main Kitchen Pass · Front Row",
        "description": "Exclusive front-row seats directly facing the master executive chef pass. Experience multi-course plating live.",
        "features": ["Direct interactive chef dining", "Behind-the-scenes plating presentation", "Curated sake/wine pairings included"],
    },
    {
        "id": "tbl-vip-03",
        "name": "Starlight Private Dining Suite #7",
        "table_type": "vip_booth",
        "capacity": 6,
        "is_premium": True,
        "reservation_fee": 1500.0,
        "location_tag": "Private Mezzanine Wing",
        "description": "Enclosed velvet acoustic booth designed for high-profile gatherings and intimate VIP dinners.",
        "features": ["Acoustic isolation & ambient lighting controls", "Exclusive private server", "Custom menu monogramming"],
    },
    {
        "id": "tbl-vip-04",
        "name": "Skyline Window Terrace Table T4",
        "table_type": "terrace_skyline",
        "capacity": 4,
        "is_premium": True,
        "reservation_fee": 500.0,
        "location_tag": "Open-Air Sky Terrace",
        "description": "Breezy open-air terrace table offering unobstructed twilight views with warm heating beacons.",
        "features": ["Open-air starlight dining", "Heated lounge seats", "Signature sunset cocktail on arrival"],
    },
    {
        "id": "tbl-std-01",
        "name": "Bamboo Garden Bistro Table #12",
        "table_type": "standard",
        "capacity": 2,
        "is_premium": False,
        "reservation_fee": 0.0,
        "location_tag": "Ground Atrium · Bamboo Garden",
        "description": "Warm, minimalist wooden table surrounded by indoor zen bonsai and gentle water features.",
        "features": ["Zen garden ambiance", "Instant mobile contactless ordering", "Zero reservation fee"],
    },
    {
        "id": "tbl-std-02",
        "name": "Central Hall Round Table #08",
        "table_type": "standard",
        "capacity": 4,
        "is_premium": False,
        "reservation_fee": 0.0,
        "location_tag": "Central Bistro Salon",
        "description": "Spacious, comfortable round table in the lively main dining room with cushioned banquettes.",
        "features": ["Lively bistro atmosphere", "Accommodates groups up to 4", "Zero reservation fee"],
    },
    {
        "id": "tbl-std-03",
        "name": "Family Gathering Table #15",
        "table_type": "standard",
        "capacity": 8,
        "is_premium": False,
        "reservation_fee": 0.0,
        "location_tag": "East Wing Dining Hall",
        "description": "Expansive solid oak table tailored for large families, friend reunions, and team feasts.",
        "features": ["Comfortably seats 8 guests", "Shared platter turntable", "Zero reservation fee"],
    },
]

COUPONS_SEED = [
    {
        "id": "cpn-bournet20",
        "code": "BOURNET20",
        "title": "Bournet Haute Cuisine 20% Off",
        "description": "Enjoy 20% discount on gourmet meals up to ₹500 discount for orders above ₹1,000.",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "max_discount_amount": 500.0,
        "min_order_value": 1000.0,
        "usage_limit": 1000,
        "valid_until_days": 180,
    },
    {
        "id": "cpn-vip500",
        "code": "VIP500",
        "title": "VIP Grand Dining ₹500 Flat Off",
        "description": "Flat ₹500 off on premium orders exceeding ₹2,500.",
        "discount_type": "fixed",
        "discount_value": 500.0,
        "max_discount_amount": None,
        "min_order_value": 2500.0,
        "usage_limit": 500,
        "valid_until_days": 180,
    },
    {
        "id": "cpn-welcome100",
        "code": "WELCOME100",
        "title": "Welcome Treat ₹100 Off",
        "description": "Get ₹100 off your delicious meal for orders of ₹499 or more.",
        "discount_type": "fixed",
        "discount_value": 100.0,
        "max_discount_amount": None,
        "min_order_value": 499.0,
        "usage_limit": 2000,
        "valid_until_days": 365,
    },
    {
        "id": "cpn-fresh15",
        "code": "FRESH15",
        "title": "Fresh Bowl Explorer 15% Off",
        "description": "15% off fresh poke bowls and bistro specialties up to ₹300 for orders above ₹750.",
        "discount_type": "percentage",
        "discount_value": 15.0,
        "max_discount_amount": 300.0,
        "min_order_value": 750.0,
        "usage_limit": 500,
        "valid_until_days": 90,
    },
]


async def seed_database(session):
    """
    Populates dishes, tables, and coupons into database if empty.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select
    from app.models import BuildYourOwnOptionModel, DishModel, RestaurantModel, RestaurantTableModel, CouponModel

    result = await session.execute(select(DishModel).limit(1))
    existing = result.scalars().first()
    if existing is not None:
        dishes_result = await session.execute(select(DishModel))
        all_seeds = DISHES_SEED + FEATURED_DISHES
        seed_map = {item["id"]: item for item in DISHES_SEED + FEATURED_DISHES}
        legacy_seed_ids = {item["id"] for item in all_seeds if item["id"] not in {"dish-build-meal", "dish-egg-01"}}
        for dish in dishes_result.scalars().all():
            if dish.id in seed_map:
                seed_item = seed_map[dish.id]
                dish.name = seed_item["name"]
                dish.description = seed_item["description"]
                dish.ingredients = json.dumps(seed_item["ingredients"])
                dish.allergens = json.dumps(seed_item["allergens"])
                dish.category = seed_item.get("category", dish.category)
            elif dish.id.startswith("generated-"):
                dietary_type = dish.id.removeprefix("generated-").rsplit("-", 1)[0]
                seq = int(dish.id.rsplit("-", 1)[1])
                generated = generated_dietary_dish(dietary_type, seq)
                dish.name = generated["name"]
                dish.description = generated["description"]
                dish.ingredients = json.dumps(generated["ingredients"])
                dish.allergens = json.dumps(generated["allergens"])
                dish.dietary_type = dietary_type
            needs_conversion = dish.id in legacy_seed_ids and dish.base_price < 100
            if needs_conversion:
                dish.base_price = round(dish.base_price * 83, 2)
                if dish.customization_schema:
                    schema = json.loads(dish.customization_schema)
                    for step in schema:
                        for option in step.get("options", []):
                            if option.get("price", 0) > 0:
                                option["price"] = round(option["price"] * 83, 2)
                    dish.customization_schema = json.dumps(schema)
            elif dish.id == "dish-build-meal" and dish.base_price > 1000:
                dish.base_price = round(dish.base_price / 83, 2)
                if dish.customization_schema:
                    schema = json.loads(dish.customization_schema)
                    for step in schema:
                        for option in step.get("options", []):
                            if option.get("price", 0) > 0:
                                option["price"] = round(option["price"] / 83, 2)
                    dish.customization_schema = json.dumps(schema)
            dish.is_premium = dish.is_premium or dish.id in PREMIUM_DISH_IDS
            restaurant_index = int(hashlib.sha256(dish.id.encode()).hexdigest()[:8], 16) % len(RESTAURANT_PROFILES)
            dish.restaurant_id = RESTAURANT_PROFILES[restaurant_index][0]

        from app.routers.continental import CONTINENTAL_DISHES
        for cont_dish in CONTINENTAL_DISHES:
            cont_res = await session.execute(select(DishModel).where(DishModel.id == cont_dish["id"]))
            if cont_res.scalars().first() is None:
                session.add(DishModel(
                    id=cont_dish["id"],
                    name=cont_dish["name"],
                    slug=f"{cont_dish['id']}-gourmet",
                    category="continental",
                    dietary_type=cont_dish["dietary_type"],
                    restaurant_id="restaurant-fire-bowl",
                    hidden_from_catalog=False,
                    description=cont_dish["description"],
                    base_price=cont_dish["base_price"],
                    calories=cont_dish["calories"],
                    protein_g=cont_dish["protein_g"],
                    prep_time_mins=cont_dish["prep_time_mins"],
                    image_url=cont_dish["imageUrl"],
                    allergens=json.dumps([]),
                    ingredients=json.dumps(cont_dish["ingredients"]),
                    customizable=False,
                    is_popular=cont_dish["is_popular"],
                    is_premium=True,
                    rating=cont_dish["rating"],
                    review_count=cont_dish["review_count"],
                ))
        builder_result = await session.execute(select(DishModel).where(DishModel.id == "dish-build-meal"))
        if builder_result.scalars().first() is None:
            builder = next(item for item in DISHES_SEED if item["id"] == "dish-build-meal")
            builder_schema = json.loads(json.dumps(builder["customization_schema"]))
            for step in builder_schema:
                for option in step["options"]:
                    option["price"] = round(option["price"] * 83, 2)
            session.add(DishModel(
                id=builder["id"], name=builder["name"], slug=builder["slug"], category=builder["category"],
                dietary_type="veg", restaurant_id="restaurant-zero-g", description=builder["description"],
                base_price=round(builder["base_price"] * 83, 2), calories=builder["calories"], protein_g=builder["protein_g"],
                prep_time_mins=builder["prep_time_mins"], image_url=builder["image_url"], allergens="[]",
                ingredients=json.dumps(builder["ingredients"]), customizable=True,
                customization_schema=json.dumps(builder_schema), is_popular=True, rating=4.9, review_count=1,
            ))
        egg_result = await session.execute(select(DishModel).where(DishModel.id == "dish-egg-01"))
        if egg_result.scalars().first() is None:
            egg_dish = next(item for item in DISHES_SEED if item["id"] == "dish-egg-01")
            session.add(DishModel(
                id=egg_dish["id"], name=egg_dish["name"], slug=egg_dish["slug"], category=egg_dish["category"],
                dietary_type="egg", restaurant_id="restaurant-zero-g", description=egg_dish["description"],
                base_price=round(egg_dish["base_price"] * 83, 2), calories=egg_dish["calories"], protein_g=egg_dish["protein_g"],
                prep_time_mins=egg_dish["prep_time_mins"], image_url=egg_dish["image_url"], allergens=json.dumps(egg_dish["allergens"]),
                ingredients=json.dumps(egg_dish["ingredients"]), customizable=False, is_popular=False,
                rating=egg_dish["rating"], review_count=egg_dish["review_count"],
            ))
        for featured in FEATURED_DISHES:
            featured_result = await session.execute(select(DishModel).where(DishModel.id == featured["id"]))
            if featured_result.scalars().first() is None:
                session.add(DishModel(
                    id=featured["id"], name=featured["name"], slug=featured["slug"], category="featured",
                    dietary_type=featured["dietary_type"], restaurant_id="restaurant-zero-g",
                    hidden_from_catalog=True, description=featured["description"],
                    base_price=round(featured["base_price"] * 83, 2), calories=featured["calories"],
                    protein_g=20, prep_time_mins=12, image_url=featured["image_url"],
                    allergens=json.dumps(featured["allergens"]), ingredients=json.dumps(featured["ingredients"]),
                    customizable=False, is_popular=True, rating=4.9, review_count=1,
                ))
    else:
        for item in DISHES_SEED + FEATURED_DISHES:
            category = item.get("category", "bowls")
            text = f"{item['name']} {item['description']} {' '.join(item['ingredients'])}"
            dietary_type = infer_dietary_type(text)
            custom_schema = item.get("customization_schema")
            if custom_schema:
                custom_schema = json.loads(json.dumps(custom_schema))
                for step in custom_schema:
                    for option in step.get("options", []):
                        option["price"] = round(option.get("price", 0.0) * 83, 2)
            dish = DishModel(
                id=item["id"],
                name=item["name"],
                slug=item["slug"],
                category=category,
                dietary_type=dietary_type,
                restaurant_id="restaurant-zero-g" if category != "pizzas" else "restaurant-fire-bowl",
                hidden_from_catalog=item in FEATURED_DISHES,
                description=item["description"],
                base_price=round(item["base_price"] * 83, 2),
                calories=item["calories"],
                protein_g=item.get("protein_g", 20),
                prep_time_mins=item.get("prep_time_mins", 12),
                    image_url=FEATURED_IMAGE_PATHS.get(item["id"], unique_dish_image_url(item["image_url"], item["id"])),
                allergens=json.dumps(item["allergens"]),
                ingredients=json.dumps(item["ingredients"]),
                customizable=item.get("customizable", False),
                customization_schema=json.dumps(custom_schema) if custom_schema else None,
                is_popular=item.get("is_popular", False),
                    is_premium=item["id"] in PREMIUM_DISH_IDS,
                rating=item.get("rating", 4.9),
                review_count=item.get("review_count", 100),
            )
            session.add(dish)

        from app.routers.continental import CONTINENTAL_DISHES
        for cont_dish in CONTINENTAL_DISHES:
            session.add(DishModel(
                id=cont_dish["id"],
                name=cont_dish["name"],
                slug=f"{cont_dish['id']}-gourmet",
                category="continental",
                dietary_type=cont_dish["dietary_type"],
                restaurant_id="restaurant-fire-bowl",
                hidden_from_catalog=False,
                description=cont_dish["description"],
                base_price=cont_dish["base_price"],
                calories=cont_dish["calories"],
                protein_g=cont_dish["protein_g"],
                prep_time_mins=cont_dish["prep_time_mins"],
                image_url=cont_dish["imageUrl"],
                allergens=json.dumps([]),
                ingredients=json.dumps(cont_dish["ingredients"]),
                customizable=False,
                is_popular=cont_dish["is_popular"],
                is_premium=True,
                rating=cont_dish["rating"],
                review_count=cont_dish["review_count"],
            ))

    await session.flush()
    visible_result = await session.execute(select(DishModel).where(DishModel.hidden_from_catalog.is_(False)))
    visible_dishes = visible_result.scalars().all()
    counts = {dietary_type: 0 for dietary_type in ("veg", "non-veg", "egg", "vegan")}
    existing_ids = set()
    for dish in visible_dishes:
        existing_ids.add(dish.id)
        if dish.dietary_type in counts:
            counts[dish.dietary_type] += 1

    for dietary_type, count in counts.items():
        sequence = 1
        while count < 50:
            generated = generated_dietary_dish(dietary_type, sequence)
            if generated["id"] not in existing_ids:
                session.add(DishModel(
                    id=generated["id"], name=generated["name"], slug=generated["slug"],
                    category=generated["category"], dietary_type=dietary_type,
                    restaurant_id=generated["restaurant_id"], description=generated["description"],
                    base_price=round(generated["base_price"] * 83, 2), calories=generated["calories"],
                    protein_g=generated["protein_g"], prep_time_mins=generated["prep_time_mins"],
                    image_url=generated["image_url"], allergens=json.dumps(generated["allergens"]),
                    ingredients=json.dumps(generated["ingredients"]), customizable=False,
                    is_premium=False,
                    is_popular=generated["is_popular"], rating=generated["rating"],
                    review_count=generated["review_count"],
                ))
                existing_ids.add(generated["id"])
                count += 1
            sequence += 1

    restaurant_result = await session.execute(select(RestaurantModel))
    restaurants_by_id = {restaurant.id: restaurant for restaurant in restaurant_result.scalars().all()}
    for index, profile in enumerate(RESTAURANT_PROFILES):
        restaurant_id, name, tags, description, rating, sla, photo_id = profile
        image_url = f"https://images.unsplash.com/photo-{photo_id}?w=900&auto=format&fit=crop&q=85"
        restaurant = restaurants_by_id.get(restaurant_id)
        if restaurant is None:
            restaurant = RestaurantModel(id=restaurant_id, name=name)
            session.add(restaurant)
        restaurant.name = name
        restaurant.cuisine_tags = json.dumps(tags)
        restaurant.description = description
        restaurant.rating = rating
        restaurant.delivery_sla_mins = sla
        restaurant.distance_km = round(1.8 + index * 0.45, 1)
        restaurant.image_url = image_url
        restaurant.logo_url = unique_dish_image_url(image_url, f"logo-{restaurant_id}")
        restaurant.is_active = True

    dish_result = await session.execute(select(DishModel).order_by(DishModel.id))
    all_dishes = dish_result.scalars().all()
    reserved_photo_ids = set(DISH_PHOTO_OVERRIDES.values())
    photo_pool = iter(photo_id for photo_id in PEXELS_FOOD_PHOTO_IDS if photo_id not in reserved_photo_ids)
    for index, dish in enumerate(all_dishes):
        photo_id = DISH_PHOTO_OVERRIDES.get(dish.id)
        if photo_id is None:
            photo_id = next(photo_pool, None)
        if photo_id is None:
            dish.hidden_from_catalog = True
            dish.is_premium = False
            continue
        dish.image_url = pexels_food_photo_url(photo_id)
        dish.is_premium = dish.is_premium or dish.id in PREMIUM_DISH_IDS
        restaurant_index = int(hashlib.sha256(dish.id.encode()).hexdigest()[:8], 16) % len(RESTAURANT_PROFILES)
        dish.restaurant_id = RESTAURANT_PROFILES[restaurant_index][0]

    options_result = await session.execute(select(BuildYourOwnOptionModel).limit(1))
    if options_result.scalars().first() is None:
        builder_seed = next(item for item in DISHES_SEED if item["id"] == "dish-build-meal")
        category_by_step = {"base": "base", "protein": "protein", "mixins": "topping", "dressing": "dressing"}
        for step in builder_seed["customization_schema"]:
            for option in step["options"]:
                session.add(BuildYourOwnOptionModel(
                    id=option["id"], category=category_by_step[step["step_id"]],
                    name=option["name"], description=step["title"],
                    price=round(option.get("price", 0.0) * 83, 2),
                    allergens=json.dumps(option.get("allergens", [])),
                ))

    tables_result = await session.execute(select(RestaurantTableModel).limit(1))
    if tables_result.scalars().first() is None:
        for t in TABLES_SEED:
            session.add(RestaurantTableModel(
                id=t["id"],
                name=t["name"],
                table_type=t["table_type"],
                capacity=t["capacity"],
                is_premium=t["is_premium"],
                reservation_fee=t["reservation_fee"],
                location_tag=t["location_tag"],
                description=t["description"],
                features_json=json.dumps(t["features"]),
                is_active=True,
            ))

    coupons_result = await session.execute(select(CouponModel).limit(1))
    if coupons_result.scalars().first() is None:
        now = datetime.utcnow()
        for c in COUPONS_SEED:
            session.add(CouponModel(
                id=c["id"],
                code=c["code"],
                title=c["title"],
                description=c["description"],
                discount_type=c["discount_type"],
                discount_value=c["discount_value"],
                max_discount_amount=c["max_discount_amount"],
                min_order_value=c["min_order_value"],
                usage_limit=c["usage_limit"],
                times_used=0,
                valid_from=now - timedelta(days=1),
                valid_until=now + timedelta(days=c["valid_until_days"]),
                is_active=True,
                created_at=now,
            ))

    await session.commit()
