from __future__ import annotations
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.orm import relationship
from app.core.base import Base #type: ignore
from app.core.fields import field #type: ignore

class Session(Base):
    __tablename__ = "community_events_session"
    __abstract__ = False
    __model__ = "session"
    __service__ = "modules.community_events.services.event.SessionService"

    event_id = field(
        Integer,
        ForeignKey("community_events_event.id", ondelete="CASCADE"),
        required=True,
        public=True,
        editable=True
        )
    title = field(
        String(200),
        required=True,
        public=True,
        editable=True
        )
    start_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        editable=True
        )
    end_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        editable=True
        )
    speaker_name = field(
        String(150),
        required=False,
        public=True,
        editable=True
        )
    room = field(
        String(100),
        required=False,
        public=True,
        editable=True
        )
    capacity = field(
        Integer,
        required=False,
        public=True,
        editable=True
        )
    status = field(
        String(20),
        required=True,
        default="active",
        public=True,
        editable=True
        )
