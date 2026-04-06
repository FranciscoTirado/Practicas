from __future__ import annotations
import datetime as dt
from app.core.services import exposed_action # type: ignore
from ..models import PracticeChecklist, PracticeChecklistItem, PracticeChecklistSettings
from .checklist import PracticeChecklistItemService

class PracticeChecklistItemAutoCloseService(PracticeChecklistItemService):
    
    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def set_done(self, id: int, done: bool = True, note: str | None = None) -> dict:
        """
        Marca un ítem y, si se completa, dispara la validación de cierre automático.
        """
        result = super().set_done(id=id, done=done, note=note)
        
        if done:
            self._run_auto_close_logic_for_item(id)

        self.repo.session.commit()
            
        return result

    @exposed_action("write", groups=["practice_checklist_group_manager", "core_group_superadmin"])
    def set_done_bulk(self, ids: list[int], done: bool = True):
        """
        Sobrescribimos el bulk para que también dispare el auto-cierre 
        en todos los checklists afectados por los ids procesados.
        """
        items = (
            self.repo.session.query(PracticeChecklistItem)
            .filter(PracticeChecklistItem.id.in_(ids))
            .all()
        )

        for item in items:
            super().set_done(item.id, done=done)

        if done and ids:
            checklist_ids = {item.checklist_id for item in items if item.checklist_id}

            for cid in checklist_ids:
                self._run_auto_close_logic_for_checklist(cid)

        self.repo.session.commit()

        return {"status": "success"}

    def _run_auto_close_logic_for_item(self, item_id: int):
        """
        Ejecuta la verificación de auto-cierre partiendo de un item.
        """
        item = self.repo.session.get(PracticeChecklistItem, int(item_id))
        if not item or not item.checklist_id:
            return
        self._run_auto_close_logic_for_checklist(item.checklist_id)

    def _run_auto_close_logic_for_checklist(self, checklist_id: int):
        """
        Cierra automáticamente el checklist si:
        - El setting auto_close está activo
        - No quedan items pendientes
        """
        # 1. Mirar configuración
        config = (
            self.repo.session.query(PracticeChecklistSettings)
            .filter_by(key="practice_checklist.auto_close")
            .first()
        )

        auto_close_enabled = bool(config and config.value)

        if not auto_close_enabled:
            return  # Si la opción está desactivada, no hacemos nada
        
        # 2. Contar items pendientes
        pending_count = (
            self.repo.session.query(PracticeChecklistItem)
            .filter_by(checklist_id=checklist_id, is_done=False)
            .count()
        )

        # 3. Si no quedan pendientes → cerrar checklist
        if pending_count == 0:
            checklist = self.repo.session.get(PracticeChecklist, checklist_id)
            if checklist and checklist.status == "open":
                checklist.status = "closed"
                checklist.closed_at = dt.datetime.now(dt.timezone.utc)
