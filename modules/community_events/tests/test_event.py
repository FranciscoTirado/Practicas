import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from modules.community_events.services.event import EventService
from modules.community_events.services.registration import RegistrationService
from modules.community_events.models.event import Event
from modules.community_events.models.registration import Registration

# Fixtures para servicios con repositorios mockeados
@pytest.fixture
def mock_event_service():
    instance = EventService(MagicMock())
    instance.repo = MagicMock()
    instance.repo.session = MagicMock()
    return instance

# Fixture para RegistrationService con repositorio mockeado
@pytest.fixture
def mock_registration_service():
    instance = RegistrationService(MagicMock())
    instance.repo = MagicMock()
    instance.repo.session = MagicMock()
    return instance

# Tests para EventService
@patch("modules.community_events.services.event.serialize")
def test_publish_event_changes_status_and_visibility(mock_serialize, mock_event_service):
    event_stub = MagicMock(spec=Event)
    event_stub.id = 1
    event_stub.status = "draft"
    event_stub.is_public = False
    
    mock_event_service.repo.session.get.return_value = event_stub

    mock_serialize.side_effect = lambda obj: {
        "status": obj.status,
        "is_public": obj.is_public
    }

    response = mock_event_service.publish_event(id=1)

    assert response["status"] == "published"
    assert response["is_public"] is True

# Tests para RegistrationService
@patch("modules.community_events.services.event.serialize")
def test_cancel_event_hides_it_from_public(mock_serialize, mock_event_service):
    event_stub = MagicMock(spec=Event)
    event_stub.id = 2
    event_stub.status = "published"
    event_stub.is_public = True
    
    mock_event_service.repo.session.get.return_value = event_stub

    mock_serialize.side_effect = lambda obj: {
        "status": obj.status,
        "is_public": obj.is_public
    }

    response = mock_event_service.cancel_event(id=2, reason="Lluvia extrema")

    assert response["status"] == "cancelled"
    assert response["is_public"] is False

# Tests para RegistrationService
@patch("modules.community_events.services.registration.serialize")
def test_checkin_success_for_confirmed_user(mock_serialize, mock_registration_service):
    reg_stub = MagicMock(spec=Registration)
    reg_stub.id = 10
    reg_stub.status = "confirmed"
    reg_stub.checkin_at = None
    
    mock_registration_service.repo.session.get.return_value = reg_stub
    mock_serialize.side_effect = lambda obj: {"checkin_at": obj.checkin_at}

    response = mock_registration_service.checkin(id=10)

    assert response["checkin_at"] is not None

# Verificar que no se permite hacer check-in a un usuario cancelado
def test_checkin_fails_for_cancelled_user(mock_registration_service):
    reg_stub = MagicMock(spec=Registration)
    reg_stub.id = 11
    reg_stub.status = "cancelled"
    
    mock_registration_service.repo.session.get.return_value = reg_stub

    with pytest.raises(HTTPException):
        mock_registration_service.checkin(id=11)

# Verificar que el método bulk_checkin actualiza correctamente múltiples registros
def test_confirm_registration(mock_registration_service):
    reg = MagicMock(spec=Registration)
    reg.id = 1
    reg.status = "pending"
    
    mock_registration_service.repo.session.get.return_value = reg

    with patch("modules.community_events.services.registration.serialize", 
               return_value={"status": "confirmed"}):
        result = mock_registration_service.confirm(1)
        assert result["status"] == "confirmed"
        assert reg.status == "confirmed"

# Verificar que el método move_waitlist actualiza el estado a waitlist
def test_move_to_waitlist(mock_registration_service):
    reg = MagicMock(spec=Registration)
    reg.id = 1
    reg.status = "pending"
    
    mock_registration_service.repo.session.get.return_value = reg

    with patch("modules.community_events.services.registration.serialize", 
               return_value={"status": "waitlist"}):
        result = mock_registration_service.move_waitlist(1)
        assert result["status"] == "waitlist"
        assert reg.status == "waitlist"

# Verificar que el método bulk_checkin actualiza correctamente múltiples registros
def test_bulk_checkin(mock_registration_service):
    reg1 = MagicMock(spec=Registration)
    reg1.id = 1
    reg1.status = "confirmed"
    reg1.checkin_at = None
    
    reg2 = MagicMock(spec=Registration)
    reg2.id = 2
    reg2.status = "confirmed"
    reg2.checkin_at = None
    
    # Simular que el método get devuelve reg1 para id=1 y reg2 para id=2
    def get_mock(model, id):
        return reg1 if id == 1 else reg2

    mock_registration_service.repo.session.get.side_effect = get_mock

    result = mock_registration_service.bulk_checkin([1, 2])

    assert "2" in result["message"]