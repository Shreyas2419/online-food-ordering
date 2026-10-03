"""Account, address, wallet, and premium membership APIs."""
import json
import hashlib
import hmac
import os
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AddressModel, OrderModel, UserModel, WalletTransactionModel
from app.schemas import AddressCreateRequest, LoginRequest, PaymentWebhookRequest, ProfileUpdateRequest, SignupRequest, TokenTopUpRequest
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/v1/account", tags=["Accounts & Wallet"])
PAYMENT_WEBHOOK_SECRET = os.getenv("PAYMENT_WEBHOOK_SECRET")


def user_payload(user: UserModel):
    premium = bool(user.premium_until and user.premium_until > datetime.utcnow())
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "phone": user.phone,
        "wallet_tokens": round(user.wallet_tokens, 2),
        "premium": premium,
        "premium_until": user.premium_until.isoformat() if premium else None,
        "premium_benefits": ["Zero delivery fee", "Priority kitchen routing", "10% token discount"] if premium else [],
        "dietary_preferences": json.loads(user.dietary_preferences or "[]"),
    }


@router.post("/signup")
async def signup(payload: SignupRequest, db: AsyncSession = Depends(get_db)):
    email = payload.email.strip().lower()
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = UserModel(
        id=f"usr-{uuid.uuid4().hex[:16]}",
        email=email,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
        phone=payload.phone.strip() if payload.phone else None,
        wallet_tokens=500.0,
    )
    db.add(user)
    db.add(WalletTransactionModel(
        id=f"txn-{uuid.uuid4().hex[:16]}", user_id=user.id, amount=500.0,
        kind="welcome_reward", status="settled", reference="signup-reward",
    ))
    await db.commit()
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": user_payload(user)}


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.email == payload.email.strip().lower()))
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": user_payload(user)}


@router.get("/me")
async def get_profile(user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    address_result = await db.execute(select(AddressModel).where(AddressModel.user_id == user.id))
    order_result = await db.execute(select(OrderModel).where(OrderModel.user_id == user.id).order_by(OrderModel.created_at.desc()).limit(20))
    return {
        **user_payload(user),
        "addresses": [
            {"id": a.id, "label": a.label, "address": a.address, "postal_code": a.postal_code, "is_default": a.is_default}
            for a in address_result.scalars().all()
        ],
        "orders": [
            {"order_id": o.id, "status": o.status, "total_amount": o.total_amount, "currency": o.currency, "created_at": o.created_at.isoformat(), "items": json.loads(o.items_json)}
            for o in order_result.scalars().all()
        ],
    }


@router.patch("/me")
async def update_profile(payload: ProfileUpdateRequest, user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.display_name is not None:
        user.display_name = payload.display_name.strip()
    if payload.phone is not None:
        user.phone = payload.phone.strip() or None
    if payload.dietary_preferences is not None:
        user.dietary_preferences = json.dumps([value.strip().lower() for value in payload.dietary_preferences if value.strip()])
    await db.commit()
    return user_payload(user)


@router.post("/addresses")
async def add_address(payload: AddressCreateRequest, user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AddressModel).where(AddressModel.user_id == user.id))
    existing = result.scalars().all()
    is_default = payload.is_default or not existing
    if is_default:
        for address in existing:
            address.is_default = False
    address = AddressModel(
        id=f"addr-{uuid.uuid4().hex[:16]}", user_id=user.id, label=payload.label.strip(),
        address=payload.address.strip(), postal_code=payload.postal_code.strip(), is_default=is_default,
    )
    db.add(address)
    await db.commit()
    return {"id": address.id, "label": address.label, "address": address.address, "postal_code": address.postal_code, "is_default": address.is_default}


@router.post("/tokens/top-up")
async def request_token_top_up(payload: TokenTopUpRequest, user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    transaction = WalletTransactionModel(
        id=f"txn-{uuid.uuid4().hex[:16]}", user_id=user.id, amount=payload.amount,
        kind="top_up", status="pending", reference=f"provider-pending-{payload.payment_method}",
    )
    db.add(transaction)
    await db.commit()
    return {
        "transaction_id": transaction.id,
        "status": "pending",
        "amount": payload.amount,
        "currency": "INR",
        "payment_method": payload.payment_method,
        "message": "Wallet tokens are added after payment-provider confirmation. Configure a payment gateway webhook to settle this transaction.",
    }


@router.post("/payments/webhook")
async def settle_token_top_up(
    payload: PaymentWebhookRequest,
    x_payment_signature: str = Header(default=""),
    db: AsyncSession = Depends(get_db),
):
    if not PAYMENT_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Payment webhook secret is not configured")
    body = json.dumps(payload.model_dump(), separators=(",", ":")).encode()
    expected = hmac.new(PAYMENT_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    supplied = x_payment_signature.removeprefix("sha256=")
    if not hmac.compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="Invalid payment signature")

    if bool(payload.transaction_id) == bool(payload.order_id):
        raise HTTPException(status_code=400, detail="Provide exactly one transaction_id or order_id")

    if payload.order_id:
        result = await db.execute(select(OrderModel).where(OrderModel.id == payload.order_id))
        order = result.scalars().first()
        if not order:
            raise HTTPException(status_code=404, detail="Payment order not found")
        if order.payment_status in {"paid", "failed"}:
            if order.payment_status == payload.status:
                return {"order_id": order.id, "status": order.payment_status, "idempotent": True}
            raise HTTPException(status_code=409, detail="Order payment has already been finalized")
        if order.payment_status != "pending":
            raise HTTPException(status_code=409, detail="Order is not awaiting online payment")
        order.payment_status = payload.status
        order.status = "received" if payload.status == "paid" else "payment_failed"
        await db.commit()
        return {"order_id": order.id, "status": order.payment_status, "order_status": order.status}

    result = await db.execute(select(WalletTransactionModel).where(WalletTransactionModel.id == payload.transaction_id))
    transaction = result.scalars().first()
    if not transaction or transaction.kind != "top_up":
        raise HTTPException(status_code=404, detail="Token top-up transaction not found")
    if transaction.status in {"settled", "failed"}:
        final_status = "paid" if transaction.status == "settled" else "failed"
        if payload.status == final_status:
            return {"transaction_id": transaction.id, "status": transaction.status, "idempotent": True}
        raise HTTPException(status_code=409, detail="Token top-up has already been finalized")
    if transaction.status != "pending":
        raise HTTPException(status_code=409, detail="Token top-up has already been finalized")

    transaction.status = "settled" if payload.status == "paid" else "failed"
    transaction.reference = payload.provider_reference or transaction.reference
    if payload.status == "paid":
        user_result = await db.execute(select(UserModel).where(UserModel.id == transaction.user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Wallet owner no longer exists")
        user.wallet_tokens = round(user.wallet_tokens + transaction.amount, 2)
    await db.commit()
    return {"transaction_id": transaction.id, "status": transaction.status, "amount": transaction.amount if payload.status == "paid" else 0.0}


@router.post("/premium")
async def activate_premium(user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    price = 499.0
    if user.wallet_tokens < price:
        raise HTTPException(status_code=402, detail={"message": "Premium costs 499 tokens for 30 days", "required_tokens": price, "wallet_tokens": user.wallet_tokens})
    now = datetime.utcnow()
    starts_at = user.premium_until if user.premium_until and user.premium_until > now else now
    user.wallet_tokens = round(user.wallet_tokens - price, 2)
    user.premium_until = starts_at + timedelta(days=30)
    db.add(WalletTransactionModel(
        id=f"txn-{uuid.uuid4().hex[:16]}", user_id=user.id, amount=-price,
        kind="premium_membership", status="settled", reference="premium-30-days",
    ))
    await db.commit()
    return user_payload(user)
