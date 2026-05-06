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
    # Método para convertir fechas en formato dd/mm/yyyy a objetos datetime
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
    # Sobrescribir los métodos de creación y actualización para sanitizar las fechas
    def create(self, obj): 
        if not isinstance(obj, dict):
            return super().create(obj)
        data_copy = self.sanitize_dates(dict(obj))
        return super().create(data_copy)
    # Sobrescribir el método de actualización para sanitizar las fechas
    def update(self, id: int, obj):  
        if not isinstance(obj, dict):
            return super().update(id, obj)
        data_copy = self.sanitize_dates(dict(obj))
        return super().update(id, data_copy)

    # Acciones para gestión de eventos
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
    # Acción para cerrar inscripciones de un evento
    @exposed_action("write", groups=["community_events_group_staff", "core_group_superadmin"])
    def close_registration(self, id: int, reason: str | None = None) -> dict:
        record = self.repo.session.get(self.Event, int(id))
        if record is None:
            raise HTTPException(404, "El evento indicado no existe")

        record.status = "closed"
        self.repo.session.add(record)
        self.repo.session.commit()
        return serialize(record)
    # Acción para cancelar un evento
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
    # Acción para reabrir un evento cerrado o cancelado
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

