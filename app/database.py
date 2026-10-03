"""
Database configuration using Async SQLAlchemy 2.0 and aiosqlite.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect

DB_PATH = os.path.join(os.path.dirname(__file__), "food_ordering.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{os.getenv('DATABASE_PATH', DB_PATH)}")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


def upgrade_legacy_columns(connection):
    """Add the new nullable/defaulted columns to existing SQLite databases."""
    additions = {
        "dishes": {
            "dietary_type": "VARCHAR(20) NOT NULL DEFAULT 'veg'",
            "restaurant_id": "VARCHAR(50)",
            "hidden_from_catalog": "BOOLEAN NOT NULL DEFAULT 0",
            "is_premium": "BOOLEAN NOT NULL DEFAULT 0",
        },
        "orders": {
            "currency": "VARCHAR(3) NOT NULL DEFAULT 'INR'",
            "cod_fee": "FLOAT NOT NULL DEFAULT 0",
            "express_fee": "FLOAT NOT NULL DEFAULT 0",
            "token_discount": "FLOAT NOT NULL DEFAULT 0",
            "payment_method": "VARCHAR(20) NOT NULL DEFAULT 'cod'",
            "payment_status": "VARCHAR(20) NOT NULL DEFAULT 'due'",
            "delivery_mode": "VARCHAR(20) NOT NULL DEFAULT 'standard'",
            "priority": "BOOLEAN NOT NULL DEFAULT 0",
            "user_id": "VARCHAR(50)",
            "tokens_used": "FLOAT NOT NULL DEFAULT 0",
            "driver_name": "VARCHAR(100)",
            "driver_phone": "VARCHAR(30)",
            "driver_vehicle": "VARCHAR(80)",
            "driver_rating": "FLOAT",
            "coupon_code": "VARCHAR(30)",
            "coupon_discount": "FLOAT NOT NULL DEFAULT 0",
            "cancellation_fee": "FLOAT NOT NULL DEFAULT 0",
            "cancellation_reason": "VARCHAR(255)",
        },
        "restaurants": {"logo_url": "VARCHAR(300) NOT NULL DEFAULT ''"},
        "users": {"phone": "VARCHAR(30)"},
    }
    inspector = inspect(connection)
    for table, columns in additions.items():
        if not inspector.has_table(table):
            continue
        existing = {column["name"] for column in inspector.get_columns(table)}
        for name, definition in columns.items():
            if name not in existing:
                connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
