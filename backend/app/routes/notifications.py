"""In-app notifications endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select, func
from backend.app.database import get_session
from backend.app.models import Notification, NotificationRead

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


class UnreadCountResponse(BaseModel):
    unread_count: int


@router.get("", response_model=List[NotificationRead])
def list_notifications(
    unread_only: bool = False,
    session: Session = Depends(get_session),
):
    """List notifications generated when price drops occur (US-11)."""
    statement = select(Notification)
    if unread_only:
        statement = statement.where(Notification.is_read == False)
    statement = statement.order_by(Notification.created_at.desc())
    return session.exec(statement).all()


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(session: Session = Depends(get_session)):
    """Count of unread notifications for badge counter."""
    statement = select(func.count(Notification.id)).where(Notification.is_read == False)
    count = session.exec(statement).one()
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_as_read(notification_id: int, session: Session = Depends(get_session)):
    """Mark a specific notification as read."""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
def mark_all_as_read(session: Session = Depends(get_session)):
    """Mark all unread notifications as read."""
    statement = select(Notification).where(Notification.is_read == False)
    notifications = session.exec(statement).all()
    for n in notifications:
        n.is_read = True
        session.add(n)
    session.commit()
    return {"message": f"Marked {len(notifications)} notifications as read"}
