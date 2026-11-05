"""Ikea scraper implementation for Pricey (Italy)."""

import json
from typing import List, Optional
from bs4 import BeautifulSoup
import httpx
from scraper.base import BaseScraper
from scraper.models import ScrapedProduct
from scraper.utils import parse_price


class IkeaScraper(BaseScraper):
    name: str = "Ikea"
    base_url: str = "https://www.ikea.com/it/it"

    def can_handle(self, url: str) -> bool:
        return "ikea.com" in url.lower()

    async def get_product_details(self, url: str) -> Optional[ScrapedProduct]:
        html = await self._fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # 1. Try structured data (JSON-LD) - most reliable on Ikea
        scripts = soup.find_all("script", type="application/ld+json")
        for s in scripts:
            try:
                raw_text = s.string or s.get_text()
                if not raw_text:
                    continue
                data = json.loads(raw_text)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "Product":
                        title = item.get("name")
                        image = item.get("image")
                        if isinstance(image, list) and image:
                            first_img = image[0]
                            image = first_img.get("contentUrl") if isinstance(first_img, dict) else str(first_img)
                        elif isinstance(image, dict):
                            image = image.get("contentUrl") or image.get("url")

                        offers = item.get("offers", {})
                        if isinstance(offers, list) and offers:
                            offers = offers[0]
                        price_val = offers.get("price")
                        currency = offers.get("priceCurrency", "EUR")
                        avail = offers.get("availability", "")
                        is_avail = "InStock" in avail if avail else True

                        if title and price_val is not None:
                            numeric_price = parse_price(str(price_val))
                            if numeric_price is not None:
                                return ScrapedProduct(
                                    title=title,
                                    price=numeric_price,
                                    currency=currency,
                                    url=url,
                                    store=self.name,
                                    image_url=image,
                                    is_available=is_avail,
                                    sku=item.get("sku"),
                                    raw_price=f"{price_val} {currency}",
                                )
            except Exception:
                continue

        # 2. Fallback to DOM parsing
        title_el = soup.select_one(".pip-header-section__title--big") or soup.select_one("h1")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        subtitle_el = soup.select_one(".pip-header-section__description-text")
        if subtitle_el:
            title = f"{title} - {subtitle_el.get_text(strip=True)}"

        price: Optional[float] = None
        raw_price: Optional[str] = None
        price_el = soup.select_one(".pip-temp-price__sr-text") or soup.select_one(".pip-price__sr-text")
        if price_el:
            raw_price = price_el.get_text(strip=True)
            price = parse_price(raw_price)

        if price is None:
            integer_el = soup.select_one(".pip-price__integer")
            decimals_el = soup.select_one(".pip-price__decimals")
            if integer_el:
                int_part = integer_el.get_text(strip=True)
                dec_part = decimals_el.get_text(strip=True) if decimals_el else "00"
                raw_price = f"{int_part},{dec_part} €"
                price = parse_price(f"{int_part}.{dec_part}")

        if price is None:
            return None

        # Image
        img_el = soup.select_one(".pip-image")
        image_url = img_el.get("src") if img_el else None

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

    async def search(self, query: str, limit: int = 5) -> List[ScrapedProduct]:
        """Search products on Ikea Italy catalog."""
        search_url = "https://sik.search.blue.cdtapps.com/it/it/search"
        payload = {
            "searchParameters": {"input": query},
            "isUserLoggedIn": False,
            "components": [
                {
                    "component": "PRIMARY_AREA",
                    "columns": 4,
                    "types": {"main": "PRODUCT", "breakouts": []},
                    "window": {"offset": 0, "size": limit},
                }
            ],
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(search_url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    results: List[ScrapedProduct] = []
                    for area in data.get("results", []):
                        for item in area.get("items", []):
                            prod = item.get("product", {})
                            if not prod:
                                continue
                            name = prod.get("name", "")
                            type_name = prod.get("typeName", "")
                            title = f"{name} {type_name}".strip() if type_name else name
                            sales_price = prod.get("salesPrice", {})
                            num_price = sales_price.get("numeral")
                            if num_price is None:
                                continue
                            pip_url = prod.get("pipUrl", "")
                            image = prod.get("mainImageUrl", "")

                            results.append(
                                ScrapedProduct(
                                    title=title,
                                    price=float(num_price),
                                    currency="EUR",
                                    url=pip_url,
                                    store=self.name,
                                    image_url=image,
                                    is_available=True,
                                    sku=prod.get("id"),
                                    raw_price=f"{num_price} €",
                                )
                            )
                            if len(results) >= limit:
                                return results
                    return results
        except Exception:
            pass

        return []
