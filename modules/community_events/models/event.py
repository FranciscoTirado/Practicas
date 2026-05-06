from __future__ import annotations
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.orm import relationship
from app.core.base import Base #type: ignore
from app.core.fields import field #type: ignore

class Event(Base):
    __tablename__ = "community_events_event"
    __abstract__ = False
    __model__ = "event"
    __service__ = "modules.community_events.services.event.EventService"

    title = field(
        String(200),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Título del evento"}
        )
    slug = field(
        String(200),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Enlace"}
        )
    summary = field(
        String(500),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Resumen"}
        )
    description = field(Text,
        required=False,
        public=True,
        editable=True,
        info = {"label": "Descripción"}
        )
    status = field(
        String(20),
        required=True,
        default="draft",
        public=True,
        editable=True,
        info={"choices": [
            {"label": "Borrador", "value": "draft"},
            {"label": "Publicado", "value": "published"},
            {"label": "Cerrado", "value": "closed"},
            {"label": "Cancelado", "value": "cancelled"}
        ]}
    )
    start_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Comienzo"}
        )
    end_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Termina"}
        )
    location = field(
        String(255),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Localización"}
        )
    capacity_total = field(
        Integer,
        required=True,
        default=0,
        public=True,
        editable=True,
        info = {"label": "Capacidad total"}
        )
    is_public = field(
        Boolean,
        required=True,
        default=False,
        public=True,
        editable=True,
        info = {"label": "Evento público"}
        )
    organizer_user_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Organizado por"}
        )
    sessions = relationship(
        "modules.community_events.models.session.Session",
        cascade="all, delete-orphan"
        )
    registrations = relationship(
        "modules.community_events.models.registration.Registration",
        cascade="all, delete-orphan"
        )

