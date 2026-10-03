"""
Cart Validation and Dynamic Pricing Engine.
"""
import json
import math
from datetime import datetime
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import BuildYourOwnOptionModel, DishModel, UserModel, CouponModel
from app.schemas import (
    CartValidateRequest,
    CartValidateResponse,
    CartItemDetail,
    SelectedCustomization,
)
from app.pricing import FREE_DELIVERY_THRESHOLD, authoritative_selections, checkout_fees, money, token_discount
from app.security import get_optional_user
from app.routers.coupon import evaluate_coupon_rules

router = APIRouter(prefix="/api/v1/cart", tags=["Cart & SLA Engine"])
custom_router = APIRouter(tags=["Custom meal builder"])


class CustomMealRequest(BaseModel):
    option_ids: List[str] = Field(min_length=3, max_length=10)
    quantity: int = Field(default=1, ge=1, le=50)


@custom_router.get("/api/custom-builder/options")
@custom_router.get("/api/v1/custom-builder/options")
async def get_custom_builder_options(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BuildYourOwnOptionModel).order_by(BuildYourOwnOptionModel.category, BuildYourOwnOptionModel.name))
    options = [
        {
            "id": option.id,
            "category": option.category,
            "name": option.name,
            "description": option.description,
            "price": option.price,
            "allergens": json.loads(option.allergens or "[]"),
        }
        for option in result.scalars().all()
    ]
    dish_result = await db.execute(select(DishModel).where(DishModel.id == "dish-build-meal"))
    dish = dish_result.scalars().first()
    return {
        "dish": {
            "id": dish.id,
            "name": dish.name,
            "base_price": dish.base_price,
            "calories": dish.calories,
            "prep_time_mins": dish.prep_time_mins,
            "image_url": dish.image_url,
        } if dish else None,
        "options": options,
    }


@custom_router.post("/api/cart/add-custom")
@custom_router.post("/api/v1/cart/add-custom")
async def add_custom_meal(payload: CustomMealRequest, db: AsyncSession = Depends(get_db)):
    if len(set(payload.option_ids)) != len(payload.option_ids):
        raise HTTPException(status_code=400, detail="An ingredient can only be selected once")
    result = await db.execute(select(BuildYourOwnOptionModel).where(BuildYourOwnOptionModel.id.in_(payload.option_ids)))
    options = list(result.scalars().all())
    if len(options) != len(payload.option_ids):
        raise HTTPException(status_code=400, detail="One or more selected ingredients are unavailable")
    counts = {category: sum(option.category == category for option in options) for category in ("base", "protein", "topping", "dressing")}
    if counts["base"] != 1 or counts["protein"] != 1 or not 1 <= counts["topping"] <= 3 or counts["dressing"] != 1:
        raise HTTPException(status_code=400, detail="Choose one base, one protein, one to three toppings, and one dressing")

    dish_result = await db.execute(select(DishModel).where(DishModel.id == "dish-build-meal"))
    dish = dish_result.scalars().first()
    if not dish:
        raise HTTPException(status_code=503, detail="Custom meal is unavailable")
    step_by_category = {"base": "base", "protein": "protein", "topping": "mixins", "dressing": "dressing"}
    submitted = [SelectedCustomization(
        step_id=step_by_category[option.category], option_id=option.id, name=option.name,
        price=option.price, allergens=json.loads(option.allergens or "[]"),
    ) for option in options]
    selections = authoritative_selections(dish, submitted)
    unit_price = round(dish.base_price + sum(selection["price"] for selection in selections), 2)
    return {
        "dish": {
            "id": dish.id, "name": dish.name, "base_price": dish.base_price,
            "calories": dish.calories, "prep_time_mins": dish.prep_time_mins,
            "image_url": dish.image_url,
        },
        "selections": selections,
        "quantity": payload.quantity,
        "unit_price": unit_price,
        "line_total": round(unit_price * payload.quantity, 2),
    }

SIMULATED_KITCHEN_QUEUE = 3  # Active orders currently ahead in queue

@router.post("", response_model=CartValidateResponse)
async def validate_cart(
    payload: CartValidateRequest,
    db: AsyncSession = Depends(get_db),
    user: UserModel | None = Depends(get_optional_user),
):
    """
    Authoritative server-side cart calculation with dynamic SLA ETA,
    allergen cross-checks, and free delivery threshold tracking.
    """
    if not payload.items:
        # Empty cart response
        transit_time = 10
        eta = 12 + (SIMULATED_KITCHEN_QUEUE * 2) + transit_time
        return CartValidateResponse(
            items=[],
            item_count=0,
            subtotal=0.0,
            delivery_fee=0.0,
            free_delivery_threshold=FREE_DELIVERY_THRESHOLD,
            amount_needed_for_free_delivery=FREE_DELIVERY_THRESHOLD,
            is_free_delivery=False,
            total=0.0,
            cod_fee=0.0,
            express_fee=0.0,
            payment_method=payload.payment_method,
            delivery_mode=payload.delivery_mode,
            active_kitchen_queue=SIMULATED_KITCHEN_QUEUE,
            prep_time_mins=12,
            transit_time_mins=transit_time,
            eta_minutes=eta,
        )

    # Fetch all relevant dishes from DB
    dish_ids = [item.dish_id for item in payload.items]
    stmt = select(DishModel).where(DishModel.id.in_(dish_ids))
    result = await db.execute(stmt)
    dishes_by_id: Dict[str, DishModel] = {d.id: d for d in result.scalars().all()}

    validated_items: List[CartItemDetail] = []
    subtotal = 0.0
    max_prep_time = 10
    normalized_allergens = [a.lower().strip() for a in payload.active_allergens]

    for item_input in payload.items:
        dish = dishes_by_id.get(item_input.dish_id)
        if not dish:
            raise HTTPException(status_code=400, detail=f"Dish ID {item_input.dish_id} not found in catalog")

        dish_allergens = json.loads(dish.allergens) if dish.allergens else []
        unit_price = dish.base_price
        total_item_cals = dish.calories
        selections_summary = []
        allergen_warnings = []

        # Check base allergens against active profile
        for a in dish_allergens:
            if a.lower() in normalized_allergens:
                allergen_warnings.append(f"Dish inherently contains {a.capitalize()}")

        # Process selections
        custom_allergens = set(dish_allergens)
        selections = authoritative_selections(dish, item_input.selections)
        for sel in selections:
            unit_price += sel["price"]
            total_item_cals += sel["calories"]
            selections_summary.append(f"{sel['name']} (+₹{sel['price']:.2f})")
            for sel_a in sel["allergens"]:
                custom_allergens.add(sel_a)
                if sel_a.lower() in normalized_allergens:
                    allergen_warnings.append(f"Option '{sel['name']}' introduces {sel_a.capitalize()}")

        item_total_price = round(unit_price * item_input.quantity, 2)
        subtotal += item_total_price
        max_prep_time = max(max_prep_time, dish.prep_time_mins)

        validated_items.append(CartItemDetail(
            dish_id=dish.id,
            name=dish.name,
            base_price=dish.base_price,
            unit_price=round(unit_price, 2),
            quantity=item_input.quantity,
            total_price=item_total_price,
            total_calories=total_item_cals * item_input.quantity,
            image_url=dish.image_url,
            allergens=list(custom_allergens),
            selections_summary=selections_summary,
            allergen_warnings=list(set(allergen_warnings)),
        ))

    subtotal = round(subtotal, 2)
    premium = bool(user and user.premium_until and user.premium_until > datetime.utcnow())
    delivery_fee, cod_fee, express_fee = checkout_fees(
        subtotal, 0.0, payload.payment_method, payload.delivery_mode, premium,
    )
    if premium and payload.delivery_mode == "express":
        express_fee = money(express_fee * 0.9)
    is_free = delivery_fee == 0.0
    amount_needed = max(0.0, round(FREE_DELIVERY_THRESHOLD - subtotal, 2))
    discount = token_discount(subtotal, premium, payload.payment_method)

    # Evaluate optional coupon
    applied_coupon_code = None
    coupon_discount_val = 0.0
    if payload.coupon_code:
        c_code = payload.coupon_code.strip().upper()
        c_stmt = select(CouponModel).where(CouponModel.code == c_code)
        c_res = await db.execute(c_stmt)
        c_obj = c_res.scalars().first()
        if c_obj:
            is_c_valid, c_disc, _ = evaluate_coupon_rules(c_obj, subtotal)
            if is_c_valid:
                applied_coupon_code = c_obj.code
                coupon_discount_val = c_disc

    grand_total = money(max(0.0, subtotal + delivery_fee + cod_fee + express_fee - discount - coupon_discount_val))
    if payload.payment_method == "tokens" and not user:
        raise HTTPException(status_code=401, detail="Sign in to pay with wallet tokens")
    if payload.payment_method == "tokens" and user and user.wallet_tokens < grand_total:
        raise HTTPException(status_code=402, detail="Insufficient wallet tokens")

    priority = payload.delivery_mode == "express" or premium
    active_queue = max(1, SIMULATED_KITCHEN_QUEUE - 2) if priority else SIMULATED_KITCHEN_QUEUE
    transit_time_mins = 10
    queue_delay_mins = active_queue * 2
    eta_mins = max_prep_time + queue_delay_mins + transit_time_mins

    return CartValidateResponse(
        items=validated_items,
        item_count=sum(i.quantity for i in validated_items),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        free_delivery_threshold=FREE_DELIVERY_THRESHOLD,
        amount_needed_for_free_delivery=amount_needed,
        is_free_delivery=is_free,
        total=grand_total,
        cod_fee=cod_fee,
        express_fee=express_fee,
        token_discount=discount,
        coupon_code=applied_coupon_code,
        coupon_discount=coupon_discount_val,
        payment_method=payload.payment_method,
        delivery_mode=payload.delivery_mode,
        active_kitchen_queue=active_queue,
        prep_time_mins=max_prep_time,
        transit_time_mins=transit_time_mins,
        eta_minutes=eta_mins,
    )
