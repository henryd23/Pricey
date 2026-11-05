"""Data models for scraped product data."""

from typing import Optional
from pydantic import BaseModel, Field


class ScrapedProduct(BaseModel):
    title: str = Field(..., description="Product title/name")
    price: float = Field(..., description="Numeric price extracted (in EUR/store currency)")
    currency: str = Field(default="EUR", description="Currency symbol or ISO code")
    url: str = Field(..., description="Canonical or requested product URL")
    store: str = Field(..., description="Name of the store (e.g., Amazon, Ikea, Decathlon)")
    image_url: Optional[str] = Field(default=None, description="Main product image URL")
    is_available: bool = Field(default=True, description="Availability status")
    sku: Optional[str] = Field(default=None, description="Store SKU / ASIN / item identifier")
    raw_price: Optional[str] = Field(default=None, description="Original unparsed price text")
