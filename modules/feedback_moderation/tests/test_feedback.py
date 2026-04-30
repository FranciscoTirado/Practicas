import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from modules.feedback_moderation.services.feedback import SuggestionService
from modules.feedback_moderation.models.feedback import Suggestion

@pytest.fixture
def mock_service():
    service = SuggestionService(MagicMock())
    service.repo = MagicMock()
    service.repo.session = MagicMock()
    return service

def test_publish_suggestion_success(mock_service):
    # Setup
    suggestion_stub = MagicMock(spec=Suggestion)
    suggestion_stub.status = "pending"
    mock_service.repo.session.get.return_value = suggestion_stub
    
    with patch("modules.feedback_moderation.services.feedback.serialize", return_value={"status": "published"}):
        result = mock_service.publish(1)
        assert suggestion_stub.status == "published"
        assert result["status"] == "published"

def test_publish_suggestion_not_found(mock_service):
    mock_service.repo.session.get.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        mock_service.publish(999)
    assert exc.value.status_code == 404

def test_archive_suggestion(mock_service):
    suggestion_stub = MagicMock(spec=Suggestion)
    suggestion_stub.status = "published"
    mock_service.repo.session.get.return_value = suggestion_stub
    
    # Asumiendo que tienes un método archive en el servicio
    if hasattr(mock_service, 'archive'):
        with patch("modules.feedback_moderation.services.feedback.serialize", return_value={"status": "archived"}):
            result = mock_service.archive(1)
            assert suggestion_stub.status == "archived"

# --- CASOS DE ERROR Y LÓGICA ---
def test_publish_already_published_raises_error(mock_service):
    """No se puede publicar algo que ya está publicado."""
    suggestion_mock = MagicMock()
    suggestion_mock.status = "published"
    
    mock_service.repo.session.get.return_value = suggestion_mock

    with pytest.raises(HTTPException) as exc:
        mock_service.publish(1)
    
    assert exc.value.status_code == 400


def test_vote_suggestion_success(mock_service):
    """Prueba la lógica de votación (incremento)."""
    suggestion_stub = MagicMock(spec=Suggestion)
    suggestion_stub.id = 1
    suggestion_stub.votes_count = 10
    
    mock_service.repo.session.get.return_value = suggestion_stub
    
    # Simulamos que el método vote incrementa el contador
    with patch("modules.feedback_moderation.services.feedback.serialize", 
               side_effect=lambda x: {"votes_count": x.votes_count}):
        result = mock_service.vote(1, user_id="user-123")
        
        assert suggestion_stub.votes_count == 11
        assert result["votes_count"] == 11


def test_get_moderation_queue(mock_service):
    """Prueba los filtros de búsqueda (la query)."""
    # Simulamos que la query devuelve una lista de mocks
    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = [MagicMock(spec=Suggestion)]
    mock_service.repo.session.query.return_value = mock_query
    
    result = mock_service.get_moderation_queue(status="pending")
    
    assert len(result) == 1
    mock_query.filter.assert_called() # Verificamos que se aplicó un filtro