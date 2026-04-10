from __future__ import annotations
import datetime as dt
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base # type: ignore
from app.core.fields import field # type: ignore

class Asset(Base):
    """
    INVENTARIO: Definición técnica de los objetos físicos.
    Aquí nacen los recursos y se les asigna su ubicación de almacén físico.
    """
    __tablename__ = "asset_lending_asset"
    __abstract__ = False
    __model__ = "asset"
    __service__ = "modules.asset_lending.services.lending.AssetService"

    name = field(
        String(180),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Nombre del producto", "en": "Product Name"}},
    )
    object_code = field(
        String(50),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Código de objeto", "en": "Object Code"}},
    )
    storage_location_code = field(
        String(50),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Cód. Ubicación Almacenamiento", "en": "Storage Code"}},
    )
    description = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Descripción", "en": "Description"}},
    )
    status = field(
        String(20),
        required=True,
        public=True,
        editable=False,
        default="almacenado",
        info={
            "label": {"es": "Estado actual", "en": "Current Status"},
            "choices": [
                {"label": "Almacenado", "value": "almacenado"},
                {"label": "Prestado", "value": "prestado"},
                {"label": "En mantenimiento", "value": "mantenimiento"},
            ],
        },
    )

class Loan(Base):
    """
    TRANSACCIÓN: Registro histórico y activo de los préstamos.
    Vincula un 'Asset' con un 'User' en una ventana de tiempo.
    """
    __tablename__ = "asset_lending_loan"
    __abstract__ = False
    __model__ = "loan"
    __service__ = "modules.asset_lending.services.lending.AssetLoanService"

    asset_id = field(
        Integer,
        ForeignKey("asset_lending_asset.id"),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Equipo prestado", "en": "Borrowed Equipment"}},
    )
    asset = relationship(
        "modules.asset_lending.models.lending.Asset",
        foreign_keys=lambda: [Loan.asset_id],
        info={"public": True, "recursive": False}
    )
    borrower_user_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Solicitante", "en": "Borrower"}},
    )
    checkout_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        default=lambda: dt.datetime.now(dt.timezone.utc), # Auto-fecha al crear
    )
    due_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        editable=True, # El gestor o usuario debe indicar cuándo lo devuelve
    )
    returned_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False, # Solo se rellena al pulsar el botón de devolver
    )
    status = field(
        String(20),
        required=True,
        public=True,
        editable=False,
        default="open",
        info={
            "label": {"es": "Estado del préstamo", "en": "Status"},
            "choices": [
                {"label": "Activo", "value": "open"},
                {"label": "Devuelto", "value": "returned"},
                {"label": "Fuera de plazo", "value": "overdue"},
            ],
        },
    )
    checkout_note = field(Text, public=True)
    return_note = field(Text, public=True)