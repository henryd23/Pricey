"""Tests for background checker and price drop detection logic."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

from backend.app.main import app
from backend.app.database import get_session
from backend.app.models import MonitoredItem, PriceHistory, Notification, utc_now
from backend.app.services.checker import check_all_monitored_items
from scraper.models import ScrapedProduct


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_price_decrease_triggers_notification():
    import asyncio

    async def run_test():
        # Setup in-memory engine for checker
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            item = MonitoredItem(
                url="https://store.test/tv-oled",
                store_name="TestStore",
                title="Smart TV 55 pollici",
                initial_price=1000.0,
                current_price=1000.0,
                lowest_price=1000.0,
                target_delta_percent=10.0,  # Alert at 10% drop
                is_active=True,
                created_at=utc_now(),
                last_checked_at=utc_now(),
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            item_id = item.id

        # Mock scraper returning a dropped price (850€ -> 15% drop)
        mock_product = ScrapedProduct(
            title="Smart TV 55 pollici",
            price=850.0,
            currency="EUR",
            url="https://store.test/tv-oled",
            store="TestStore",
        )

        with patch("backend.app.services.checker.engine", engine):
            with patch(
                "backend.app.services.checker.scraper_manager.get_product_from_url",
                new=AsyncMock(return_value=mock_product),
            ):
                stats = await check_all_monitored_items()

                assert stats["checked"] == 1
                assert stats["price_changes"] == 1
                assert stats["drops_detected"] == 1
                assert stats["notifications_generated"] == 1

        # Verify database state
        with Session(engine) as session:
            updated_item = session.get(MonitoredItem, item_id)
            assert updated_item.current_price == 850.0
            assert updated_item.lowest_price == 850.0

            # Check notification
            notifs = session.exec(select(Notification)).all()
            assert len(notifs) == 1
            assert notifs[0].delta_percent == 15.0
            assert notifs[0].old_price == 1000.0
            assert notifs[0].new_price == 850.0

            # Check price history
            hist = session.exec(select(PriceHistory)).all()
            assert len(hist) == 1
            assert hist[0].price == 850.0

    asyncio.run(run_test())


def test_price_decrease_below_threshold_does_not_notify():
    import asyncio

    async def run_test():
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            item = MonitoredItem(
                url="https://store.test/cuffie",
                store_name="TestStore",
                title="Cuffie Bluetooth",
                initial_price=100.0,
                current_price=100.0,
                lowest_price=100.0,
                target_delta_percent=10.0,  # Alert at 10% drop
                is_active=True,
                created_at=utc_now(),
                last_checked_at=utc_now(),
            )
            session.add(item)
            session.commit()

        # Mock scraper returning only a 5% drop (95€), threshold is 10%
        mock_product = ScrapedProduct(
            title="Cuffie Bluetooth",
            price=95.0,
            currency="EUR",
            url="https://store.test/cuffie",
            store="TestStore",
        )

        with patch("backend.app.services.checker.engine", engine):
            with patch(
                "backend.app.services.checker.scraper_manager.get_product_from_url",
                new=AsyncMock(return_value=mock_product),
            ):
                stats = await check_all_monitored_items()

                assert stats["checked"] == 1
                assert stats["price_changes"] == 1
                assert stats["drops_detected"] == 1
                assert stats["notifications_generated"] == 0  # Below 10%, no alert

        with Session(engine) as session:
            notifs = session.exec(select(Notification)).all()
            assert len(notifs) == 0

    asyncio.run(run_test())


def test_manual_check_now_endpoint(client: TestClient):
    with patch(
        "backend.app.routes.tracking.check_all_monitored_items",
        new=AsyncMock(
            return_value={
                "checked": 2,
                "price_changes": 1,
                "drops_detected": 1,
                "notifications_generated": 1,
                "errors": 0,
            }
        ),
    ):
        res = client.post("/api/tracked/check-now")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["stats"]["checked"] == 2
        assert data["stats"]["notifications_generated"] == 1
