from __future__ import annotations
import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService # type: ignore
from app.core.serializer import serialize # type: ignore
from app.core.services import exposed_action # type: ignore
from ..models.lending import Asset, Loan

class AssetService(BaseService):
    """
    Gestiona la lógica de negocio del Inventario (Assets).
    """
    __model__ = Asset

    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def mark_maintenance(self, id: int, note: str | None = None) -> dict:
        """ Cambia el estado del objeto a 'mantenimiento' y añade una nota histórica. """
        asset = self.repo.session.get(Asset, int(id))
        if not asset:
            raise HTTPException(404, "Objeto no encontrado en el inventario.")

        asset.status = "mantenimiento"
        if note:
            # Concatena la nota nueva preservando el historial
            base = (asset.description or "").strip()
            asset.description = f"{base}\n\n[Mantenimiento {dt.date.today()}] {note}".strip()

        self.repo.session.add(asset)
        self.repo.session.commit()
        self.repo.session.refresh(asset)
        return serialize(asset)

    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def release_maintenance(self, id: int) -> dict:
        """ Devuelve un objeto reparado al almacén. """
        asset = self.repo.session.get(Asset, int(id))
        if not asset or asset.status != "mantenimiento":
            raise HTTPException(400, "El objeto no está actualmente en mantenimiento.")

        asset.status = "almacenado"
        self.repo.session.add(asset)
        self.repo.session.commit()
        self.repo.session.refresh(asset)
        return serialize(asset)

class AssetLoanService(BaseService):
    """
    Gestiona el ciclo de vida de los préstamos.
    """
    __model__ = Loan

    def create(self, obj):  
        """
        Sobrescribe la creación por defecto para validar disponibilidad y fechas.
        """
        if not isinstance(obj, dict):
            return super().create(obj)
        
        payload = dict(obj)

        #  Validación de Seguridad
        asset_id = payload.get("asset_id")
        if not asset_id:
            raise HTTPException(400, "Debe seleccionar un equipo válido para el préstamo.")

        #  Gestión de Fechas
        raw_due = payload.get("due_at")
        if not raw_due:
            # Evita que el servidor colapse si el formulario envía la fecha vacía
            raise HTTPException(400, "La fecha prevista de devolución es obligatoria.")

        if isinstance(raw_due, str):
            try:
                # Intenta procesar formato español DD/MM/YYYY o estándar ISO
                if "/" in raw_due:
                    parsed = dt.datetime.strptime(raw_due, "%d/%m/%Y")
                else:
                    parsed = dt.datetime.fromisoformat(raw_due.replace('Z', '+00:00'))
                payload["due_at"] = parsed.replace(tzinfo=dt.timezone.utc)
            except Exception:
                raise HTTPException(400, f"Formato de fecha inválido: {raw_due}")

        #  Verificación de Disponibilidad en Inventario
        asset = self.repo.session.get(Asset, int(asset_id))
        if not asset:
            raise HTTPException(404, "El equipo seleccionado no existe en la base de datos.")
        
        if asset.status != "almacenado":
            raise HTTPException(
                400, f"Operación denegada: el equipo no está en almacén (Estado actual: '{asset.status}')"
            )

        #  Bloquear el equipo en el inventario
        asset.status = "prestado"
        self.repo.session.add(asset)

        #  Configurar el préstamo
        payload["status"] = "open"
        payload["checkout_at"] = dt.datetime.now(dt.timezone.utc)

        # Ejecuta la creación en la base de datos
        return super().create(payload)

    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def return_asset(self, id: int, note: str | None = None) -> dict:
        """
        Cierra el préstamo y devuelve automáticamente el objeto al inventario.
        """
        loan = self.repo.session.get(Loan, int(id))
        if not loan or loan.status != "open":
            raise HTTPException(400, "Préstamo no válido o el equipo ya ha sido devuelto.")

        # Actualiza el préstamo
        loan.status = "returned"
        loan.returned_at = dt.datetime.now(dt.timezone.utc)
        if note:
            loan.return_note = note

        # Actualiza el objeto vinculado
        asset = self.repo.session.get(Asset, loan.asset_id)
        if asset:
            asset.status = "almacenado"
            self.repo.session.add(asset)

        self.repo.session.add(loan)
        self.repo.session.commit()
        self.repo.session.refresh(loan)
        return serialize(loan)