"""Main FastAPI application entrypoint."""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database import init_db
from backend.app.services.scheduler import start_scheduler, stop_scheduler
from backend.app.routes import products, tracking, notifications


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db()
    # Start periodic background price checking
    start_scheduler()
    yield
    # Stop scheduler on shutdown
    stop_scheduler()


app = FastAPI(
    title="Pricey API",
    description="Backend API for Pricey - E-commerce price tracker and notification system",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(products.router)
app.include_router(tracking.router)
app.include_router(notifications.router)


@app.get("/")
def home():
    return {
        "name": "Pricey API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "search": "POST /api/search",
            "lookup_url": "POST /api/lookup-url",
            "tracked": "GET /api/tracked",
            "notifications": "GET /api/notifications",
        },
    }
