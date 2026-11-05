"""Product search and URL lookup endpoints."""

import sys
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException

# Ensure project root is on sys.path for scraper module
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scraper.manager import ScraperManager
from scraper.models import ScrapedProduct
from backend.app.models import SearchRequest, LookupUrlRequest

router = APIRouter(prefix="/api", tags=["Products"])
scraper_manager = ScraperManager()


@router.post("/search", response_model=List[ScrapedProduct])
async def search_products(req: SearchRequest):
    """
    Search for products across configured stores (US-01, US-02).
    Applies optional max_price filtering (US-04).
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    results = await scraper_manager.search_all(req.query, limit_per_store=req.limit)

    # US-04: Filter by maximum price if specified
    if req.max_price is not None and req.max_price > 0:
        results = [p for p in results if p.price <= req.max_price]

    return results


@router.post("/lookup-url", response_model=ScrapedProduct)
async def lookup_url(req: LookupUrlRequest):
    """
    Extract product details from a direct product URL.
    Works with Ikea, Amazon, and any store supporting OpenGraph / Schema.org metadata.
    """
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    product = await scraper_manager.get_product_from_url(req.url)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Could not extract product details from the provided URL. Please check the link or store compatibility.",
        )

    return product

