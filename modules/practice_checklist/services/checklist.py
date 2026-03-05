from __future__ import annotations
import datetime as dt
from fastapi import HTTPException

from app.core.base import BaseService
from app.core.context import get_current_user_id
from app.core.serializer import serialize
from app.core.services import exposed_action

from ..models import PracticeChecklist, PracticeChecklistItem

class PracticeChecklistService(BaseService):
    from ..models import PracticeChecklist

    def create(self, obj):
        if not isinstance(obj, dict):
            return super().create(obj)
        payload = dict(obj)
        if not payload.get("owner_id"):
            payload["owner_id"] = get_current_user_id()
        if not payload.get("status"):
            payload["status"] = "open"
        return super().create(payload)

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
        ids = [id] if isinstance(id, int) else id
        updated_items = []
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
        self.repo.session.commit()
        return [serialize(i) for i in updated_items]
    