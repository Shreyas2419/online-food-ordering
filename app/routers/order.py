"""
Order Placement and Real-Time WebSocket Tracking Engine.
"""
import asyncio
import json
import math
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, async_session
from app.models import DriverLocationModel, OrderModel, DishModel, CouponModel
from app.models import UserModel, WalletTransactionModel, SupportTicketModel
from app.schemas import (
    OrderCreateRequest,
    OrderResponse,
    OrderCancelResponse,
    KitchenStatusResponse,
    CartItemDetail,
    SupportTicketRequest,
)
from app.pricing import checkout_fees, money, authoritative_selections, token_discount, cancellation_charge, COD_CANCELLATION_FEE
from app.security import get_optional_user
from app.routers.coupon import evaluate_coupon_rules

router = APIRouter(tags=["Orders & Real-Time Tracking"])

CURRENT_QUEUE = 3
DRIVERS = [
    ("Aarav Menon", "+91 90000 12345", "Electric scooter · KA 03 AB 4821", 4.9),
    ("Mira Shah", "+91 90000 23456", "Electric cycle · KA 05 CD 1742", 4.8),
    ("Kabir Rao", "+91 90000 34567", "Electric scooter · KA 01 EF 9053", 4.9),
]

@router.get("/api/v1/kitchen/queue-status", response_model=KitchenStatusResponse)
async def get_kitchen_status():
    return KitchenStatusResponse(
        active_queue=CURRENT_QUEUE,
        avg_prep_time_mins=12,
        transit_rate_mins_per_km=2.2,
        current_status="Optimal Operations",
        sla_formula="ETA = Prep Time + (Active Kitchen Queue * 2 mins) + Transit Time"
    )

@router.post("/api/v1/orders", response_model=OrderResponse)
@router.post("/api/orders", response_model=OrderResponse)
async def create_order(
    payload: OrderCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserModel | None = Depends(get_optional_user),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cannot place empty order")

    # Fetch dishes to calculate authoritative total and prep time
    dish_ids = [item.dish_id for item in payload.items]
    stmt = select(DishModel).where(DishModel.id.in_(dish_ids))
    result = await db.execute(stmt)
    dishes = {d.id: d for d in result.scalars().all()}

    subtotal = 0.0
    max_prep = 10
    detail_items = []

    for item in payload.items:
        dish = dishes.get(item.dish_id)
        if not dish:
            raise HTTPException(status_code=400, detail=f"Invalid dish ID: {item.dish_id}")
        
        unit_price = dish.base_price
        cals = dish.calories
        selections = authoritative_selections(dish, item.selections)
        for selection in selections:
            unit_price += selection["price"]
            cals += selection["calories"]
        
        item_total = round(unit_price * item.quantity, 2)
        subtotal += item_total
        max_prep = max(max_prep, dish.prep_time_mins)

        detail_items.append({
            "dish_id": dish.id,
            "name": dish.name,
            "unit_price": round(unit_price, 2),
            "base_price": dish.base_price,
            "calories": cals,
            "prep_time_mins": dish.prep_time_mins,
            "quantity": item.quantity,
            "total_price": item_total,
            "image_url": dish.image_url,
            "selections": selections
        })

    subtotal = round(subtotal, 2)
    premium = bool(user and user.premium_until and user.premium_until > datetime.utcnow())
    delivery_fee, cod_fee, express_charge = checkout_fees(
        subtotal, 0.0, payload.payment_method, payload.delivery_mode, premium,
    )
    if payload.delivery_mode == "express" and premium:
        express_charge = money(express_charge * 0.9)
    discount = token_discount(subtotal, premium, payload.payment_method)

    # Evaluate optional promo coupon
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
                c_obj.times_used += 1

    total_amount = money(max(0.0, subtotal + delivery_fee + cod_fee + express_charge - discount - coupon_discount_val))
    if payload.payment_method == "tokens":
        if not user:
            raise HTTPException(status_code=401, detail="Sign in to pay with wallet tokens")
        if user.wallet_tokens < total_amount:
            raise HTTPException(status_code=402, detail={"message": "Insufficient wallet tokens", "required": total_amount, "available": user.wallet_tokens})
        user.wallet_tokens = money(user.wallet_tokens - total_amount)
        db.add(WalletTransactionModel(
            id=f"txn-{uuid.uuid4().hex[:16]}", user_id=user.id, amount=-total_amount,
            kind="order_payment", status="settled", reference="pending-order",
        ))
    payment_status = "paid" if payload.payment_method == "tokens" else ("due" if payload.payment_method == "cod" else "pending")
    priority = payload.delivery_mode == "express" or premium
    active_queue = max(1, CURRENT_QUEUE - 2) if priority else CURRENT_QUEUE

    # Standard delivery transit time (independent of distance)
    transit_mins = 10
    queue_delay = active_queue * 2
    eta_mins = max_prep + queue_delay + transit_mins
    if payload.delivery_mode == "express":
        eta_mins = max(5, round(eta_mins * 0.65))
    elif premium:
        eta_mins = max(6, round(eta_mins * 0.8))

    order_id = f"ZG-{uuid.uuid4().hex[:8].upper()}"
    driver = DRIVERS[int(order_id[-2:], 16) % len(DRIVERS)]

    new_order = OrderModel(
        id=order_id,
        customer_name=payload.customer_name,
        items_json=json.dumps(detail_items),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        cod_fee=cod_fee,
        express_fee=express_charge,
        token_discount=discount,
        coupon_code=applied_coupon_code,
        coupon_discount=coupon_discount_val,
        total_amount=total_amount,
        currency="INR",
        payment_method=payload.payment_method,
        payment_status=payment_status,
        delivery_mode=payload.delivery_mode,
        priority=priority,
        user_id=user.id if user else None,
        tokens_used=total_amount if payload.payment_method == "tokens" else 0.0,
        delivery_address=payload.delivery_address,
        distance_km=0.0,
        active_kitchen_queue=active_queue,
        prep_time_mins=max_prep,
        transit_time_mins=transit_mins,
        eta_minutes=eta_mins,
        cancellation_fee=0.0,
        status="payment_pending" if payment_status == "pending" else ("placed" if request.url.path == "/api/orders" else "received"),
        driver_name=driver[0],
        driver_phone=driver[1],
        driver_vehicle=driver[2],
        driver_rating=driver[3],
        created_at=datetime.utcnow(),
    )
    db.add(new_order)
    db.add(DriverLocationModel(order_id=order_id, latitude=12.9716, longitude=77.5946))
    await db.commit()

    return OrderResponse(
        order_id=order_id,
        customer_name=payload.customer_name,
        delivery_address=payload.delivery_address,
        status=new_order.status,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        cod_fee=cod_fee,
        express_fee=express_charge,
        token_discount=discount,
        coupon_code=applied_coupon_code,
        coupon_discount=coupon_discount_val,
        total_amount=total_amount,
        payment_method=payload.payment_method,
        payment_status=payment_status,
        delivery_mode=payload.delivery_mode,
        priority=priority,
        currency="INR",
        item_count=sum(i.quantity for i in payload.items),
        distance_km=payload.distance_km,
        active_kitchen_queue=active_queue,
        prep_time_mins=max_prep,
        transit_time_mins=transit_mins,
        eta_minutes=eta_mins,
        created_at=new_order.created_at.isoformat(),
        items=[
            CartItemDetail(
                dish_id=it["dish_id"],
                name=it["name"],
                base_price=it["unit_price"],
                unit_price=it["unit_price"],
                quantity=it["quantity"],
                total_price=it["total_price"],
                total_calories=500,
                image_url=it["image_url"],
                allergens=[],
                selections_summary=[s["name"] for s in it.get("selections", [])],
                allergen_warnings=[],
            )
            for it in detail_items
        ]
    )


@router.get("/api/v1/orders/{order_id}/track")
@router.get("/api/orders/{order_id}/track")
async def track_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserModel | None = Depends(get_optional_user),
):
    result = await db.execute(select(OrderModel).where(OrderModel.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id and (not user or order.user_id != user.id):
        raise HTTPException(status_code=403, detail="Sign in to track this order")

    elapsed = max(0.0, (datetime.utcnow() - order.created_at).total_seconds())
    if order.payment_status == "pending":
        status, progress = "payment_pending", 5
    elif elapsed < 10:
        status, progress = "placed", 18
    elif elapsed < 30:
        status, progress = "preparing", 38 + int((elapsed - 10) / 20 * 24)
    elif elapsed < 90:
        status, progress = "out_for_delivery", 64 + int((elapsed - 30) / 60 * 32)
    else:
        status, progress = "delivered", 100

    if status != "payment_pending":
        order.status = status
    location_result = await db.execute(select(DriverLocationModel).where(DriverLocationModel.order_id == order_id))
    location = location_result.scalars().first()
    if location is None:
        location = DriverLocationModel(order_id=order_id, latitude=12.9716, longitude=77.5946)
        db.add(location)

    route_progress = 0.0 if status in ("placed", "payment_pending") else 0.18 if status == "preparing" else min(0.96, max(0.18, (elapsed - 19) / 71))
    if status == "delivered":
        route_progress = 1.0
    destination_latitude, destination_longitude = 12.9828, 77.6061
    location.latitude = round(12.9716 + (destination_latitude - 12.9716) * route_progress, 6)
    location.longitude = round(77.5946 + (destination_longitude - 77.5946) * route_progress, 6)
    location.updated_at = datetime.utcnow()
    await db.commit()

    return {
        "order_id": order.id,
        "status": status,
        "progress_percent": progress,
        "eta_minutes": max(0, order.eta_minutes - int(elapsed // 60)),
        "distance_km": round(max(0.0, order.distance_km * (1.0 - route_progress)), 2),
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "payment_summary": {
            "method": order.payment_method,
            "status": order.payment_status,
            "total": order.total_amount,
        },
        "driver": {
            "name": order.driver_name,
            "phone": order.driver_phone,
            "vehicle": order.driver_vehicle,
            "rating": order.driver_rating,
        },
        "location": {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "updated_at": location.updated_at.isoformat(),
        },
    }

@router.get("/api/v1/orders/{order_id}")
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserModel | None = Depends(get_optional_user),
):
    stmt = select(OrderModel).where(OrderModel.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id and (not user or order.user_id != user.id):
        raise HTTPException(status_code=403, detail="Sign in to view this order")
    
    return {
        "order_id": order.id,
        "status": order.status,
        "customer_name": order.customer_name,
        "delivery_address": order.delivery_address,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "cod_fee": order.cod_fee,
        "express_fee": order.express_fee,
        "token_discount": order.token_discount,
        "total_amount": order.total_amount,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "delivery_mode": order.delivery_mode,
        "priority": order.priority,
        "currency": order.currency,
        "eta_minutes": order.eta_minutes,
        "active_kitchen_queue": order.active_kitchen_queue,
        "prep_time_mins": order.prep_time_mins,
        "transit_time_mins": order.transit_time_mins,
        "distance_km": order.distance_km,
        "created_at": order.created_at.isoformat(),
        "items": json.loads(order.items_json)
    }


@router.post("/api/v1/orders/{order_id}/support")
async def create_order_support_ticket(
    order_id: str,
    payload: SupportTicketRequest,
    db: AsyncSession = Depends(get_db),
    user: UserModel | None = Depends(get_optional_user),
):
    result = await db.execute(select(OrderModel).where(OrderModel.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id and (not user or order.user_id != user.id):
        raise HTTPException(status_code=403, detail="Sign in to contact support for this order")
    ticket = SupportTicketModel(
        id=f"SUP-{uuid.uuid4().hex[:10].upper()}", order_id=order_id,
        user_id=user.id if user else None, message=payload.message.strip(),
    )
    db.add(ticket)
    await db.commit()
    return {"ticket_id": ticket.id, "order_id": order_id, "status": ticket.status, "created_at": ticket.created_at.isoformat()}

@router.websocket("/ws/order-tracking/{order_id}")
async def order_tracking_ws(websocket: WebSocket, order_id: str):
    """
    Real-Time WebSocket stream broadcasting high-frequency status transitions
    and simulated drone/courier telemetry along with SLA countdown.
    """
    await websocket.accept()

    # Initial lookup
    async with async_session() as db:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        distance = order.distance_km if order else 3.5
        eta_minutes = order.eta_minutes if order else 26

    # Stages timeline simulation (demonstrates full lifecycle smoothly):
    # Stage 1: Received (4 seconds)
    # Stage 2: Preparing (8 seconds)
    # Stage 3: Out for Delivery (14 seconds, with continuous drone telemetry)
    # Stage 4: Delivered
    try:
        # Phase 1: Order Received & Allergen Shield Verified
        for i in range(4):
            await websocket.send_json({
                "type": "TELEMETRY_UPDATE",
                "order_id": order_id,
                "status": "received",
                "stage_index": 0,
                "stage_label": "Order Received",
                "stage_description": "Kitchen verified order & active allergen shield filters locked in.",
                "progress_percent": 15 + (i * 5),
                "eta_minutes": eta_minutes,
                "distance_km": distance,
                "courier": {
                    "name": "Droid Courier X-9",
                    "type": "Zero-G Quadcopter",
                    "status": "Standing by at Kitchen Pad A"
                }
            })
            await asyncio.sleep(1.0)

        # Update DB status to preparing
        async with async_session() as db:
            stmt = select(OrderModel).where(OrderModel.id == order_id)
            res = await db.execute(stmt)
            ord_obj = res.scalars().first()
            if ord_obj:
                ord_obj.status = "preparing"
                await db.commit()

        # Phase 2: Kitchen Preparing
        for i in range(7):
            prep_progress = 30 + int((i / 7.0) * 30)
            await websocket.send_json({
                "type": "TELEMETRY_UPDATE",
                "order_id": order_id,
                "status": "preparing",
                "stage_index": 1,
                "stage_label": "Zero-G Kitchen Crafting",
                "stage_description": f"Sous-chef crafting bowl. Induction heating active. Step {i+1}/7.",
                "progress_percent": prep_progress,
                "eta_minutes": max(1, eta_minutes - int(i * 0.5)),
                "distance_km": distance,
                "courier": {
                    "name": "Droid Courier X-9",
                    "type": "Zero-G Quadcopter",
                    "status": "Pre-flight calibration complete"
                }
            })
            await asyncio.sleep(1.0)

        # Update DB status to out_for_delivery
        async with async_session() as db:
            stmt = select(OrderModel).where(OrderModel.id == order_id)
            res = await db.execute(stmt)
            ord_obj = res.scalars().first()
            if ord_obj:
                ord_obj.status = "out_for_delivery"
                await db.commit()

        # Phase 3: Out for Delivery (Drone in Flight)
        flight_steps = 14
        for step in range(flight_steps):
            ratio = (step + 1) / flight_steps
            dist_remaining = round(max(0.05, distance * (1.0 - ratio)), 2)
            eta_rem = max(1, round(eta_minutes * (1.0 - (ratio * 0.8))))
            speed_kmh = round(38.0 + (step % 4) * 2.5, 1)
            altitude_m = round(85.0 + math.sin(step) * 12, 1)
            battery_pct = round(98 - (step * 0.8), 0)

            await websocket.send_json({
                "type": "TELEMETRY_UPDATE",
                "order_id": order_id,
                "status": "out_for_delivery",
                "stage_index": 2,
                "stage_label": "Out for Zero-G Delivery",
                "stage_description": f"Autonomous aerial drone en route. Speed: {speed_kmh} km/h • Altitude: {altitude_m}m",
                "progress_percent": 65 + int(ratio * 30),
                "eta_minutes": eta_rem,
                "distance_km": dist_remaining,
                "courier": {
                    "name": "Droid Courier X-9",
                    "type": "Zero-G Quadcopter",
                    "status": "Airborne in Corridor 4",
                    "speed_kmh": speed_kmh,
                    "altitude_m": altitude_m,
                    "battery_pct": battery_pct,
                    "flight_ratio": ratio,
                }
            })
            await asyncio.sleep(1.0)

        # Update DB status to delivered
        async with async_session() as db:
            stmt = select(OrderModel).where(OrderModel.id == order_id)
            res = await db.execute(stmt)
            ord_obj = res.scalars().first()
            if ord_obj:
                ord_obj.status = "delivered"
                await db.commit()

        # Phase 4: Delivered
        while True:
            await websocket.send_json({
                "type": "TELEMETRY_UPDATE",
                "order_id": order_id,
                "status": "delivered",
                "stage_index": 3,
                "stage_label": "Order Delivered! 🛸",
                "stage_description": "Package deposited at landing zone with thermal seal intact. Enjoy your meal!",
                "progress_percent": 100,
                "eta_minutes": 0,
                "distance_km": 0.0,
                "courier": {
                    "name": "Droid Courier X-9",
                    "type": "Zero-G Quadcopter",
                    "status": "Mission Complete - Returning to Base",
                    "battery_pct": 86,
                    "flight_ratio": 1.0,
                }
            })
            await asyncio.sleep(5.0)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print(f"WS error: {exc}")


@router.post("/api/v1/orders/{order_id}/cancel", response_model=OrderCancelResponse)
@router.post("/api/orders/{order_id}/cancel", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserModel | None = Depends(get_optional_user),
):
    """
    Cancel an existing order.
    Business Rule (Requirement 6):
    Extra charges apply for the cancellation of an order after it has been placed.
    Crucially, this extra cancellation charge must ONLY apply to orders where
    the payment method is selected as 'Cash on Delivery' (COD).
    """
    stmt = select(OrderModel).where(OrderModel.id == order_id)
    res = await db.execute(stmt)
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == "cancelled":
        is_cod = order.payment_method.strip().lower() in ("cod", "cash on delivery")
        return OrderCancelResponse(
            order_id=order.id,
            status="cancelled",
            payment_method=order.payment_method,
            extra_cancellation_charge_applied=order.cancellation_fee > 0,
            cancellation_fee=order.cancellation_fee,
            message="Order is already cancelled.",
            policy_notice="Extra charges apply for the cancellation of an order after it has been placed (Strictly applicable for Cash on Delivery).",
        )

    if order.status in ("delivered", "out_for_delivery"):
        raise HTTPException(status_code=400, detail="Dispatched or delivered orders cannot be cancelled")

    is_cod = order.payment_method.strip().lower() in ("cod", "cash on delivery")
    fee = cancellation_charge(order.payment_method)

    order.status = "cancelled"
    order.cancellation_fee = fee
    order.cancellation_reason = (
        f"Customer cancellation. Extra cancellation charge of ₹{fee:.2f} applied strictly for Cash on Delivery (COD)."
        if is_cod else "Customer cancellation. Zero cancellation fee applied for prepaid order."
    )
    await db.commit()

    return OrderCancelResponse(
        order_id=order.id,
        status="cancelled",
        payment_method=order.payment_method,
        extra_cancellation_charge_applied=is_cod,
        cancellation_fee=fee,
        message=(
            f"Order cancelled. Extra cancellation charge of ₹{fee:.2f} applied strictly for Cash on Delivery (COD)."
            if is_cod else "Order cancelled successfully. No cancellation charges applied for prepaid order."
        ),
        policy_notice="Extra charges apply for the cancellation of an order after it has been placed (Strictly applicable for Cash on Delivery).",
    )

