"""Monitored items and tracking endpoints."""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

# Ensure project root is on sys.path for scraper module
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scraper.manager import ScraperManager
from backend.app.database import get_session
from backend.app.services.checker import check_all_monitored_items
from backend.app.models import (
    MonitoredItem,
    PriceHistory,
    TrackItemRequest,
    MonitoredItemRead,
    MonitoredItemDetail,
    PriceHistoryRead,
    utc_now,
)

router = APIRouter(prefix="/api/tracked", tags=["Tracking"])
scraper_manager = ScraperManager()


class UpdateThresholdRequest(BaseModel):
    target_delta_percent: float


@router.post("/check-now")
async def trigger_price_check():
    """
    Manually triggers an immediate price check cycle for all active monitored items (US-07).
    Returns summary statistics of the check cycle.
    """
    stats = await check_all_monitored_items()
    return {
        "status": "success",
        "message": f"Controllati {stats['checked']} prodotti. Rilevati {stats['drops_detected']} cali di prezzo e generate {stats['notifications_generated']} notifiche.",
        "stats": stats,
    }


@router.post("", response_model=MonitoredItemRead, status_code=status.HTTP_201_CREATED)
async def track_item(req: TrackItemRequest, session: Session = Depends(get_session)):
    """
    Add a product to monitored items (US-05, US-06, US-08).
    If details are not passed, fetches them live from the URL.
    """
    clean_url = req.url.strip()
    if not clean_url:
        raise HTTPException(status_code=400, detail="Product URL is required")

    # Check if item is already tracked
    statement = select(MonitoredItem).where(MonitoredItem.url == clean_url)
    existing_item = session.exec(statement).first()

    if existing_item:
        if not existing_item.is_active:
            existing_item.is_active = True
            existing_item.target_delta_percent = req.target_delta_percent
            session.add(existing_item)
            session.commit()
            session.refresh(existing_item)
            return existing_item
        raise HTTPException(
            status_code=409,
            detail="This product is already being monitored.",
        )

    # Resolve details if not provided
    title = req.title
    price = req.price
    image_url = req.image_url
    store_name = req.store_name

    if not title or price is None or not store_name:
        scraped = await scraper_manager.get_product_from_url(clean_url)
        if not scraped:
            raise HTTPException(
                status_code=400,
                detail="Could not extract details from the provided URL. Please verify the URL.",
            )
        title = title or scraped.title
        price = price if price is not None else scraped.price
        image_url = image_url or scraped.image_url
        store_name = store_name or scraped.store

    # Create MonitoredItem
    new_item = MonitoredItem(
        url=clean_url,
        store_name=store_name,
        title=title,
        image_url=image_url,
        initial_price=price,
        current_price=price,
        lowest_price=price,
        currency="EUR",
        target_delta_percent=req.target_delta_percent,
        is_active=True,
        created_at=utc_now(),
        last_checked_at=utc_now(),
    )
    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    # Initial Price History entry
    initial_history = PriceHistory(
        item_id=new_item.id,
        price=price,
        timestamp=new_item.created_at,
    )
    session.add(initial_history)
    session.commit()

    return new_item


@router.get("", response_model=List[MonitoredItemRead])
def list_tracked_items(
    active_only: bool = True,
    session: Session = Depends(get_session),
):
    """List all monitored products (US-06)."""
    statement = select(MonitoredItem)
    if active_only:
        statement = statement.where(MonitoredItem.is_active == True)
    statement = statement.order_by(MonitoredItem.created_at.desc())
    items = session.exec(statement).all()
    return items


@router.get("/{item_id}", response_model=MonitoredItemDetail)
def get_tracked_item(item_id: int, session: Session = Depends(get_session)):
    """Retrieve details and price history for a specific monitored product."""
    item = session.get(MonitoredItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Monitored item not found")

    history_statement = (
        select(PriceHistory)
        .where(PriceHistory.item_id == item_id)
        .order_by(PriceHistory.timestamp.asc())
    )
    history = session.exec(history_statement).all()

    return MonitoredItemDetail(
        id=item.id,
        url=item.url,
        store_name=item.store_name,
        title=item.title,
        image_url=item.image_url,
        initial_price=item.initial_price,
        current_price=item.current_price,
        lowest_price=item.lowest_price,
        currency=item.currency,
        target_delta_percent=item.target_delta_percent,
        is_active=item.is_active,
        created_at=item.created_at,
        last_checked_at=item.last_checked_at,
        price_history=[
            PriceHistoryRead(id=h.id, price=h.price, timestamp=h.timestamp)
            for h in history
        ],
    )


@router.patch("/{item_id}/threshold", response_model=MonitoredItemRead)
def update_threshold(
    item_id: int,
    req: UpdateThresholdRequest,
    session: Session = Depends(get_session),
):
    """Update the target price drop threshold (US-09)."""
    item = session.get(MonitoredItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Monitored item not found")

    if req.target_delta_percent <= 0:
        raise HTTPException(status_code=400, detail="Threshold must be greater than 0%")

    item.target_delta_percent = req.target_delta_percent
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tracked_item(item_id: int, session: Session = Depends(get_session)):
    """Stop monitoring and delete a product (US-06)."""
    item = session.get(MonitoredItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Monitored item not found")

    session.delete(item)
    session.commit()
    return None
