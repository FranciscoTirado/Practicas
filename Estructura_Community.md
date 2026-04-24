## /backend/
Archivo: `backend/modules/community_events/__init__.py`
```py
from . import models
from . import services
```
Archivo: `backend/modules/community_events/__manifest__.yaml`
```yml
name: "Community Events"
technical_name: "community_events"
version: "1.0.0"
category: "Community"
summary: "Gestión de eventos, sesiones internas e inscripciones de la comunidad."
depends:
  - core
  - ui
data:
  - data/ui_modules.yml
  - data/settings.yml
  - data/groups.yml
  - data/acl_rules.yml
  - views/views.yml
  - views/menu.yml
```

## /data/
Archivo: `backend/modules/community_events/data/acl_rules.yml`
```yml
- model: core.aclrule
  ext_id: ce_acl_staff_all
  fields:
    model_key: "community_events.*"
    group_id.ext_id: community_events_group_staff
    perm_read: true
    perm_write: true
    perm_create: true
    perm_delete: true

- model: core.aclrule
  ext_id: ce_acl_public_read_events
  fields:
    model_key: "community_events.event"
    group_id.ext_id: core.core_group_public
    perm_read: true
    domain:
      - { field: "status", operator: "=", value: "published" }
      - { field: "is_public", operator: "=", value: true }

- model: core.aclrule
  ext_id: ce_acl_public_create_registrations
  fields:
    model_key: "community_events.registration"
    group_id.ext_id: core.core_group_public
    perm_create: true
```
Archivo: `backend/modules/community_events/data/groups.yml`
```yml
- model: core.group
  ext_id: community_events_group_viewer
  fields:
    name: "Eventos | Lector"
    parent_id.ext_id: core.core_group_internal_user

- model: core.group
  ext_id: community_events_group_staff
  fields:
    name: "Eventos | Organizador - Staff"
    parent_id.ext_id: community_events_group_viewer
```
Archivo: `backend/modules/community_events/data/settings.yml`
```yml
- model: core.setting
  ext_id: ce_setting_allow_waitlist
  fields:
    key: "community_events.allow_waitlist"
    value: "true"
    type: "boolean"

- model: core.setting
  ext_id: ce_setting_default_capacity
  fields:
    key: "community_events.default_capacity"
    value: "100"
    type: "integer"

- model: core.setting
  ext_id: ce_setting_auto_confirm
  fields:
    key: "community_events.auto_confirm"
    value: "false"
    type: "boolean"

- model: core.setting
  ext_id: ce_setting_reminder_hours
  fields:
    key: "community_events.reminder_hours_before"
    value: "24"
    type: "integer"
```
Archivo: `backend/modules/community_events/data/ui_modules.yml`
```yml
- model: ui.uimodule
  ext_id: community_events_ui_module
  fields:
    slug: community_events
    name: Community Events
    description: "Gestión avanzada de eventos, sesiones e inscripciones públicas"
    icon: mdi-calendar-star
    active: true
```

## /models/
Archivo: `backend/modules/community_events/models/__init__.py`
```py
from .event import Event # noqa: F401
from .registration import Registration # noqa: F401
from .session import Session # noqa: F401
```
Archivo: `backend/modules/community_events/models/event.py`
```py
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

```
Archivo: `backend/modules/community_events/models/registration.py`
```py
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
        editable=True
        )
    session_id = field(
        Integer,
        ForeignKey("community_events_session.id", ondelete="SET NULL"),
        required=False,
        public=True,
        editable=True
        )
    
    attendee_name = field(
        String(150),
        required=True,
        public=True,
        editable=True
        )
    attendee_email = field(
        String(150),
        required=True,
        public=True,
        editable=True
        )
    attendee_user_id = field(
        UUID,
        ForeignKey("core_user.id", ondelete="SET NULL"),
        required=False,
        public=True,
        editable=True
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
        editable=False
        )
    checkin_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False
        )
    notes = field(
        Text,
        required=False,
        public=True,
        editable=True
        )
```
Archivo: `backend/modules/community_events/models/session.py`
```py
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

```

## /services/
Archivo: `backend/modules/community_events/services/__init__.py`
```py
from .event import EventService # noqa: F401
from .registration import RegistrationService # noqa: F401
```
Archivo: `backend/modules/community_events/services/event.py`
```py
from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService #type: ignore
from app.core.serializer import serialize #type: ignore
from app.core.services import exposed_action #type: ignore

class SessionService(BaseService):
    from ..models.session import Session

class EventService(BaseService):
    from ..models.event import Event

    def sanitize_dates(self, payload: dict) -> dict:
        import datetime as dt
        for key in ("start_at", "end_at"):
            raw_value = payload.get(key)
            if raw_value and isinstance(raw_value, str) and "/" in raw_value:
                try:
                    converted = dt.datetime.strptime(raw_value.split()[0], "%d/%m/%Y")
                    payload[key] = converted.replace(tzinfo=dt.timezone.utc)
                except ValueError:
                    pass
        return payload

    def create(self, obj):  # type: ignore[override]
        if not isinstance(obj, dict):
            return super().create(obj)
        data_copy = self.sanitize_dates(dict(obj))
        return super().create(data_copy)

    def update(self, id: int, obj):  # type: ignore[override]
        if not isinstance(obj, dict):
            return super().update(id, obj)
        data_copy = self.sanitize_dates(dict(obj))
        return super().update(id, data_copy)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def publish_event(self, id: int, note: str | None = None) -> dict:
        record = self.repo.session.get(self.Event, int(id))
        if record is None:
            raise HTTPException(404, "No se encontró el evento solicitado")

        record.status = "published"
        record.is_public = True
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def close_registration(self, id: int, reason: str | None = None) -> dict:
        record = self.repo.session.get(self.Event, int(id))
        if record is None:
            raise HTTPException(404, "El evento indicado no existe")

        record.status = "closed"
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def cancel_event(self, id: int, reason: str) -> dict:
        record = self.repo.session.get(self.Event, int(id))
        if record is None:
            raise HTTPException(404, "El evento especificado no fue hallado")

        record.status = "cancelled"
        record.is_public = False
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def reopen_event(self, id: int) -> dict:
        record = self.repo.session.get(self.Event, int(id))
        if record is None:
            raise HTTPException(404, "No existe un evento con ese identificador")

        record.status = "published"
        record.is_public = True
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

```
Archivo: `backend/modules/community_events/services/registration.py`
```py
from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService #type: ignore
from app.core.serializer import serialize #type: ignore
from app.core.services import exposed_action #type: ignore

class RegistrationService(BaseService):
    from ..models.registration import Registration

    def create(self, obj):
        if not isinstance(obj, dict):
            return super().create(obj)
        entry = dict(obj)
        entry["registered_at"] = dt.datetime.now(dt.timezone.utc)
        if "status" not in entry:
            entry["status"] = "pending"
        return super().create(entry)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def confirm(self, id: int, note: str | None = None) -> dict:
        record = self.repo.session.get(self.Registration, int(id))
        if record is None:
            raise HTTPException(404, "No se encontró la inscripción indicada")
        record.status = "confirmed"
        if note:
            record.notes = f"{record.notes or ''} | {note}".strip()
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def move_waitlist(self, id: int, note: str | None = None) -> dict:
        record = self.repo.session.get(self.Registration, int(id))
        if record is None:
            raise HTTPException(404, "La inscripción solicitada no existe")
        record.status = "waitlist"
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def checkin(self, id: int, source: str = "manual") -> dict:
        record = self.repo.session.get(self.Registration, int(id))
        if record is None:
            raise HTTPException(404, "No se pudo localizar la inscripción")
        if record.status not in ["confirmed", "pending"]:
            raise HTTPException(400, "El estado actual del registro no permite el acceso.")

        record.checkin_at = dt.datetime.now(dt.timezone.utc)
        record.notes = f"{record.notes or ''} [Checkin: {source}]".strip()
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)

    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def bulk_checkin(self, ids: list[int]) -> dict:
        validated = 0
        for reg_id in ids:
            entry = self.repo.session.get(self.Registration, int(reg_id))
            if entry and entry.status in ["confirmed", "pending"] and not entry.checkin_at:
                entry.checkin_at = dt.datetime.now(dt.timezone.utc)
                entry.notes = f"{entry.notes or ''} [Bulk Checkin]".strip()
                self.repo.session.add(entry)
                validated += 1
        self.repo.session.commit()
        return {"message": f"Se procesaron {validated} registros de acceso."}
```


## /tests/
Archivo: `backend/modules/community_events/tests/test_event.py`
```py
import pytest
import datetime as dt
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from modules.community_events.services.event import EventService
from modules.community_events.services.registration import RegistrationService
from modules.community_events.models.event import Event
from modules.community_events.models.registration import Registration

@pytest.fixture
def mock_event_service():
    instance = EventService(MagicMock())
    instance.repo = MagicMock()
    instance.repo.session = MagicMock()
    return instance

@pytest.fixture
def mock_registration_service():
    instance = RegistrationService(MagicMock())
    instance.repo = MagicMock()
    instance.repo.session = MagicMock()
    return instance


@patch("modules.community_events.services.event.serialize")
def test_publish_event_changes_status_and_visibility(mock_serialize, mock_event_service):
    event_stub = Event(id=1, status="draft", is_public=False)
    mock_event_service.repo.session.get.return_value = event_stub

    def _serialize_event(obj):
        return {"status": obj.status, "is_public": obj.is_public}

    mock_serialize.side_effect = _serialize_event

    response = mock_event_service.publish_event(id=1)

    assert response["status"] == "published"
    assert response["is_public"] is True
    mock_event_service.repo.session.commit.assert_called_once()


@patch("modules.community_events.services.event.serialize")
def test_cancel_event_hides_it_from_public(mock_serialize, mock_event_service):
    event_stub = Event(id=2, status="published", is_public=True)
    mock_event_service.repo.session.get.return_value = event_stub

    def _serialize_event(obj):
        return {"status": obj.status, "is_public": obj.is_public}

    mock_serialize.side_effect = _serialize_event

    response = mock_event_service.cancel_event(id=2, reason="Lluvia extrema")

    assert response["status"] == "cancelled"
    assert response["is_public"] is False
    mock_event_service.repo.session.commit.assert_called_once()


@patch("modules.community_events.services.registration_service.serialize")
def test_checkin_success_for_confirmed_user(mock_serialize, mock_registration_service):
    reg_stub = Registration(id=10, status="confirmed", checkin_at=None)
    mock_registration_service.repo.session.get.return_value = reg_stub

    def _serialize_reg(obj):
        return {"checkin_at": obj.checkin_at}

    mock_serialize.side_effect = _serialize_reg

    response = mock_registration_service.checkin(id=10, source="scanner")

    assert response["checkin_at"] is not None
    mock_registration_service.repo.session.commit.assert_called_once()


def test_checkin_fails_for_cancelled_user(mock_registration_service):
    reg_stub = Registration(id=11, status="cancelled", checkin_at=None)
    mock_registration_service.repo.session.get.return_value = reg_stub

    with pytest.raises(HTTPException) as raised_exc:
        mock_registration_service.checkin(id=11)

    http_error = raised_exc.value
    assert http_error.status_code == 400
    assert "El estado actual del registro no permite el acceso." in http_error.detail
    mock_registration_service.repo.session.commit.assert_not_called()
```

## /views/
Archivo: `backend/modules/community_events/views/menu.yml`
```yml
- model: ui.menuitem
  ext_id: ce_menu_root
  fields:
    title: "Eventos"
    icon: mdi-ticket-confirmation
    color_primary: "#FF5722"

# Menú: Eventos
- model: ui.action
  ext_id: ce_action_events
  fields:
    name: "Gestión de Eventos"
    route: community_events/events
    model_key: community_events.event
    model_path: "community_events/event"
    menu: true
    context:
      allowed_group_ext_ids: [community_events_group_staff, core_group_superadmin]
    default_multi_read_view_id.ext_id: ce_view_event_list
    default_single_edit_view_id.ext_id: ce_view_event_form

- model: ui.menuitem
  ext_id: ce_menu_events
  fields:
    title: "Eventos"
    icon: mdi-calendar-star
    parent_id.ext_id: ce_menu_root
    action_id.ext_id: ce_action_events

# Menú: Inscripciones
- model: ui.action
  ext_id: ce_action_registrations
  fields:
    name: "Inscripciones"
    route: community_events/registrations
    model_key: community_events.registration
    model_path: "community_events/registration"
    menu: true
    context:
      allowed_group_ext_ids: [community_events_group_staff, core_group_superadmin]
    default_multi_read_view_id.ext_id: ce_view_registration_list
    default_single_edit_view_id.ext_id: ce_view_registration_form

- model: ui.menuitem
  ext_id: ce_menu_registrations
  fields:
    title: "Inscripciones"
    icon: mdi-account-group
    parent_id.ext_id: ce_menu_root
    action_id.ext_id: ce_action_registrations
```
Archivo: `backend/modules/community_events/views/views.yml`
```yml
# ========================
# EVENTOS
# ========================
- model: ui.view
  ext_id: ce_view_event_list
  fields:
    name: "Eventos - Lista"
    model_key: community_events.event
    type_id.ext_id: ui.ui_view_type_list
    definition:
      columns:
        - { field: title, label: Título }
        - { field: start_at, label: Inicio }
        - { field: capacity_total, label: Aforo }
        - { field: status, label: Estado, chip: true }
      # Filtros rápidos predefinidos
      filters:
        - { name: "Publicados", domain: [{ field: "status", operator: "=", value: "published" }] }
        - { name: "Borradores", domain: [{ field: "status", operator: "=", value: "draft" }] }
      row_actions:
        - { key: publish, type: service, label: "Publicar", method: publish_event, icon: mdi-earth, hidden: "item.status !== 'draft'" }
        - { key: close, type: service, label: "Cerrar", method: close_registration, icon: mdi-door-closed, hidden: "item.status !== 'published'" }
      actions:
        - { name: new, type: create, icon: mdi-plus }
        - { name: edit, type: update, icon: mdi-pencil }

- model: ui.view
  ext_id: ce_view_event_form
  fields:
    name: "Eventos - Form"
    model_key: community_events.event
    type_id.ext_id: ui.ui_view_type_form
    definition:
      # BUTTONBOX: El acceso directo a las inscripciones desde dentro del evento
      buttonbox:
        - icon: mdi-ticket-account
          label: "Inscripciones"
          route: "community_events/registrations"
          query: { "event_id": "item.id" }
      groups:
        - label: Datos Generales
          fields: [title, slug, summary, description, is_public]
        - label: Logística
          fields: [start_at, end_at, location, capacity_total]
        - label: Administración
          fields: [status, organizer_user_id]
      form_actions:
        - key: cancel
          type: service
          label: "Cancelar Evento"
          method: cancel_event
          hidden: "item.status === 'cancelled'"
          params: [{ name: reason, label: "Motivo", type: string, required: true }]

# ========================
# INSCRIPCIONES (REGISTRATIONS)
# ========================
- model: ui.view
  ext_id: ce_view_registration_list
  fields:
    name: "Inscripciones - Lista"
    model_key: community_events.registration
    type_id.ext_id: ui.ui_view_type_list
    definition:
      columns:
        - { field: attendee_name, label: Asistente }
        - { field: attendee_email, label: Email }
        - { field: event_id, label: Evento }
        - { field: status, label: Estado, chip: true }
        - { field: checkin_at, label: Check-in }
      # ACCIÓN MASIVA (Bulk Action)
      bulk_actions:
        - key: bulk_checkin
          type: service
          label: "Validar Check-in Masivo"
          icon: mdi-qrcode-scan
          method: bulk_checkin
      # ACCIONES DE FILA (Row Actions)
      row_actions:
        - { key: confirm, type: service, label: "Confirmar", method: confirm, icon: mdi-check-circle, hidden: "item.status !== 'pending'" }
        - { key: waitlist, type: service, label: "A Espera", method: move_waitlist, icon: mdi-clock-outline, hidden: "item.status === 'waitlist'" }
        - { key: checkin, type: service, label: "Hacer Check-in", method: checkin, icon: mdi-account-check, hidden: "item.checkin_at || item.status === 'cancelled'" }
      actions:
        - { name: new, type: create, icon: mdi-plus }
        - { name: edit, type: update, icon: mdi-pencil }

- model: ui.view
  ext_id: ce_view_registration_form
  fields:
    name: "Inscripciones - Form"
    model_key: community_events.registration
    type_id.ext_id: ui.ui_view_type_form
    definition:
      groups:
        - label: Inscripción
          fields: [event_id, session_id, attendee_name, attendee_email, attendee_user_id]
        - label: Estado y Control
          fields: [status, checkin_at, notes]
```
