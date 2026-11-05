"""Integration tests for User Management and Authentication (US-12, US-13)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from backend.app.main import app
from backend.app.database import get_session


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


def test_user_registration_and_validation(client: TestClient):
    # 1. Invalid email
    bad_email = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password123", "full_name": "Mario Rossi"},
    )
    assert bad_email.status_code == 400

    # 2. Short password
    bad_pass = client.post(
        "/api/auth/register",
        json={"email": "mario@example.com", "password": "123", "full_name": "Mario Rossi"},
    )
    assert bad_pass.status_code == 400

    # 3. Successful registration (US-12)
    reg_res = client.post(
        "/api/auth/register",
        json={"email": "mario@example.com", "password": "securepassword", "full_name": "Mario Rossi"},
    )
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "mario@example.com"
    assert data["user"]["full_name"] == "Mario Rossi"

    # 4. Duplicate registration should return 409
    dup_res = client.post(
        "/api/auth/register",
        json={"email": "mario@example.com", "password": "anotherpassword"},
    )
    assert dup_res.status_code == 409


def test_user_login_and_profile(client: TestClient):
    # Register user first
    client.post(
        "/api/auth/register",
        json={"email": "luigi@example.com", "password": "mypassword123", "full_name": "Luigi"},
    )

    # 1. Wrong password
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "luigi@example.com", "password": "wrongpassword"},
    )
    assert bad_login.status_code == 401

    # 2. Unknown user
    unknown_login = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "password"},
    )
    assert unknown_login.status_code == 401

    # 3. Successful login (US-13)
    login_res = client.post(
        "/api/auth/login",
        json={"email": "luigi@example.com", "password": "mypassword123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # 4. Access /api/auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "luigi@example.com"

    # 5. Access without token should fail
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401


def test_user_tracked_items_isolation(client: TestClient):
    # Register User 1
    u1_res = client.post(
        "/api/auth/register",
        json={"email": "user1@example.com", "password": "password123"},
    )
    token1 = u1_res.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Register User 2
    u2_res = client.post(
        "/api/auth/register",
        json={"email": "user2@example.com", "password": "password123"},
    )
    token2 = u2_res.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 1 tracks product A
    client.post(
        "/api/tracked",
        headers=headers1,
        json={
            "url": "https://store.test/p1",
            "title": "Product 1",
            "price": 50.0,
            "store_name": "TestStore",
        },
    )

    # User 1 sees 1 product
    list1 = client.get("/api/tracked", headers=headers1).json()
    assert len(list1) == 1
    assert list1[0]["title"] == "Product 1"

    # User 2 sees 0 products (isolated)
    list2 = client.get("/api/tracked", headers=headers2).json()
    assert len(list2) == 0
