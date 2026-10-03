"""
Discount Coupon Validation & Application Router.
Supports percentage and fixed discounts, expiry checking, minimum order value,
usage limits, and dynamic savings calculations.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import CouponModel
from app.pricing import money
from app.schemas import (
    CouponValidateRequest,
    CouponValidateResponse,
    AvailableCouponResponse,
)

router = APIRouter(prefix="/api/v1/coupons", tags=["Discount Coupons"])


def evaluate_coupon_rules(coupon: CouponModel, subtotal: float) -> Tuple[bool, float, str]:
    """
    Core coupon validation utility.
    Validates existence, active status, date range, usage limit, and minimum order value.
    Returns: (is_valid, discount_amount, message)
    """
    now = datetime.utcnow()

    # 1. Active status check
    if not coupon.is_active:
        return False, 0.0, f"Promo code '{coupon.code}' is currently inactive."

    # 2. Expiry dates validation
    if coupon.valid_from and now < coupon.valid_from:
        return False, 0.0, f"Promo code '{coupon.code}' is not active yet."

    if coupon.valid_until and now > coupon.valid_until:
        return False, 0.0, f"Promo code '{coupon.code}' expired on {coupon.valid_until.strftime('%b %d, %Y')}."

    # 3. Usage limit validation
    if coupon.usage_limit is not None and coupon.times_used >= coupon.usage_limit:
        return False, 0.0, f"Promo code '{coupon.code}' has reached its maximum redemption limit."

    # 4. Minimum order value validation
    if subtotal < coupon.min_order_value:
        shortfall = money(coupon.min_order_value - subtotal)
        return False, 0.0, f"Add ₹{shortfall:.2f} more to unlock '{coupon.code}' (min order ₹{coupon.min_order_value:.2f})."

    # 5. Calculate discount amount
    if coupon.discount_type == "percentage":
        raw_discount = subtotal * (coupon.discount_value / 100.0)
        if coupon.max_discount_amount:
            calculated_discount = min(raw_discount, coupon.max_discount_amount)
        else:
            calculated_discount = raw_discount
        discount_amount = money(calculated_discount)
        message = f"Applied {coupon.discount_value:.0f}% off! You saved ₹{discount_amount:.2f}."
    elif coupon.discount_type == "fixed":
        discount_amount = money(min(coupon.discount_value, subtotal))
        message = f"Applied flat ₹{discount_amount:.2f} discount successfully!"
    else:
        discount_amount = 0.0
        message = "Unrecognized discount rule."

    return True, discount_amount, message


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    payload: CouponValidateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Real-time coupon validation endpoint.
    Provides immediate feedback and returns discount amount and new total.
    """
    code_normalized = payload.code.strip().upper()
    if not code_normalized:
        raise HTTPException(status_code=400, detail="Please enter a valid coupon code.")

    stmt = select(CouponModel).where(CouponModel.code == code_normalized)
    result = await db.execute(stmt)
    coupon = result.scalars().first()

    if not coupon:
        return CouponValidateResponse(
            is_valid=False,
            code=code_normalized,
            title="",
            description="",
            discount_type="percentage",
            discount_value=0.0,
            discount_amount=0.0,
            min_order_value=0.0,
            subtotal=payload.subtotal,
            final_total=payload.subtotal,
            message=f"Coupon code '{code_normalized}' is invalid or does not exist.",
        )

    is_valid, discount_amount, message = evaluate_coupon_rules(coupon, payload.subtotal)
    final_total = money(max(0.0, payload.subtotal - discount_amount))

    return CouponValidateResponse(
        is_valid=is_valid,
        code=coupon.code,
        title=coupon.title,
        description=coupon.description,
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value,
        discount_amount=discount_amount,
        min_order_value=coupon.min_order_value,
        subtotal=payload.subtotal,
        final_total=final_total,
        message=message,
    )


@router.get("/available", response_model=List[AvailableCouponResponse])
async def list_available_coupons(db: AsyncSession = Depends(get_db)):
    """
    Returns list of active public coupons for user discovery.
    """
    now = datetime.utcnow()
    stmt = select(CouponModel).where(
        CouponModel.is_active.is_(True),
        CouponModel.valid_until > now,
    ).order_by(CouponModel.discount_value.desc())
    result = await db.execute(stmt)
    coupons = result.scalars().all()
    return [
        AvailableCouponResponse(
            code=c.code,
            title=c.title,
            description=c.description,
            discount_type=c.discount_type,
            discount_value=c.discount_value,
            min_order_value=c.min_order_value,
            max_discount_amount=c.max_discount_amount,
        )
        for c in coupons
    ]
