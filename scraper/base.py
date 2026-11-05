"""Abstract base class for all store scrapers."""

from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
from scraper.models import ScrapedProduct
from scraper.utils import DEFAULT_HEADERS


class BaseScraper(ABC):
    name: str = "Base"
    base_url: str = ""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return True if this scraper can process the given URL."""
        pass

    @abstractmethod
    async def get_product_details(self, url: str) -> Optional[ScrapedProduct]:
        """Fetch and extract product information from a specific product page URL."""
        pass

    async def search(self, query: str, limit: int = 5) -> List[ScrapedProduct]:
        """
        Search for products by query text.
        Override in subclasses if store search scraping is supported.
        """
        return []

    async def _fetch_html(self, url: str, extra_headers: Optional[dict] = None) -> Optional[str]:
        """Utility to safely fetch HTML with custom browser headers."""
        headers = {**DEFAULT_HEADERS}
        if extra_headers:
            headers.update(extra_headers)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.text
                return None
        except Exception:
            return None
