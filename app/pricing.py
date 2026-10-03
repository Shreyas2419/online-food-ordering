"""Shared INR pricing rules used by cart and order validation."""

import json
from fastapi import HTTPException

CURRENCY = "INR"
USD_TO_INR = 83.0
FREE_DELIVERY_THRESHOLD = 25.0 * USD_TO_INR
COD_FEE = 10.0
FLAT_DELIVERY_FEE = 49.0
FLAT_EXPRESS_FEE = 79.0
COD_CANCELLATION_FEE = 50.0


def money(value: float) -> float:
    return round(value + 1e-9, 2)


def delivery_fee(subtotal: float, distance_km: float = 0.0, premium: bool = False) -> float:
    """Distance-free standard delivery fee; free for orders meeting threshold or premium accounts."""
    if premium or subtotal >= FREE_DELIVERY_THRESHOLD:
        return 0.0
    return FLAT_DELIVERY_FEE


def express_fee(distance_km: float = 0.0) -> float:
    """Flat priority express dispatch fee independent of distance."""
    return FLAT_EXPRESS_FEE


def cancellation_charge(payment_method: str) -> float:
    """Extra charges apply strictly for Cash on Delivery (COD) cancellations."""
    if payment_method and payment_method.strip().lower() in ("cod", "cash on delivery"):
        return COD_CANCELLATION_FEE
    return 0.0


def token_discount(subtotal: float, premium: bool, payment_method: str) -> float:
    return money(subtotal * 0.10) if premium and payment_method == "tokens" else 0.0


def checkout_fees(subtotal: float, distance_km: float = 0.0, payment_method: str = "cod", delivery_mode: str = "standard", premium: bool = False):
    standard_delivery = delivery_fee(subtotal, distance_km, premium)
    express = express_fee(distance_km) if delivery_mode == "express" else 0.0
    cod = COD_FEE if payment_method == "cod" else 0.0
    return standard_delivery, cod, express


FEATURED_ADDON_PRICES = {
    "featured-salmon-poke": [(15.0, 180), (5.0, 160), (3.0, 120)],
    "featured-tuna-sashimi": [(14.0, 170), (4.0, 45), (3.0, 90)],
    "featured-crispy-tofu": [(8.0, 150), (3.5, 110), (4.0, 60)],
    "featured-unagi": [(16.0, 210), (3.0, 70), (4.0, 130)],
    "featured-chirashi": [(18.0, 90), (5.0, 160), (4.5, 80)],
    "featured-chicken-katsu": [(12.0, 220), (4.0, 180), (2.0, 80)],
    "featured-garden-quinoa": [(3.5, 110), (3.0, 120), (1.5, 55)],
    "featured-prawn-soba": [(11.0, 150), (3.0, 180), (1.5, 45)],
    "featured-miso-mushroom": [(5.0, 150), (3.0, 70), (1.5, 40)],
    "featured-jammy-egg": [(2.0, 70), (3.0, 180), (1.5, 55)],
}


def authoritative_selections(dish, selections):
    """Resolve submitted option IDs against server-side menu definitions."""
    options = {}
    if dish.customization_schema:
        for step in json.loads(dish.customization_schema):
            for option in step.get("options", []):
                options[(step["step_id"], option["id"])] = option

    resolved = []
    for selection in selections:
        key = (selection.step_id, selection.option_id)
        option = options.get(key)
        if option:
            resolved.append({
                "step_id": selection.step_id,
                "option_id": selection.option_id,
                "name": option["name"],
                "price": money(float(option.get("price", 0))),
                "calories": int(option.get("calories", 0)),
                "allergens": option.get("allergens", []),
            })
            continue

        if selection.step_id.startswith("addon-") and selection.option_id.startswith("opt-"):
            try:
                index = int(selection.option_id.removeprefix("opt-")) - 1
                dollar_price, calories = FEATURED_ADDON_PRICES[dish.id][index]
            except (ValueError, IndexError, KeyError):
                raise HTTPException(status_code=400, detail="Unknown dish add-on")
            resolved.append({
                "step_id": selection.step_id,
                "option_id": selection.option_id,
                "name": selection.name,
                "price": money(dollar_price * USD_TO_INR),
                "calories": calories,
                "allergens": [],
            })
            continue

        if selection.step_id == "allergen_swap" and selection.price == 0:
            resolved.append({
                "step_id": selection.step_id,
                "option_id": selection.option_id,
                "name": selection.name,
                "price": 0.0,
                "calories": selection.calories,
                "allergens": [],
            })
            continue

        raise HTTPException(status_code=400, detail=f"Invalid customization option: {selection.option_id}")
    if dish.id == "dish-build-meal" and not any(item["step_id"] == "base" for item in resolved):
        raise HTTPException(status_code=400, detail="Choose a base before adding a custom meal")
    return resolved
