from sqlalchemy import Boolean, String
from app.core.base import Base
from app.core.fields import field

class PracticeChecklistSettings(Base):
    __tablename__ = "practice_checklist_settings"
    __abstract__ = False
    __model__ = "checklist_settings"
    __service__ = "app.core.base.BaseService" 

    auto_close = field(
        Boolean,
        default=True,
        info={"label": "¿Cierre automático?"}
    )
