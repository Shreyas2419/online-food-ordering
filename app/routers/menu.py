"""
Menu and Allergen Safe-Search Router.
"""
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import DishModel
from app.schemas import (
    DishResponse,
    DishSafeAssessment,
    SafeSearchRequest,
    SafeSearchResponse,
    CustomizationStep,
)

router = APIRouter(prefix="/api/v1/menu", tags=["Menu & Allergen Engine"])
premium_router = APIRouter(tags=["Premium dishes"])

def parse_dish_model(d: DishModel) -> DishResponse:
    allergens = json.loads(d.allergens) if d.allergens else []
    ingredients = json.loads(d.ingredients) if d.ingredients else []
    custom_schema = None
    if d.customization_schema:
        custom_schema = [CustomizationStep(**step) for step in json.loads(d.customization_schema)]
    
    return DishResponse(
        id=d.id,
        name=d.name,
        slug=d.slug,
        category=d.category,
        dietary_type=d.dietary_type,
        restaurant_id=d.restaurant_id,
        hidden_from_catalog=d.hidden_from_catalog,
        description=d.description,
        base_price=d.base_price,
        calories=d.calories,
        protein_g=d.protein_g,
        prep_time_mins=d.prep_time_mins,
        image_url=d.image_url,
        allergens=allergens,
        ingredients=ingredients,
        customizable=d.customizable,
        customization_schema=custom_schema,
        is_popular=d.is_popular,
        is_premium=d.is_premium,
        rating=d.rating,
        review_count=d.review_count,
    )

def assess_dish_safety(dish: DishResponse, active_allergens: List[str]) -> DishSafeAssessment:
    """
    Evaluates dish against active allergen filters, detecting conflicts
    and generating safe ingredient swaps.
    """
    normalized_active = [a.lower().strip() for a in active_allergens]
    detected = [a for a in dish.allergens if a.lower() in normalized_active]
    is_safe = len(detected) == 0

    swaps = []
    # If dish is customizable, check if any options offer safe swaps for detected allergens
    if dish.customization_schema:
        for step in dish.customization_schema:
            for opt in step.options:
                if opt.is_safe_swap and opt.swap_for and opt.swap_for.lower() in detected:
                    swaps.append({
                        "step_id": step.step_id,
                        "step_title": step.title,
                        "replaces_allergen": opt.swap_for,
                        "recommended_option": opt.name,
                        "option_id": opt.id,
                        "price_difference": opt.price,
                        "calorie_delta": opt.calories,
                    })

    # Standard fallback swap suggestions for non-customizable dishes
    if not is_safe and not swaps:
        for allergen in detected:
            if allergen == "peanuts":
                swaps.append({
                    "step_id": "kitchen_note",
                    "step_title": "Kitchen Preparation Swap",
                    "replaces_allergen": "peanuts",
                    "recommended_option": "Request kitchen exclude crushed peanuts and substitute toasted seeds",
                    "option_id": "swap-seeds",
                    "price_difference": 0.0,
                    "calorie_delta": -15
                })
            elif allergen == "gluten":
                swaps.append({
                    "step_id": "kitchen_note",
                    "step_title": "Kitchen Preparation Swap",
                    "replaces_allergen": "gluten",
                    "recommended_option": "Request lettuce wrap or gluten-free bowl modification",
                    "option_id": "swap-lettuce-wrap",
                    "price_difference": 0.0,
                    "calorie_delta": -120
                })
            elif allergen == "dairy":
                swaps.append({
                    "step_id": "kitchen_note",
                    "step_title": "Kitchen Preparation Swap",
                    "replaces_allergen": "dairy",
                    "recommended_option": "Request dairy-free cashew aioli or hold cheese",
                    "option_id": "swap-hold-dairy",
                    "price_difference": 0.0,
                    "calorie_delta": -90
                })
            elif allergen == "soy":
                swaps.append({
                    "step_id": "kitchen_note",
                    "step_title": "Kitchen Preparation Swap",
                    "replaces_allergen": "soy",
                    "recommended_option": "Sub with coconut aminos / olive oil drizzle",
                    "option_id": "swap-coconut-aminos",
                    "price_difference": 0.0,
                    "calorie_delta": 0
                })

    risk_level = "safe"
    if not is_safe:
        risk_level = "high_risk" if len(detected) >= 2 or "peanuts" in detected or "shellfish" in detected else "warning"

    return DishSafeAssessment(
        **dish.model_dump(),
        safe=is_safe,
        detected_allergens=detected,
        suggested_swaps=swaps,
        risk_level=risk_level,
    )

@router.get("", response_model=List[DishResponse])
async def get_menu(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
):
    query = select(DishModel).where(DishModel.hidden_from_catalog.is_(False))
    if category and category.lower() != "all":
        query = query.where(DishModel.category == category.lower())
    
    result = await db.execute(query)
    dishes = result.scalars().all()
    return [parse_dish_model(d) for d in dishes]


@premium_router.get("/api/dishes/premium", response_model=List[DishResponse])
@premium_router.get("/api/v1/dishes/premium", response_model=List[DishResponse])
async def get_premium_dishes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DishModel).where(DishModel.is_premium.is_(True)).order_by(DishModel.base_price.desc())
    )
    return [parse_dish_model(dish) for dish in result.scalars().all()]

@router.post("/safe-search", response_model=SafeSearchResponse)
async def safe_search(
    payload: SafeSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates all menu items against active allergen shields,
    partitioning into Safe vs High-Risk items with actionable swaps.
    """
    query = select(DishModel).where(DishModel.hidden_from_catalog.is_(False))
    if payload.category and payload.category.lower() != "all":
        query = query.where(DishModel.category == payload.category.lower())

    result = await db.execute(query)
    raw_dishes = result.scalars().all()

    filtered_dishes = []
    q = payload.query.lower().strip() if payload.query else ""

    for d in raw_dishes:
        parsed = parse_dish_model(d)
        if q:
            matches_name = q in parsed.name.lower()
            matches_desc = q in parsed.description.lower()
            matches_ingr = any(q in ing.lower() for ing in parsed.ingredients)
            if not (matches_name or matches_desc or matches_ingr):
                continue
        filtered_dishes.append(parsed)

    safe_list: List[DishSafeAssessment] = []
    unsafe_list: List[DishSafeAssessment] = []

    for dish in filtered_dishes:
        assessment = assess_dish_safety(dish, payload.allergens)
        if assessment.safe:
            safe_list.append(assessment)
        else:
            unsafe_list.append(assessment)

    return SafeSearchResponse(
        total=len(filtered_dishes),
        safe_count=len(safe_list),
        unsafe_count=len(unsafe_list),
        active_filters=payload.allergens,
        safe_items=safe_list,
        unsafe_items=unsafe_list,
    )
