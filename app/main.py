"""
Main FastAPI Application Entrypoint.
"""
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base, async_session, upgrade_legacy_columns
from app.initial_data import seed_database
from app.routers import menu, cart, order, account, restaurants, coupon, reservations, bournet, continental

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
    if origin.strip()
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed default menu
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(upgrade_legacy_columns)
    
    async with async_session() as session:
        await seed_database(session)
    
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Faura - Flavour and Aura",
    description="Faura (Flavour and Aura) brings rich regional Indian delicacies and Continental favorites to your table.",
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(menu.router)
app.include_router(menu.premium_router)
app.include_router(bournet.router)
app.include_router(continental.router)
app.include_router(cart.router)
app.include_router(cart.custom_router)
app.include_router(coupon.router)
app.include_router(reservations.router)
app.include_router(order.router)
app.include_router(account.router)
app.include_router(restaurants.router)
app.include_router(restaurants.api_router)

# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Faura (Flavour and Aura) API is running. Static frontend pending."}
