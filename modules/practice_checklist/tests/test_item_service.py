from __future__ import annotations
import datetime as dt
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from .conftest import FakeChecklistItem

"""Pruebas para marcar ítems como completados."""
class TestSetDone:

    """Verifica que el servicio devuelva un diccionario serializado tras la operación."""
    def test_set_done_marks_item_done(self, item_service, mock_session):
        item = FakeChecklistItem(is_done=False)
        mock_session.get.return_value = item

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={"id": 1}):
            item_service.set_done(id=1, done=True)

        assert item.is_done is True
        assert item.done_at is not None
        assert item.done_at.tzinfo == dt.timezone.utc
        mock_session.commit.assert_called_once()

    """Verifica que el campo booleano 'is_done' cambie correctamente."""
    def test_set_done_marks_item_pending(self, item_service, mock_session):
        item = FakeChecklistItem(is_done=True, done_at=dt.datetime.now(dt.timezone.utc))
        mock_session.get.return_value = item

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            item_service.set_done(id=1, done=False)

        assert item.is_done is False
        assert item.done_at is None

    """Asegura que se registre la marca de tiempo cuando se completa un ítem."""
    def test_set_done_default_is_true(self, item_service, mock_session):
        item = FakeChecklistItem(is_done=False)
        mock_session.get.return_value = item

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            item_service.set_done(id=1)

        assert item.is_done is True

    """Verifica que si se desmarca un ítem (done=False), se elimine la fecha de realización."""
    def test_set_done_appends_note(self, item_service, mock_session):
        item = FakeChecklistItem(note="Nota previa")
        mock_session.get.return_value = item

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            item_service.set_done(id=1, note="Completado por revisión")

        assert "[Estado] Completado por revisión" in item.note
        assert "Nota previa" in item.note

    """Verifica que se añada una nota de estado al historial del ítem."""
    def test_set_done_note_on_empty(self, item_service, mock_session):
        item = FakeChecklistItem(note=None)
        mock_session.get.return_value = item

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            item_service.set_done(id=1, note="Primera nota")

        assert item.note == "[Estado] Primera nota"

    """Verifica el formato de la nota cuando el ítem no tenía notas previas."""
    def test_set_done_without_note_keeps_note(self, item_service, mock_session):
        item = FakeChecklistItem(note="Intacta")
        mock_session.get.return_value = item

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            item_service.set_done(id=1)

        assert item.note == "Intacta"

    """Verifica error 404."""
    def test_set_done_not_found_raises_404(self, item_service, mock_session):
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            item_service.set_done(id=999)
        assert exc_info.value.status_code == 404
