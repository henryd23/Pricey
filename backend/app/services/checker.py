"""Service responsible for periodic checking of monitored product prices."""

import sys
from pathlib import Path
from typing import Dict, Any, List
from sqlmodel import Session, select

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scraper.manager import ScraperManager
from backend.app.database import engine
from backend.app.models import MonitoredItem, PriceHistory, Notification, utc_now
from backend.app.services.email_service import send_price_drop_email

scraper_manager = ScraperManager()


async def check_all_monitored_items() -> Dict[str, Any]:
    """
    Checks all active monitored products, records price history,
    and creates alerts if the price drop exceeds the target threshold (US-07, US-10).
    """
    stats = {
        "checked": 0,
        "price_changes": 0,
        "drops_detected": 0,
        "notifications_generated": 0,
        "errors": 0,
    }

    with Session(engine) as session:
        statement = select(MonitoredItem).where(MonitoredItem.is_active == True)
        items: List[MonitoredItem] = session.exec(statement).all()

        for item in items:
            try:
                stats["checked"] += 1
                scraped = await scraper_manager.get_product_from_url(item.url)

                if not scraped or scraped.price is None:
                    # Could be temporary connection issue or unavailable
                    continue

                new_price = scraped.price
                previous_price = item.current_price

                # Check if price changed
                if new_price != previous_price:
                    stats["price_changes"] += 1

                    # Record new price point in history
                    history_entry = PriceHistory(
                        item_id=item.id,
                        price=new_price,
                        timestamp=utc_now(),
                    )
                    session.add(history_entry)

                    # Check for price decrease
                    if new_price < previous_price:
                        delta_percent = ((previous_price - new_price) / previous_price) * 100
                        stats["drops_detected"] += 1

                        # US-10: Trigger alert if threshold reached or exceeded
                        if delta_percent >= item.target_delta_percent:
                            notif_msg = (
                                f"Il prezzo di '{item.title}' su {item.store_name} "
                                f"è sceso da {previous_price:.2f}€ a {new_price:.2f}€ "
                                f"(-{delta_percent:.1f}%)!"
                            )
                            notification = Notification(
                                user_id=item.user_id,
                                item_id=item.id,
                                message=notif_msg,
                                old_price=previous_price,
                                new_price=new_price,
                                delta_percent=round(delta_percent, 1),
                                is_read=False,
                                created_at=utc_now(),
                            )
                            session.add(notification)
                            stats["notifications_generated"] += 1

                            # Send email notification to user or default
                            recipient_email = "user@pricey.local"
                            if item.user and item.user.email:
                                recipient_email = item.user.email

                            send_price_drop_email(
                                to_email=recipient_email,
                                product_title=item.title,
                                store_name=item.store_name,
                                old_price=previous_price,
                                new_price=new_price,
                                delta_percent=delta_percent,
                                product_url=item.url,
                            )

                    # Update current and lowest price
                    item.current_price = new_price
                    item.lowest_price = min(item.lowest_price, new_price)

                # Always update last_checked_at timestamp
                item.last_checked_at = utc_now()
                session.add(item)
                session.commit()

            except Exception as e:
                stats["errors"] += 1
                print(f"[CHECKER ERROR] Failed to check item {item.id} ({item.title}): {e}")

    return stats

