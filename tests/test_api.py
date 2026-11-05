"""Integration tests for Pricey FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from backend.app.main import app
from backend.app.database import get_session
from backend.app.models import Notification


@pytest.fixture(name="session")
def session_fixture():
    # In-memory SQLite for tests
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


def test_home_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_search_and_lookup_endpoints(client: TestClient):
    # Empty query should fail
    bad_res = client.post("/api/search", json={"query": "   "})
    assert bad_res.status_code == 400

    # Search with max price
    search_res = client.post(
        "/api/search", json={"query": "billy", "limit": 3, "max_price": 50.0}
    )
    assert search_res.status_code == 200
    results = search_res.json()
    assert isinstance(results, list)
    for prod in results:
        assert prod["price"] <= 50.0

    # Direct URL lookup
    ikea_url = "https://www.ikea.com/it/it/p/billy-libreria-bianco-20522046/"
    lookup_res = client.post("/api/lookup-url", json={"url": ikea_url})
    assert lookup_res.status_code == 200
    prod_data = lookup_res.json()
    assert "BILLY" in prod_data["title"]
    assert prod_data["price"] > 0
    assert prod_data["store"] == "Ikea"


def test_track_and_manage_item(client: TestClient):
    # 1. Add tracked item
    payload = {
        "url": "https://www.ikea.com/it/it/p/billy-libreria-bianco-20522046/",
        "title": "BILLY Libreria - bianco 80x28x202 cm",
        "price": 59.95,
        "store_name": "Ikea",
        "image_url": "https://www.ikea.com/img.jpg",
        "target_delta_percent": 10.0,
    }
    create_res = client.post("/api/tracked", json=payload)
    assert create_res.status_code == 201
    item = create_res.json()
    assert item["id"] is not None
    assert item["title"] == payload["title"]
    assert item["current_price"] == 59.95
    assert item["target_delta_percent"] == 10.0
    item_id = item["id"]

    # 2. Duplicate tracking should return 409
    dup_res = client.post("/api/tracked", json=payload)
    assert dup_res.status_code == 409

    # 3. List tracked items
    list_res = client.get("/api/tracked")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 1
    assert items[0]["id"] == item_id

    # 4. Get item detail with price history
    detail_res = client.get(f"/api/tracked/{item_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["price_history"]) == 1
    assert detail["price_history"][0]["price"] == 59.95

    # 5. Update threshold
    patch_res = client.patch(
        f"/api/tracked/{item_id}/threshold", json={"target_delta_percent": 15.0}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["target_delta_percent"] == 15.0

    # 6. Delete item
    del_res = client.delete(f"/api/tracked/{item_id}")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get(f"/api/tracked/{item_id}")
    assert get_res.status_code == 404


def test_notifications_lifecycle(client: TestClient, session: Session):
    # Setup dummy tracked item & notification directly
    from backend.app.models import MonitoredItem

    item = MonitoredItem(
        url="https://store.test/p1",
        store_name="TestStore",
        title="Test Product",
        initial_price=100.0,
        current_price=80.0,
        lowest_price=80.0,
        target_delta_percent=5.0,
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    notif = Notification(
        item_id=item.id,
        message="Price dropped by 20% on Test Product!",
        old_price=100.0,
        new_price=80.0,
        delta_percent=20.0,
        is_read=False,
    )
    session.add(notif)
    session.commit()
    session.refresh(notif)

    # 1. Check unread count
    res_count = client.get("/api/notifications/unread-count")
    assert res_count.status_code == 200
    assert res_count.json()["unread_count"] == 1

    # 2. List notifications
    res_list = client.get("/api/notifications?unread_only=true")
    assert res_list.status_code == 200
    notifs = res_list.json()
    assert len(notifs) == 1
    assert notifs[0]["delta_percent"] == 20.0

    # 3. Mark as read
    res_read = client.patch(f"/api/notifications/{notif.id}/read")
    assert res_read.status_code == 200
    assert res_read.json()["is_read"] is True

    # 4. Check unread count is now 0
    res_count2 = client.get("/api/notifications/unread-count")
    assert res_count2.json()["unread_count"] == 0
