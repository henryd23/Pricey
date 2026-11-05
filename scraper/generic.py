"""Generic OpenGraph and Schema.org scraper for arbitrary e-commerce URLs."""

import json
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from scraper.base import BaseScraper
from scraper.models import ScrapedProduct
from scraper.utils import parse_price


class GenericScraper(BaseScraper):
    name: str = "Web"

    def can_handle(self, url: str) -> bool:
        return True  # Fallback handler

    async def get_product_details(self, url: str) -> Optional[ScrapedProduct]:
        html = await self._fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        parsed_domain = urlparse(url).netloc.replace("www.", "").capitalize()

        # 1. Check JSON-LD schema
        scripts = soup.find_all("script", type="application/ld+json")
        for s in scripts:
            try:
                raw_text = s.string or s.get_text()
                if not raw_text:
                    continue
                data = json.loads(raw_text)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") in ["Product", "IndividualProduct"]:
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
                        price_val = offers.get("price") or offers.get("lowPrice")
                        currency = offers.get("priceCurrency", "EUR")

                        if title and price_val is not None:
                            val = parse_price(str(price_val))
                            if val is not None:
                                return ScrapedProduct(
                                    title=title,
                                    price=val,
                                    currency=currency,
                                    url=url,
                                    store=parsed_domain,
                                    image_url=image,
                                    is_available=True,
                                    sku=item.get("sku"),
                                    raw_price=f"{price_val} {currency}",
                                )
            except Exception:
                continue

        # 2. Check OpenGraph / meta tags
        og_title = (
            soup.select_one('meta[property="og:title"]')
            or soup.select_one('meta[name="twitter:title"]')
        )
        title = og_title.get("content") if og_title else None
        if not title and soup.title:
            title = soup.title.get_text(strip=True)

        og_image = (
            soup.select_one('meta[property="og:image"]')
            or soup.select_one('meta[name="twitter:image"]')
        )
        image_url = og_image.get("content") if og_image else None

        og_price = (
            soup.select_one('meta[property="product:price:amount"]')
            or soup.select_one('meta[property="og:price:amount"]')
            or soup.select_one('meta[name="price"]')
        )
        price_val = og_price.get("content") if og_price else None
        price = parse_price(price_val) if price_val else None

        # 3. Fallback to common CSS classes
        if price is None:
            common_selectors = [
                '[data-price]',
                '.price',
                '.product-price',
                '#product-price',
                '.current-price',
                '.sales-price',
                '.special-price',
            ]
            for sel in common_selectors:
                el = soup.select_one(sel)
                if el:
                    p = parse_price(el.get("data-price") or el.get_text(strip=True))
                    if p is not None and p > 0:
                        price = p
                        break

        if not title or price is None:
            return None

        return ScrapedProduct(
            title=title,
            price=price,
            currency="EUR",
            url=url,
            store=parsed_domain,
            image_url=image_url,
            is_available=True,
            sku=None,
            raw_price=str(price),
        )
