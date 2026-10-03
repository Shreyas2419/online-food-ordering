"""
SQLAlchemy ORM models for Dish and Order entities.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class DishModel(Base):
    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    dietary_type: Mapped[str] = mapped_column(String(20), default="veg", index=True)
    restaurant_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    hidden_from_catalog: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    protein_g: Mapped[int] = mapped_column(Integer, default=20)
    prep_time_mins: Mapped[int] = mapped_column(Integer, default=12)
    image_url: Mapped[str] = mapped_column(String(300), nullable=False)
    allergens: Mapped[str] = mapped_column(Text, default="[]")  # JSON list e.g. ["peanuts", "soy"]
    ingredients: Mapped[str] = mapped_column(Text, default="[]") # JSON list of ingredients
    customizable: Mapped[bool] = mapped_column(Boolean, default=False)
    customization_schema: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON schema for dish builder
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rating: Mapped[float] = mapped_column(Float, default=4.9)
    review_count: Mapped[int] = mapped_column(Integer, default=120)

class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100), default="Astro Eater")
    items_json: Mapped[str] = mapped_column(Text, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_fee: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    cod_fee: Mapped[float] = mapped_column(Float, default=0.0)
    express_fee: Mapped[float] = mapped_column(Float, default=0.0)
    token_discount: Mapped[float] = mapped_column(Float, default=0.0)
    coupon_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    coupon_discount: Mapped[float] = mapped_column(Float, default=0.0)
    payment_method: Mapped[str] = mapped_column(String(20), default="cod")
    payment_status: Mapped[str] = mapped_column(String(20), default="due")
    delivery_mode: Mapped[str] = mapped_column(String(20), default="standard")
    priority: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    tokens_used: Mapped[float] = mapped_column(Float, default=0.0)
    delivery_address: Mapped[str] = mapped_column(String(200), default="Sector 7G, Cyber District")
    distance_km: Mapped[float] = mapped_column(Float, default=3.2)
    active_kitchen_queue: Mapped[int] = mapped_column(Integer, default=3)
    prep_time_mins: Mapped[int] = mapped_column(Integer, default=14)
    transit_time_mins: Mapped[int] = mapped_column(Integer, default=8)
    eta_minutes: Mapped[int] = mapped_column(Integer, default=28)
    status: Mapped[str] = mapped_column(String(50), default="placed", index=True)
    driver_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    driver_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    driver_vehicle: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    driver_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cancellation_fee: Mapped[float] = mapped_column(Float, default=0.0)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RestaurantModel(Base):
    __tablename__ = "restaurants"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    cuisine_tags: Mapped[str] = mapped_column(Text, default="[]")
    description: Mapped[str] = mapped_column(Text, default="")
    rating: Mapped[float] = mapped_column(Float, default=4.8)
    delivery_sla_mins: Mapped[int] = mapped_column(Integer, default=30)
    distance_km: Mapped[float] = mapped_column(Float, default=2.5)
    image_url: Mapped[str] = mapped_column(String(300), default="")
    logo_url: Mapped[str] = mapped_column(String(300), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    wallet_tokens: Mapped[float] = mapped_column(Float, default=0.0)
    premium_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    dietary_preferences: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AddressModel(Base):
    __tablename__ = "delivery_addresses"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(40), default="Home")
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(12), default="")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class WalletTransactionModel(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reference: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SupportTicketModel(Base):
    __tablename__ = "support_tickets"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BuildYourOwnOptionModel(Base):
    __tablename__ = "build_your_own_options"

    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    allergens: Mapped[str] = mapped_column(Text, default="[]")


class DriverLocationModel(Base):
    __tablename__ = "driver_locations"

    order_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RestaurantTableModel(Base):
    __tablename__ = "restaurant_tables"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    table_type: Mapped[str] = mapped_column(String(40), default="standard", index=True)
    capacity: Mapped[int] = mapped_column(Integer, default=4)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    reservation_fee: Mapped[float] = mapped_column(Float, default=0.0)
    location_tag: Mapped[str] = mapped_column(String(100), default="Main Dining Room")
    description: Mapped[str] = mapped_column(Text, default="")
    features_json: Mapped[str] = mapped_column(Text, default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TableReservationModel(Base):
    __tablename__ = "table_reservations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    table_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(254), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    reservation_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    time_slot: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    special_requests: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="confirmed", index=True)
    deposit_amount: Mapped[float] = mapped_column(Float, default=0.0)
    deposit_status: Mapped[str] = mapped_column(String(20), default="waived")
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CouponModel(Base):
    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    discount_type: Mapped[str] = mapped_column(String(20), default="percentage")
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_discount_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
