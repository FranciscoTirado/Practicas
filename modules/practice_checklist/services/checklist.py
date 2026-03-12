from __future__ import annotations
import datetime as dt

from sqlalchemy import select, func, update, desc
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.context import get_current_user_id
from app.core.serializer import serialize
from app.core.services import exposed_action

from ..models import PracticeChecklist, PracticeChecklistItem, PracticeChecklistSettings

class PracticeChecklistSettingsService(BaseService):
    @exposed_action("create")
    def create(self, obj: dict | object):
        count = self.repo.session.scalar(select(func.count(PracticeChecklistSettings.id)))
        if count > 0:
            raise HTTPException(status_code=400, detail="Ya existe una configuración global.")
        return super().create(obj)

class PracticeChecklistService(BaseService):
    def _get_settings(self):
        """Obtiene el último setting sin intentar borrar nada (evita errores 500)."""
        try:
            return self.repo.session.execute(
                select(PracticeChecklistSettings).order_by(desc(PracticeChecklistSettings.id))
            ).scalars().first()
        except Exception:
            return None

    @exposed_action("create")
    def create(self, obj: dict | object):
        payload = dict(obj) if isinstance(obj, dict) else obj.__dict__
        if not payload.get("owner_id"):
            payload["owner_id"] = get_current_user_id()
        
        settings = self._get_settings()
        if not payload.get("status"):
            payload["status"] = settings.default_status if settings and settings.default_status else "draft"

        created = super().create(payload)
        checklist_id = created["id"] if isinstance(created, dict) else getattr(created, "id", None)

        if checklist_id:
            try:
                item = PracticeChecklistItem(
                    checklist_id=int(checklist_id),
                    title=payload.get("initial_item_title") or "Item automático inicial"
                )
                self.repo.session.add(item)
                self.repo.session.commit()
            except Exception:
                self.repo.session.rollback()
        return created

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def reopen(self, id: int | list[int]) -> list[dict]:
        ids = [id] if isinstance(id, int) else id
        results = []
        for res_id in ids:
            rec = self.repo.session.get(PracticeChecklist, int(res_id))
            if rec:
                rec.status = "open"
                rec.closed_at = None
                self.repo.session.execute(
                    update(PracticeChecklistItem)
                    .where(PracticeChecklistItem.checklist_id == rec.id)
                    .values(is_done=False, done_at=None)
                )
                self.repo.session.add(rec)
                results.append(rec)
        self.repo.session.commit()
        return [serialize(r) for r in results]

class PracticeChecklistItemService(BaseService):
    def _get_settings(self):
        try:
            return self.repo.session.execute(
                select(PracticeChecklistSettings).order_by(desc(PracticeChecklistSettings.id))
            ).scalars().first()
        except Exception:
            return None

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def set_done(self, id: int | list[int], done: bool = True, note: str | None = None) -> list[dict]:
        ids = [id] if isinstance(id, int) else id
        updated_items = []
        affected_checklist_ids = set()

        for item_id in ids:
            item = self.repo.session.get(PracticeChecklistItem, int(item_id))
            if not item: continue
            
            # Validación de seguridad: no modificar si el checklist está cerrado
            # Solo lanzamos el error si intentamos cambiar algo en un checklist CERRADO
            checklist = self.repo.session.get(PracticeChecklist, item.checklist_id)
            if checklist and checklist.status == "closed":
                raise HTTPException(
                    status_code=400, 
                    detail="Checklist cerrado. Reábrelo para editar sus ítems."
                )

            item.is_done = bool(done)
            item.done_at = dt.datetime.now(dt.timezone.utc) if done else None
            if note:
                item.note = f"{(item.note or '').strip()}\n\n[Nota] {note}".strip()
            
            self.repo.session.add(item)
            updated_items.append(item)
            affected_checklist_ids.add(item.checklist_id)

        self.repo.session.commit()

        # Lógica de auto-cierre
        settings = self._get_settings()
        should_auto_close = bool(settings.auto_close) if settings is not None else True

        if should_auto_close and done: # Solo intentamos cerrar si estamos marcando como hecho
            for cl_id in affected_checklist_ids:
                pending = self.repo.session.scalar(
                    select(func.count()).where(
                        PracticeChecklistItem.checklist_id == cl_id,
                        PracticeChecklistItem.is_done == False
                    )
                )
                if pending == 0:
                    cl = self.repo.session.get(PracticeChecklist, cl_id)
                    if cl and cl.status != "closed":
                        cl.status = "closed"
                        cl.closed_at = dt.datetime.now(dt.timezone.utc)
                        self.repo.session.add(cl)
            self.repo.session.commit()

        return [serialize(i) for i in updated_items]