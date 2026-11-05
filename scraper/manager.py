"""Unified Scraper Manager to orchestrate all store scrapers."""

import asyncio
from typing import List, Optional
from scraper.base import BaseScraper
from scraper.models import ScrapedProduct
from scraper.amazon import AmazonScraper
from scraper.ikea import IkeaScraper
from scraper.generic import GenericScraper


class ScraperManager:
    def __init__(self):
        # Specific scrapers first, generic fallback last
        self.specific_scrapers: List[BaseScraper] = [
            AmazonScraper(),
            IkeaScraper(),
        ]
        self.fallback_scraper = GenericScraper()

    def get_scraper_for_url(self, url: str) -> BaseScraper:
        """Finds the best scraper for a given URL."""
        for scraper in self.specific_scrapers:
            if scraper.can_handle(url):
                return scraper
        return self.fallback_scraper

    async def get_product_from_url(self, url: str) -> Optional[ScrapedProduct]:
        """Extracts product details from any supported product page URL."""
        scraper = self.get_scraper_for_url(url)
        product = await scraper.get_product_details(url)
        # If specific scraper failed (e.g. anti-bot/structure change), try generic fallback
        if not product and scraper != self.fallback_scraper:
            product = await self.fallback_scraper.get_product_details(url)
        return product

    async def search_all(self, query: str, limit_per_store: int = 5) -> List[ScrapedProduct]:
        """Searches across all scrapers that support keyword search."""
        tasks = [
            scraper.search(query, limit=limit_per_store)
            for scraper in self.specific_scrapers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        aggregated: List[ScrapedProduct] = []
        for res in results:
            if isinstance(res, list):
                aggregated.extend(res)
        return aggregated

