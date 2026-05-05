from __future__ import annotations

from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import Base  # type: ignore
from app.core.fields import field  # type: ignore

suggestion_tag_rel = Table(
    "feedback_moderation_suggestion_tag_rel",
    Base.metadata,
    Column("suggestion_id", Integer, ForeignKey("feedback_moderation_suggestion.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("feedback_moderation_tag.id"), primary_key=True),
    extend_existing=True,
)

class Suggestion(Base):
    __tablename__ = "feedback_moderation_suggestion"
    __abstract__ = False
    __model__ = "suggestion"
    __service__ = "modules.feedback_moderation.services.feedback.SuggestionService"

    title = field(String(255), required=True, public=True, editable=True)
    content = field(Text, required=True, public=True, editable=True)

    status = field(
        String(20),
        default="pending",
        required=True,
        public=True,
        editable=False,
        info={
            "label": {"es": "Estado"},
            "choices": [
                {"label": "Pendiente", "value": "pending"},
                {"label": "Publicado", "value": "published"},
                {"label": "Rechazado", "value": "rejected"},
                {"label": "Fusionado", "value": "merged"},
            ],
        },
    )

    author_email = field(String(255), required=False, public=True, editable=True)
    author_name = field(String(255), required=False, public=True, editable=True)

    is_public = field(Boolean, default=True, public=True, editable=True)
    moderation_note = field(Text, required=False, public=False, editable=False)

    votes_count = field(Integer, default=0, public=True, editable=False, info={"label": {"es": "Votos"}})

    published_at = field(DateTime(timezone=True), required=False, public=True, editable=False)
    
    reviewed_by_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=False,
        public=False,
        editable=False,
    )

    reviewed_by = relationship(
        "User", 
        foreign_keys=[reviewed_by_id],
        info={"public": False, "recursive": False}
    )

    tags = relationship(
        "modules.feedback_moderation.models.feedback.Tag",
        secondary=suggestion_tag_rel,
        back_populates="suggestions",
        info={"public": True, "editable": True},
    )

class Comment(Base):
    __tablename__ = "feedback_moderation_comment"
    __abstract__ = False
    __model__ = "comment"
    __service__ = "modules.feedback_moderation.services.feedback.CommentService"

    suggestion_id = field(
        Integer,
        ForeignKey("feedback_moderation_suggestion.id"),
        required=True,
        public=True,
        editable=True,
    )

    suggestion = relationship(
        "modules.feedback_moderation.models.feedback.Suggestion",
        info={"public": True, "recursive": False},
    )

    content = field(Text, required=True, public=True, editable=True)

    status = field(
        String(20),
        default="pending",
        required=True,
        public=True,
        editable=False,
        info={
            "choices": [
                {"label": "Pendiente", "value": "pending"},
                {"label": "Publicado", "value": "published"},
                {"label": "Rechazado", "value": "rejected"},
            ],
        },
    )

    author_email = field(String(255), required=False, public=True, editable=True)
    is_public = field(Boolean, default=True, public=True, editable=True)
    moderation_note = field(Text, required=False, public=False, editable=False)
    published_at = field(DateTime(timezone=True), required=False, public=True, editable=False)


class Tag(Base):
    __tablename__ = "feedback_moderation_tag"
    __abstract__ = False
    __model__ = "tag"
    __service__ = "modules.feedback_moderation.services.feedback.TagService"

    name = field(String(100), required=True, public=True, editable=True)
    slug = field(String(100), required=True, public=True, editable=True, unique=True)
    color = field(String(20), required=False, public=True, editable=True)

    suggestions = relationship(
        "modules.feedback_moderation.models.feedback.Suggestion",
        secondary=suggestion_tag_rel,
        back_populates="tags",
    )