import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from modules.asset_lending.services.lending import LoanService
from modules.asset_lending.models.lending import Asset, Loan

@pytest.fixture
def mock_service():
    service = LoanService(MagicMock())
    service.repo = MagicMock()
    service.repo.session = MagicMock()
    return service

# Test para crear un préstamo exitosamente (asset disponible)
def test_create_loan_success(mock_service):
    asset_stub = MagicMock(spec=Asset)
    asset_stub.status = "available"
    mock_service.repo.session.get.return_value = asset_stub
    
    # Datos de entrada
    data = {"asset_id": 1, "borrower_user_id": "uuid-test", "due_at": "2030-01-01"}
    
    with patch("app.core.base.BaseService.create", return_value={"id": 100, "status": "open"}):
        result = mock_service.create(data)
        
        assert asset_stub.status == "loaned"
        assert result["status"] == "open"

# Test para crear un préstamo con asset no encontrado (debe lanzar error)
def test_create_loan_asset_not_found(mock_service):
    
    mock_service.repo.session.get.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        mock_service.create({"asset_id": 999})
    assert exc.value.status_code == 404

# --- TESTS DE DEVOLUCIÓN (RETURN) ---
# Test para devolver un préstamo exitosamente (asset en estado loaned)
def test_return_asset_success(mock_service):
    loan_stub = MagicMock(spec=Loan)
    loan_stub.status = "open"
    asset_stub = MagicMock(spec=Asset)
    asset_stub.status = "loaned"
    
    mock_service.repo.session.get.side_effect = lambda model, id: \
        loan_stub if "Loan" in str(model) else asset_stub
    
    with patch("modules.asset_lending.services.lending.serialize", return_value={"status": "returned"}):
        result = mock_service.return_asset(1)
        assert asset_stub.status == "available"
        assert loan_stub.status == "returned"

# Test para devolver un préstamo que ya fue devuelto (debe lanzar error)
def test_return_already_returned_loan(mock_service):
    loan_stub = MagicMock(spec=Loan)
    loan_stub.status = "returned"
    mock_service.repo.session.get.return_value = loan_stub
    
    with pytest.raises(HTTPException) as exc:
        mock_service.return_asset(1)
    assert exc.value.status_code == 400

