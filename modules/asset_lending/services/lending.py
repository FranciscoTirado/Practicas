from __future__ import annotations

import datetime as dt

from fastapi import HTTPException

from app.core.base import BaseService #type: ignore
from app.core.serializer import serialize #type: ignore
from app.core.services import exposed_action #type: ignore

from ..models.lending import Asset, Loan

# Valida ubicación y recurso al crear o actualizar un préstamo
class LocationService(BaseService):
    from ..models.lending import Location

# Clase pricipal de servicios para recursos, con acciones expuestas para marcar mantenimiento y devolver de mantenimiento
class AssetService(BaseService):
    from ..models.lending import Asset

    # Valida que el recurso exista, no este prestado ni en mantenimiento al crear o actualizar un recurso
    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def mark_maintenance(self, id: int, note: str | None = None) -> dict:
        asset = self.repo.session.get(Asset, int(id))
        if asset is None:
            raise HTTPException(404, "Asset not found")
        
        asset.status = "maintenance"
        if note:
            base = (asset.notes or "").strip()
            asset.notes = f"{base}\n\n[Mantenimiento] {note}".strip()

        self.repo.session.add(asset)
        self.repo.session.commit()
        self.repo.session.refresh(asset)
        return serialize(asset)

    # Devuelve un recurso de mantenimiento a disponible, validando que esté en mantenimiento actualmente
    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def release_maintenance(self, id: int) -> dict:
        asset = self.repo.session.get(Asset, int(id))
        if asset is None:
            raise HTTPException(404, "Asset not found")
        if asset.status != "maintenance":
            raise HTTPException(
                400, f"Asset is not in maintenance (current status: {asset.status})"
            )

        asset.status = "available"
        self.repo.session.add(asset)
        self.repo.session.commit()
        self.repo.session.refresh(asset)
        return serialize(asset)

# Clase principal de servicios para préstamos, con validaciones al crear un préstamo y marcar un préstamo como devuelto
class AssetLoanService(BaseService):
    from ..models.lending import Loan

    # Valida que el recurso exista y esté disponible, y que la fecha de devolución sea correcta al crear un préstamo
    def create(self, obj):  
        if not isinstance(obj, dict):
            return super().create(obj)

        payload = dict(obj)

        asset_id = payload.get("asset_id")
        if not asset_id:
            raise HTTPException(400, "asset_id is required")

        raw_due = payload.get("due_at")
        if isinstance(raw_due, str) and "/" in raw_due:
            parsed = dt.datetime.strptime(raw_due, "%d/%m/%Y")
            payload["due_at"] = parsed.replace(tzinfo=dt.timezone.utc)

        asset = self.repo.session.get(Asset, int(asset_id))
        if asset is None:
            raise HTTPException(404, "Asset not found")
        if asset.status != "available":
            raise HTTPException(
                400, f"Asset not available: {asset.status}"
            )

        asset.status = "loaned"
        self.repo.session.add(asset)

        payload["status"] = "open"
        payload["checkout_at"] = dt.datetime.now(dt.timezone.utc)

        return super().create(payload)

    # Marca un préstamo como devuelto, validando que el préstamo exista y esté abierto,
    # y actualiza el estado del recurso a disponible
    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def return_asset(self, id: int, note: str | None = None) -> dict:
        loan = self.repo.session.get(Loan, int(id))
        if loan is None:
            raise HTTPException(404, "Loan not found")
        if loan.status != "open":
            raise HTTPException(
                400, f"Loan is not open (current status: {loan.status})"
            )

        loan.status = "returned"
        loan.returned_at = dt.datetime.now(dt.timezone.utc)
        if note:
            loan.return_note = note

        asset = self.repo.session.get(Asset, loan.asset_id)
        if asset is not None:
            asset.status = "available"
            self.repo.session.add(asset)

        self.repo.session.add(loan)
        self.repo.session.commit()
        self.repo.session.refresh(loan)
        return serialize(loan)
    
    # Al buscar préstamos, actualiza el estado a vencidode los que estén abiertos y hayan pasado su fecha de devolución
    def search(self, *args, **kwargs):
        loans = super().search(*args, **kwargs)
        now = dt.datetime.now(dt.timezone.utc)
        changed = False

        for loan in loans:
            if (
                loan.status == "open" and
                loan.due_at is not None and
                loan.due_at < now
            ):
                loan.status = "overdue"
                self.repo.session.add(loan)
                changed = True

        if changed:
            self.repo.session.commit()

        return loans
    