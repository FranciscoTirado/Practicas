from __future__ import annotations
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.orm import relationship
from app.core.base import Base #type: ignore
from app.core.fields import field #type: ignore

class Registration(Base):
    __tablename__ = "community_events_registration"
    __abstract__ = False
    __model__ = "registration"
    __service__ = "modules.community_events.services.registration.RegistrationService"

    event_id = field(
        Integer,
        ForeignKey("community_events_event.id", ondelete="CASCADE"),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Id del evento"}
        )
    session_id = field(
        Integer,
        ForeignKey("community_events_session.id", ondelete="SET NULL"),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Id de la sesión"}
        )

    attendee_name = field(
        String(150),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Nombre del asistente"}
        )
    attendee_email = field(
        String(150),
        required=True,
        public=True,
        editable=True,
        info = {"label": "Email del asistente"}
        )
    attendee_user_id = field(
        UUID,
        ForeignKey("core_user.id", ondelete="SET NULL"),
        required=False,
        public=True,
        editable=True,
        info = {"label": "Usuario del asistente"}
        )
    status = field(
        String(20),
        required=True,
        default="pending",
        public=True,
        editable=True,
        info={"choices": [
            {"label": "Pendiente", "value": "pending"},
            {"label": "Confirmado", "value": "confirmed"},
            {"label": "Lista de Espera", "value": "waitlist"},
            {"label": "Cancelado", "value": "cancelled"}
        ]}
    )
    registered_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        info = {"label": "Fecha de registro(dd/mm/aaaa)"}
        )
    checkin_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        info = {"label": "Fecha de check-in(dd/mm/aaaa)"}
        )
    notes = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info = {"label": "Notas del registro"}
        )