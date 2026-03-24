from __future__ import annotations
import datetime as dt
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from .conftest import FakeChecklist

"""Pruebas para la acción de cerrar una lista de control."""
class TestClose:
    
    """Verifica que al cerrar la lista, el estado cambie a 'closed'."""
    def test_close_sets_status_closed(self, checklist_service, mock_session):
        rec = FakeChecklist(status="open")
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={"id": 1}):
            result = checklist_service.close(id=1)

        assert rec.status == "closed"
        assert rec.closed_at is not None
        mock_session.commit.assert_called_once()

    """Verifica que si se pasa make_public=True, la lista se marque como pública."""
    def test_close_sets_is_public_when_requested(self, checklist_service, mock_session):
        rec = FakeChecklist(status="open", is_public=False)
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            checklist_service.close(id=1, make_public=True)

        assert rec.is_public is True

    """Verifica que la nota de cierre se concatene correctamente a la descripción existente."""
    def test_close_appends_note_to_description(self, checklist_service, mock_session):
        rec = FakeChecklist(description="Desc original")
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            checklist_service.close(id=1, close_note="Motivo de cierre")

        assert "Nota de cierre: Motivo de cierre" in rec.description
        assert "Desc original" in rec.description

    """Verifica el formato de la nota de cierre cuando la descripción original está vacía."""
    def test_close_note_on_empty_description(self, checklist_service, mock_session):
        rec = FakeChecklist(description=None)
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            checklist_service.close(id=1, close_note="Nota")

        assert rec.description == "Nota de cierre: Nota"

    """Asegura que si no se envía nota, la descripción no se altere ni se vuelva None."""
    def test_close_without_note_keeps_description(self, checklist_service, mock_session):
        rec = FakeChecklist(description="Intacta")
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            checklist_service.close(id=1)

        assert rec.description == "Intacta"

    """Verifica que se registre la fecha y hora exacta (UTC) del cierre."""
    def test_close_sets_closed_at_utc(self, checklist_service, mock_session):
        rec = FakeChecklist()
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            checklist_service.close(id=1)

        assert rec.closed_at.tzinfo == dt.timezone.utc

    def test_close_not_found_raises_404(self, checklist_service, mock_session):
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            checklist_service.close(id=999)
        assert exc_info.value.status_code == 404

"""Pruebas para la acción de reabrir una lista cerrada."""
class TestReopen:

    """Verifica que al reabrir, el estado vuelva a 'open' y se limpie la fecha de cierre."""
    def test_reopen_sets_status_open(self, checklist_service, mock_session):
        rec = FakeChecklist(status="closed", closed_at=dt.datetime.now(dt.timezone.utc))
        mock_session.get.return_value = rec

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={"id": 1, "status": "open"}):
            result = checklist_service.reopen(id=1)

        assert rec.status == "open"
        assert rec.closed_at is None
        mock_session.commit.assert_called_once()

    """Verifica error 404."""
    def test_reopen_not_found_raises_404(self, checklist_service, mock_session):
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            checklist_service.reopen(id=999)
        assert exc_info.value.status_code == 404
