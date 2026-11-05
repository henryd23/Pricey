"""Background scheduler setup using APScheduler."""

import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.app.services.checker import check_all_monitored_items

scheduler = AsyncIOScheduler()


async def scheduled_price_check():
    """Wrapper function executed on each scheduler trigger."""
    print("[SCHEDULER] Running scheduled price check cycle...")
    stats = await check_all_monitored_items()
    print(f"[SCHEDULER] Cycle finished: {stats}")


def start_scheduler():
    """Initializes and starts the periodic price checker scheduler."""
    interval_minutes = int(os.getenv("PRICE_CHECK_INTERVAL_MINUTES", "60"))

    # Add periodic recurring job
    scheduler.add_job(
        scheduled_price_check,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="price_check_job",
        name="Periodic Price Check",
        replace_existing=True,
    )

    if not scheduler.running:
        scheduler.start()
        print(f"[SCHEDULER] Started periodic price check job every {interval_minutes} minutes.")


def stop_scheduler():
    """Shuts down the background scheduler cleanly."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[SCHEDULER] Scheduler stopped.")
