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
        editable=True,
        info = {"label": "Id del evento"}
        )
    title = field(
        String(200),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Título de la sesión"}
        )
    speaker_name = field(
        String(150),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Nombre del ponente"}
        )
    room = field(
        String(100),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Sala"}
        )
    capacity = field(
        Integer,
        required=False,
        public=True,
        editable=True,
        info = {"label": "Capacidad"}
        )
    status = field(
        String(20),
        required=True,
        default="active",
        public=True,
        editable=True,
        info = {"label": "Estado", "choices": [
             {"label": "Activa", "value": "active"},
             {"label": "Cancelada", "value": "cancelled"},
             {"label": "Finalizada", "value": "finished"},
        ]}
        )
