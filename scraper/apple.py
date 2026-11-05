"""Apple store scraper implementation for Pricey."""

import re
from typing import Optional
from bs4 import BeautifulSoup
from scraper.base import BaseScraper
from scraper.models import ScrapedProduct
from scraper.utils import parse_price


class AppleScraper(BaseScraper):
    name: str = "Apple"
    base_url: str = "https://www.apple.com/it"

    def can_handle(self, url: str) -> bool:
        return "apple.com" in url.lower()

    async def get_product_details(self, url: str) -> Optional[ScrapedProduct]:
        html = await self._fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Title
        title_el = (
            soup.select_one('meta[property="og:title"]')
            or soup.select_one("h1")
            or soup.select_one(".rc-dimension-selector-label")
        )
        title = title_el.get("content") if title_el and title_el.get("content") else (title_el.get_text(strip=True) if title_el else None)

        if not title and soup.title:
            title = soup.title.get_text(strip=True).replace("- Apple (IT)", "").strip()

        if not title:
            return None

        # Price
        price: Optional[float] = None
        raw_price: Optional[str] = None

        price_meta = soup.select_one('meta[property="product:price:amount"]') or soup.select_one('meta[name="price"]')
        if price_meta and price_meta.get("content"):
            price = parse_price(price_meta.get("content"))
            raw_price = price_meta.get("content")

        if price is None:
            selectors = [
                ".rc-prices-fullprice",
                ".rc-prices-currentprice",
                ".current_price",
                '[data-autom="full-price"]',
            ]
            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    raw = el.get_text(strip=True)
                    val = parse_price(raw)
                    if val is not None and val > 0:
                        price = val
                        raw_price = raw
                        break

        if price is None:
            return None

        # Image
        img_meta = soup.select_one('meta[property="og:image"]')
        image_url = img_meta.get("content") if img_meta else None

        return ScrapedProduct(
            title=title,
            price=price,
            currency="EUR",
            url=url,
            store=self.name,
            image_url=image_url,
            is_available=True,
            sku=None,
            raw_price=raw_price,
        )

