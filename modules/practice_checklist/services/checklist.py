from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.context import get_current_user_id
from app.core.serializer import serialize
from app.core.services import exposed_action

from ..models import PracticeChecklist, PracticeChecklistItem, PracticeChecklistSettings

class PracticeChecklistService(BaseService):
    def create(self, obj):
        """
        Crea un checklist asignando el owner actual y estado 'open'.
        Genera un ítem inicial automático.
        """
        if not isinstance(obj, dict):
            return super().create(obj)
        
        payload = dict(obj)
        if not payload.get("owner_id"):
            payload["owner_id"] = get_current_user_id()
        if not payload.get("status"):
            payload["status"] = "open"

        new_checklist = PracticeChecklist(**payload)
        self.repo.session.add(new_checklist)
        # flush para asegurar que new_checklist.id esté disponible
        self.repo.session.flush()

        initial_item = PracticeChecklistItem(
            checklist_id=new_checklist.id,
            title="Item inicial del checklist",
            is_done=False
        )
        self.repo.session.add(initial_item)
        
        self.repo.session.commit()
        self.repo.session.refresh(new_checklist)
        return serialize(new_checklist)
    
    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def close(self, id: int, close_note: str | None = None, force_close: bool = False, make_public: bool = False) -> dict:
        """
        Cierra el checklist.
        - Si make_public=True, marca is_public.
        - Si close_note se proporciona, la concatena con el formato esperado por los tests.
        - Si hay ítems pendientes y force_close=False, lanza 400.
        """
        rec = self.repo.session.get(PracticeChecklist, int(id))
        if rec is None:
            raise HTTPException(404, "No encontrado")

        # Verificar pendientes
        pending = [i for i in getattr(rec, "items", []) if not i.is_done]
        if pending and not force_close:
            raise HTTPException(400, f"No se puede cerrar: hay {len(pending)} ítems pendientes.")

        # Aplicar visibilidad pública si se solicita
        if make_public:
            rec.is_public = True

        # Concatenar nota de cierre con el formato exacto esperado
        if close_note:
            prefix = f"Nota de cierre: {close_note}"
            if rec.description:
                # Mantener la descripción original antes de la nota de cierre
                rec.description = f"{rec.description}\n\n{prefix}"
            else:
                rec.description = prefix

        rec.status = "closed"
        rec.closed_at = dt.datetime.now(dt.timezone.utc)
        self.repo.session.commit()
        return serialize(rec)

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def reopen(self, id: int) -> dict:
        rec = self.repo.session.get(PracticeChecklist, int(id))
        if rec is None:
            raise HTTPException(404, "No encontrado")
        rec.status = "open"
        rec.closed_at = None
        self.repo.session.commit()
        return serialize(rec)
    
class PracticeChecklistItemService(BaseService):
    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def set_done(self, id: int, done: bool = True, note: str | None = None) -> dict:
        """
        Marca un ítem como hecho/pendiente.
        - Añade nota con prefijo "[Estado] ..." si se proporciona.
        - Mantiene notas previas después del prefijo.
        """
        item = self.repo.session.get(PracticeChecklistItem, int(id))
        if item is None:
            raise HTTPException(404, "No encontrado")

        item.is_done = bool(done)
        item.done_at = dt.datetime.now(dt.timezone.utc) if done else None

        if note:
            prefix = f"[Estado] {note}"
            if item.note:
                # Prefijo primero, luego nota previa (como esperan los tests)
                item.note = f"{prefix}\n\n{item.note}"
            else:
                item.note = prefix

        self.repo.session.commit()
        return serialize(item)

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def set_done_bulk(self, ids: list[int], done: bool = True):
        """
        Procesa un bulk llamando a set_done por cada id.
        Devuelve conteo de procesados y lista de fallos.
        """
        items = (
            self.repo.session.query(PracticeChecklistItem)
            .filter(PracticeChecklistItem.id.in_(ids)).all()
        )

        processed = 0
        failed = []

        for item in items:
            try:
                item.is_done = bool(done)
                item.done_at = dt.datetime.now(dt.timezone.utc) if done else None
                processed += 1
            except Exception:
                failed.append(item.id)

        self.repo.session.commit()
        return {"status": "success", "processed": processed, "failed": failed}

class PracticeChecklistSettingsService(BaseService):
    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def toggle_setting(self, id: int) -> dict:
        """
        Alterna valores booleanos almacenados como string.
        """
        setting = self.repo.session.get(PracticeChecklistSettings, id)
        if not setting:
            raise HTTPException(404, "Ajuste no encontrado")
        
        setting.value = "false" if setting.value == "true" else "true"
        self.repo.session.commit()
        return serialize(setting)
