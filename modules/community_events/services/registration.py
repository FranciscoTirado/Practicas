from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService  # type: ignore
from app.core.serializer import serialize  # type: ignore
from app.core.services import exposed_action  # type: ignore


class RegistrationService(BaseService):
    from ..models.registration import Registration
    from ..models.event import Event

    def create(self, obj):
        if not isinstance(obj, dict):
            return super().create(obj)

        entry = dict(obj)

        event_id = entry.get("event_id")

        if event_id is None:
            raise HTTPException(400, "event_id es obligatorio")

        event = self.repo.session.get(self.Event, int(event_id))
        if not event:
            raise HTTPException(400, "El evento no existe")

        if event.status != "published":
            raise HTTPException(400, "El evento no está publicado")

        # ✅ timestamp automático
        entry["registered_at"] = dt.datetime.now(dt.timezone.utc)

        # ✅ estado por defecto
        entry["status"] = entry.get("status", "pending")

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