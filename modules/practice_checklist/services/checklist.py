from __future__ import annotations
import datetime as dt

from sqlalchemy import select, func
from sqlalchemy import false as sql_false

from app.core.base import BaseService
from app.core.context import get_current_user_id
from app.core.serializer import serialize
from app.core.services import exposed_action

from ..models import PracticeChecklist, PracticeChecklistItem

class PracticeChecklistService(BaseService):
    from ..models import PracticeChecklist

    def create(self, obj):
        """
        Crea un checklist y, si todo va bien, crea un ítem inicial asociado.
        Si el payload incluye 'initial_item_title' se usará como título del ítem,
        si no, se usará "Item automatico".
        """
        if not isinstance(obj, dict):
            return super().create(obj)
        payload = dict(obj)
        if not payload.get("owner_id"):
            payload["owner_id"] = get_current_user_id()
        if not payload.get("status"):
            payload["status"] = "open"

        # Crea checklist usando la implementación base
        created = super().create(payload)

        # Determina id del checklist (super().create puede devolver dict o modelo)
        checklist_id = created["id"] if isinstance(created, dict) else getattr(created, "id", None)

        # Crear un ítem inicial asociado al checklist
        try:
            initial_title = payload.get("initial_item_title", "Item automatico")
            if checklist_id is not None:
                item = PracticeChecklistItem(
                    checklist_id=int(checklist_id),
                    title=initial_title,
                )
                self.repo.session.add(item)
                # Commit para persistir el ítem (y asegurar integridad)
                self.repo.session.commit()
        except Exception:
            self.repo.session.rollback()
            raise

        return created

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def close(self, id: int | list[int], close_note: str | None = None, make_public: bool = False) -> list[dict]:
        ids = [id] if isinstance(id, int) else id
        results = []
        for res_id in ids:
            rec = self.repo.session.get(PracticeChecklist, int(res_id))
            if rec:
                rec.status = "closed"
                rec.is_public = bool(make_public)
                rec.closed_at = dt.datetime.now(dt.timezone.utc)
                if close_note:
                    base = (rec.description or "").strip()
                    rec.description = f"{base}\n\n[Cierre] {close_note}".strip()
                self.repo.session.add(rec)
                results.append(rec)
        self.repo.session.commit()
        return [serialize(r) for r in results]

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def reopen(self, id: int | list[int]) -> list[dict]:
        ids = [id] if isinstance(id, int) else id
        results = []
        for res_id in ids:
            rec = self.repo.session.get(PracticeChecklist, int(res_id))
            if rec:
                rec.status = "open"
                rec.closed_at = None
                self.repo.session.add(rec)
                results.append(rec)
        self.repo.session.commit()
        return [serialize(r) for r in results]

class PracticeChecklistItemService(BaseService):
    from ..models import PracticeChecklistItem

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def set_done(self, id: int | list[int], done: bool = True, note: str | None = None) -> list[dict]:
        """
        Marca uno o varios ítems como hechos/pendientes. Tras la actualización,
        si todos los ítems de un checklist están hechos, se cierra automáticamente el checklist.
        """
        ids = [id] if isinstance(id, int) else id
        updated_items = []
        affected_checklist_ids = set()

        try:
            for item_id in ids:
                item = self.repo.session.get(PracticeChecklistItem, int(item_id))
                if item:
                    item.is_done = bool(done)
                    item.done_at = dt.datetime.now(dt.timezone.utc) if done else None
                    if note:
                        base = (item.note or "").strip()
                        item.note = f"{base}\n\n[Bulk Update] {note}".strip()
                    self.repo.session.add(item)
                    updated_items.append(item)
                    affected_checklist_ids.add(int(item.checklist_id))
            self.repo.session.commit()

            # Para cada checklist afectado, comprobar si todos los ítems están hechos
            for checklist_id in affected_checklist_ids:
                # contar ítems pendientes
                pending_count = (
                    self.repo.session.scalar(
                        select(func.count()).where(
                            PracticeChecklistItem.checklist_id == checklist_id,
                            PracticeChecklistItem.is_done.is_(False)
                        )
                    ) or 0
                )
                checklist = self.repo.session.get(PracticeChecklist, checklist_id)
                if checklist:
                    if pending_count == 0 and checklist.status != "closed":
                        checklist.status = "closed"
                        checklist.closed_at = dt.datetime.now(dt.timezone.utc)
                        self.repo.session.add(checklist)

            # Commit cambios en checklists
            self.repo.session.commit()

        except Exception:
            self.repo.session.rollback()
            raise

        return [serialize(i) for i in updated_items]
