from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import Base #type: ignore
from app.core.fields import field #type: ignore

class Location(Base):
    __tablename__ = "asset_lending_location"
    __abstract__ = False
    __model__ = "location"
    __service__ = "modules.asset_lending.services.lending.LocationService"

    name = field(String(100), required=True, public=True, editable=True)
    description = field(Text, required=False, public=True, editable=True)

    assets = relationship(
        "modules.asset_lending.models.lending.Asset",
        back_populates="location",
        info={"public": False}
    )


class Asset(Base):
    __tablename__ = "asset_lending_asset"
    __abstract__ = False
    __model__ = "asset"
    __service__ = "modules.asset_lending.services.lending.AssetService"

    name = field(String(180), required=True, public=True, editable=True)
    asset_code = field(String(50), required=True, public=True, editable=True)
    status = field(
        String(20),
        default="available",
        required=True,
        public=True,
        editable=False,
    )

    location_id = field(
        Integer,
        ForeignKey("asset_lending_location.id"),
        required=True,
        public=True,
    )

    location = relationship(
        "modules.asset_lending.models.lending.Asset",
        back_populates="assets",
        info={"public": True, "recursive": False},
    )

    responsible_user_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=False,
        public=True,
    )

    responsible_user = relationship(
        "User",
        info={"public": True, "recursive": False},
    )


class Loan(Base):
    __tablename__ = "asset_lending_loan"
    __abstract__ = False
    __model__ = "loan"
    __service__ = "modules.asset_lending.services.lending.LoanService"

    asset_id = field(
        Integer,
        ForeignKey("asset_lending_asset.id"),
        required=True,
        public=True,
    )

    asset = relationship(
        "modules.asset_lending.models.lending.Asset",
        info={"public": True, "recursive": False},
    )

    borrower_user_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=True,
        public=True,
    )

    borrower = relationship(
        "User",
        info={"public": True, "recursive": False},
    )

    checkout_at = field(DateTime(timezone=True), required=True, public=True)
    due_at = field(DateTime(timezone=True), required=True, public=True)
    returned_at = field(DateTime(timezone=True), required=False, public=True)
    
    status = field(
        String(20),
        default="open",
        required=True,
        public=True,
    )

    checkout_note = field(Text, required=False, public=True)
    return_note = field(Text, required=False, public=True)