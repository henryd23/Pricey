"""Database models and schemas for Pricey."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ==========================================
# Database Tables (SQLModel)
# ==========================================

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)

    # Relationships
    monitored_items: List["MonitoredItem"] = Relationship(back_populates="user", cascade_delete=True)
    notifications: List["Notification"] = Relationship(back_populates="user", cascade_delete=True)


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    brand: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)

    # Relationships
    items: List["MonitoredItem"] = Relationship(back_populates="product", cascade_delete=True)


class MonitoredItem(SQLModel, table=True):
    __tablename__ = "monitored_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    product_id: Optional[int] = Field(default=None, foreign_key="products.id")
    url: str = Field(index=True)
    store_name: str = Field(index=True)
    title: str
    image_url: Optional[str] = Field(default=None)
    
    initial_price: float
    current_price: float
    lowest_price: float
    currency: str = Field(default="EUR")
    
    # User alert configuration (default 5% price drop)
    target_delta_percent: float = Field(default=5.0)
    
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    last_checked_at: datetime = Field(default_factory=utc_now)

    # Relationships
    user: Optional[User] = Relationship(back_populates="monitored_items")
    product: Optional[Product] = Relationship(back_populates="items")
    price_history: List["PriceHistory"] = Relationship(
        back_populates="item", cascade_delete=True
    )
    notifications: List["Notification"] = Relationship(
        back_populates="item", cascade_delete=True
    )


class PriceHistory(SQLModel, table=True):
    __tablename__ = "price_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="monitored_items.id", index=True)
    price: float
    timestamp: datetime = Field(default_factory=utc_now, index=True)

    # Relationship
    item: Optional[MonitoredItem] = Relationship(back_populates="price_history")


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    item_id: int = Field(foreign_key="monitored_items.id", index=True)
    message: str
    old_price: float
    new_price: float
    delta_percent: float
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utc_now)

    # Relationship
    user: Optional[User] = Relationship(back_populates="notifications")
    item: Optional[MonitoredItem] = Relationship(back_populates="notifications")


# ==========================================
# API Request / Response Schemas (Pydantic)
# ==========================================

class UserRegister(SQLModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

    # Relationship
    item: Optional[MonitoredItem] = Relationship(back_populates="notifications")


# ==========================================
# API Request / Response Schemas (Pydantic)
# ==========================================

class SearchRequest(SQLModel):
    query: str
    limit: int = 5
    max_price: Optional[float] = None


class LookupUrlRequest(SQLModel):
    url: str


class TrackItemRequest(SQLModel):
    url: str
    target_delta_percent: float = 5.0
    title: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    store_name: Optional[str] = None


class PriceHistoryRead(SQLModel):
    id: int
    price: float
    timestamp: datetime


class MonitoredItemRead(SQLModel):
    id: int
    url: str
    store_name: str
    title: str
    image_url: Optional[str]
    initial_price: float
    current_price: float
    lowest_price: float
    currency: str
    target_delta_percent: float
    is_active: bool
    created_at: datetime
    last_checked_at: datetime


class MonitoredItemDetail(MonitoredItemRead):
    price_history: List[PriceHistoryRead] = []


class NotificationRead(SQLModel):
    id: int
    item_id: int
    message: str
    old_price: float
    new_price: float
    delta_percent: float
    is_read: bool
    created_at: datetime
