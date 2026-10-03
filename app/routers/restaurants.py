"""Restaurant discovery endpoint."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import DishModel, RestaurantModel
from app.routers.menu import parse_dish_model

router = APIRouter(prefix="/api/v1/restaurants", tags=["Restaurants"])
api_router = APIRouter(tags=["Restaurants"])


@router.get("")
@api_router.get("/api/restaurants")
async def list_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantModel).where(RestaurantModel.is_active.is_(True)).order_by(RestaurantModel.name))
    return [
        {
            "id": restaurant.id,
            "name": restaurant.name,
            "cuisine_tags": json.loads(restaurant.cuisine_tags or "[]"),
            "description": restaurant.description,
            "rating": restaurant.rating,
            "delivery_sla_mins": restaurant.delivery_sla_mins,
            "distance_km": restaurant.distance_km,
            "image_url": restaurant.image_url,
            "logo_url": restaurant.logo_url,
            "tags": json.loads(restaurant.cuisine_tags or "[]"),
        }
        for restaurant in result.scalars().all()
    ]


@router.get("/{restaurant_id}/dishes")
@api_router.get("/api/restaurants/{restaurant_id}/dishes")
async def list_restaurant_dishes(restaurant_id: str, db: AsyncSession = Depends(get_db)):
    restaurant_result = await db.execute(
        select(RestaurantModel).where(RestaurantModel.id == restaurant_id, RestaurantModel.is_active.is_(True))
    )
    if restaurant_result.scalars().first() is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    result = await db.execute(
        select(DishModel)
        .where(DishModel.restaurant_id == restaurant_id, DishModel.hidden_from_catalog.is_(False))
        .order_by(DishModel.name)
    )
    return [parse_dish_model(dish) for dish in result.scalars().all()]
