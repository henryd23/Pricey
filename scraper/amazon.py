"""Amazon scraper implementation for Pricey."""

import re
from typing import List, Optional
from bs4 import BeautifulSoup
from scraper.base import BaseScraper
from scraper.models import ScrapedProduct
from scraper.utils import parse_price


class AmazonScraper(BaseScraper):
    name: str = "Amazon"
    base_url: str = "https://www.amazon.it"

    def can_handle(self, url: str) -> bool:
        return "amazon." in url.lower() or "amzn.eu" in url.lower() or "amzn.to" in url.lower()

    def _extract_asin(self, url: str) -> Optional[str]:
        match = re.search(r"/(?:dp|gp/product|d)/([A-Z0-9]{10})", url)
        if match:
            return match.group(1)
        match_end = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
        return match_end.group(1) if match_end else None

    async def get_product_details(self, url: str) -> Optional[ScrapedProduct]:
        html = await self._fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # 1. Title
        title_el = soup.select_one("#productTitle") or soup.select_one("#title")
        if not title_el:
            # Check if captcha / bot block
            if "Type the characters you see in this image" in html or "api-services-support@amazon.com" in html:
                return None
            return None
        title = title_el.get_text(strip=True)

        # 2. Price
        price: Optional[float] = None
        raw_price: Optional[str] = None
        price_selectors = [
            ".priceToPay span.a-offscreen",
            ".apexPriceToPay span.a-offscreen",
            ".corePriceDisplay_desktop_feature_div span.a-offscreen",
            "#corePrice_desktop span.a-offscreen",
            ".a-price.aok-align-center span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#priceblock_saleprice",
            ".a-price span.a-offscreen",
        ]

        for selector in price_selectors:
            el = soup.select_one(selector)
            if el and el.get_text(strip=True):
                raw = el.get_text(strip=True)
                val = parse_price(raw)
                if val is not None and val > 0:
                    price = val
                    raw_price = raw
                    break

        if price is None:
            # Fallback for whole + fraction parts
            whole_el = soup.select_one(".a-price-whole")
            fraction_el = soup.select_one(".a-price-fraction")
            if whole_el:
                whole = whole_el.get_text(strip=True).replace(".", "").replace(",", "")
                fraction = fraction_el.get_text(strip=True) if fraction_el else "00"
                price = parse_price(f"{whole}.{fraction}")
                raw_price = f"{whole},{fraction} €"

        if price is None:
            return None

        # 3. Image
        image_url = None
        img_el = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-old-hires")

        # 4. Availability
        avail_el = soup.select_one("#availability span")
        avail_text = avail_el.get_text(strip=True).lower() if avail_el else ""
        is_available = not ("non disponibile" in avail_text or "attualmente non disponibile" in avail_text)

        asin = self._extract_asin(url)
        canonical_url = f"https://www.amazon.it/dp/{asin}" if asin else url

        return ScrapedProduct(
            title=title,
            price=price,
            currency="EUR",
            url=canonical_url,
            store=self.name,
            image_url=image_url,
            is_available=is_available,
            sku=asin,
            raw_price=raw_price,
        )

    async def search(self, query: str, limit: int = 5) -> List[ScrapedProduct]:
        search_url = f"{self.base_url}/s?k={httpx._utils.quote(query)}"
        html = await self._fetch_html(search_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div[data-component-type='s-search-result']")
        results: List[ScrapedProduct] = []

        for item in items:
            if len(results) >= limit:
                break

            asin = item.get("data-asin")
            if not asin:
                continue

            # Title
            title_el = item.select_one("h2 a span") or item.select_one("h2")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)

            # Price
            price_el = item.select_one(".a-price .a-offscreen")
            if not price_el:
                continue
            raw_price = price_el.get_text(strip=True)
            price = parse_price(raw_price)
            if price is None:
                continue

            # Image
            img_el = item.select_one("img.s-image")
            image_url = img_el.get("src") if img_el else None

            prod_url = f"{self.base_url}/dp/{asin}"

            results.append(
                ScrapedProduct(
                    title=title,
                    price=price,
                    currency="EUR",
                    url=prod_url,
                    store=self.name,
                    image_url=image_url,
                    is_available=True,
                    sku=asin,
                    raw_price=raw_price,
                )
            )

        return results

