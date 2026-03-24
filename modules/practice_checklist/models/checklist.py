from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import Base
from app.core.fields import field

class PracticeChecklist(Base):
    """
    Modelo principal que representa la cabecera de un Checklist.
    Almacena el estado global, el responsable y si es visible para todos.
    """
    __tablename__ = "practice_checklist"
    __abstract__ = False
    __model__ = "checklist"
    __service__ = "modules.practice_checklist.services.checklist.PracticeChecklistService"

    # Configuración del selector para búsquedas y FKs en la UI
    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "status", "description"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "name", "label": "Checklist"},
            {"field": "status", "label": "Estado"},
            {"field": "is_public", "label": "Público"},
        ],
    }

    name = field(String(180), required=True, public=True, editable=True, info={"label": "Nombre"})
    
    description = field(Text, required=False, public=True, editable=True, info={"label": {"es": "Descripción", "en": "Description"}})
    
    status = field(
        String(20),
        required=True,
        public=True,
        editable=True,
        default="draft",
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Draft", "value": "draft"},
                {"label": "Open", "value": "open"},
                {"label": "Closed", "value": "closed"},
            ],
        },
    )

    is_public = field(Boolean, required=True, public=True, editable=True, default=False, info={"label": {"es": "Público", "en": "Public"}})
    
    owner_id = field(
        UUID, 
        ForeignKey("core_user.id"), 
        required=False, 
        public=True, 
        editable=True, 
        info={"label": {"es": "Responsable", "en": "Owner"}})
    
    owner = relationship(
        "User", 
        foreign_keys=lambda: [PracticeChecklist.owner_id], 
        info={"public": True, "recursive": False, "editable": True})
    
    closed_at = field(
        DateTime(timezone=True), 
        required=False, 
        public=True, 
        editable=False, 
        info={"label": {"es": "Cerrado en", "en": "Closed at"}})

class PracticeChecklistItem(Base):
    """
    Representa cada una de las tareas dentro de un Checklist.
    Utiliza un Override en el servicio para gestionar el auto-cierre del padre.
    """
    __tablename__ = "practice_checklist_item"
    __abstract__ = False
    __model__ = "checklist_item"
    # Apunta al servicio de Override para activar la lógica de auto-cierre
    __service__ = "modules.practice_checklist.services.checklist_item_override.PracticeChecklistItemAutoCloseService"

    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "note"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "checklist", "label": "Checklist"},
            {"field": "title", "label": "Ítem"},
            {"field": "is_done", "label": "Hecho"},
        ],
    }

    checklist_id = field(
        Integer, 
        ForeignKey("practice_checklist.id", ondelete="CASCADE"),
        required=True, public=True, editable=True)
    
    checklist = relationship(
        "PracticeChecklist", 
        foreign_keys=lambda: [PracticeChecklistItem.checklist_id],
        backref=backref("items", cascade="all, delete-orphan"),
        info={"public": True, "recursive": False, "editable": True})

    title = field(
        String(180), 
        required=True, 
        public=True, 
        editable=True, 
        info={"label": {"es": "Ítem", "en": "Item"}})
    
    note = field(
        Text, 
        required=False, 
        public=True, 
        editable=True, 
        info={"label": {"es": "Nota", "en": "Note"}})
    
    assigned_user_id = field(
        UUID, 
        ForeignKey("core_user.id"), 
        required=False, 
        public=True, 
        editable=True, 
        info={"label": {"es": "Asignado a", "en": "Assigned to"}})
    
    assigned_user = relationship(
        "User", 
        foreign_keys=lambda: [PracticeChecklistItem.assigned_user_id], 
        info={"public": True, "recursive": False, "editable": True})
    
    is_done = field(
        Boolean, 
        required=True, 
        public=True, 
        editable=True, 
        default=False, 
        info={"label": {"es": "Hecho", "en": "Done"}})
    
    done_at = field(
        DateTime(timezone=True), 
        required=False, 
        public=True, 
        editable=False, 
        info={"label": {"es": "Hecho en", "en": "Done at"}})

class PracticeChecklistSettings(Base):
    """
    Almacena parámetros de configuración globales del módulo (como el flag de auto-cierre).
    """
    __tablename__ = "practice_checklist_settings"
    __abstract__ = False
    __model__ = "settings"
    __service__ = "modules.practice_checklist.services.checklist.PracticeChecklistSettingsService"

    key = field(
        String(100),
        required=True, 
        public=True, 
        editable=False, 
        info={"label": {"es": "Clave", "en": "Key"}})
    
    value = field(
        Text, 
        required=False, 
        public=True, 
        editable=True, 
        info={"label": {"es": "Valor", "en": "Value"}})
    
    description = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Descripción", "en": "Description"}})
