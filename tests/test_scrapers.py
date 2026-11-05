"""Tests for scraper utilities and parsing."""

import pytest
from scraper.utils import parse_price
from scraper.manager import ScraperManager
from scraper.amazon import AmazonScraper
from scraper.ikea import IkeaScraper
from scraper.apple import AppleScraper


def test_parse_price_formats():
    assert parse_price("19,99 €") == 19.99
    assert parse_price("€ 1.299,00") == 1299.00
    assert parse_price("99.95") == 99.95
    assert parse_price("1,450.50 €") == 1450.50
    assert parse_price("5 €") == 5.0
    assert parse_price("Non disponibile") is None
    assert parse_price("") is None


def test_scraper_dispatch():
    manager = ScraperManager()
    
    amazon_url = "https://www.amazon.it/dp/B08N5WRWNW"
    ikea_url = "https://www.ikea.com/it/it/p/billy-libreria-bianco-00263850/"
    apple_url = "https://www.apple.com/it/shop/buy-iphone/iphone-15"
    random_url = "https://www.kasanova.com/it/prodotto-test.html"

    assert isinstance(manager.get_scraper_for_url(amazon_url), AmazonScraper)
    assert isinstance(manager.get_scraper_for_url(ikea_url), IkeaScraper)
    assert isinstance(manager.get_scraper_for_url(apple_url), AppleScraper)
    assert manager.get_scraper_for_url(random_url) == manager.fallback_scraper


def test_generic_scraper_meta_extraction():
    from scraper.generic import GenericScraper
    from bs4 import BeautifulSoup
    
    html = """
    <html>
      <head>
        <meta property="og:title" content="Lampada da Tavolo Elegante" />
        <meta property="product:price:amount" content="24.90" />
        <meta property="og:image" content="https://store.test/img.jpg" />
      </head>
      <body></body>
    </html>
    """
    scraper = GenericScraper()
    # Mocking internal fetch
    import asyncio
    
    async def mock_fetch():
        scraper._fetch_html = lambda url: asyncio.sleep(0, result=html)
        prod = await scraper.get_product_details("https://store.test/lampada")
        assert prod is not None
        assert prod.title == "Lampada da Tavolo Elegante"
        assert prod.price == 24.90
        assert prod.image_url == "https://store.test/img.jpg"

    asyncio.run(mock_fetch())
