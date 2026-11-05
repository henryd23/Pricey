"""Utility functions and HTTP helpers for scrapers."""

import re
from typing import Optional, Dict

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def parse_price(price_str: Optional[str]) -> Optional[float]:
    """
    Parses a price string with European (e.g. '1.299,99 €') or US format ('$1,299.99')
    into a clean float.
    """
    if not price_str:
        return None

    cleaned = price_str.strip()
    # Remove currency symbols and letters
    cleaned = re.sub(r"[^\d,\.]", "", cleaned)
    if not cleaned:
        return None

    # European format: 1.234,56 -> 1234.56
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            # Dot is thousands separator, comma is decimal
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # Comma is thousands separator, dot is decimal
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # Check if comma is decimal (e.g. 19,99)
        cleaned = cleaned.replace(",", ".")
    
    try:
        val = float(cleaned)
        return round(val, 2)
    except ValueError:
        return None
