from __future__ import annotations

import datetime as dt
from fastapi import HTTPException

from app.core.base import BaseService  # type: ignore
from app.core.serializer import serialize # type: ignore
from app.core.services import exposed_action # type: ignore

from ..models.feedback import Comment, Suggestion, Tag


class SuggestionService(BaseService):
    from ..models.feedback import Suggestion
    # Acciones para gestión de sugerencias
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def publish(self, id: int, note: str | None = None, pin: bool = False):
        suggestion = self.repo.session.get(Suggestion, id)
        if not suggestion:
            raise HTTPException(404, "Suggestion not found")

        # FIX: Evitar que se publique algo ya publicado (necesario para el test)
        if suggestion.status == "published":
            raise HTTPException(400, "Already published")

        suggestion.status = "published"
        suggestion.published_at = dt.datetime.now(dt.timezone.utc)
        suggestion.moderation_note = note

        self.repo.session.commit()
        return serialize(suggestion)
    # Acción para rechazar una sugerencia
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reject(self, id: int, note: str):
        suggestion = self.repo.session.get(Suggestion, id)
        if not suggestion:
            raise HTTPException(404, "Suggestion not found")

        suggestion.status = "rejected"
        suggestion.moderation_note = note
        self.repo.session.commit()
        return serialize(suggestion)
    # Acción para fusionar una sugerencia con otra
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def merge(self, id: int, target_id: int, note: str | None = None):
        suggestion = self.repo.session.get(Suggestion, id)
        target = self.repo.session.get(Suggestion, target_id)

        if not suggestion or not target:
            raise HTTPException(404, "Suggestion not found")

        suggestion.status = "merged"
        suggestion.moderation_note = note
        self.repo.session.commit()
        return serialize(suggestion)
    # Acción para reabrir una sugerencia (volver a estado pendiente)
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reopen(self, id: int):
        suggestion = self.repo.session.get(Suggestion, id)
        if not suggestion:
            raise HTTPException(404, "Suggestion not found")

        suggestion.status = "pending"
        self.repo.session.commit()
        return serialize(suggestion)
    # Acción para votar por una sugerencia
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def vote(self, suggestion_id: int, user_id: str):
        suggestion = self.repo.session.get(Suggestion, suggestion_id)
        if not suggestion:
            raise HTTPException(status_code=404)
        suggestion.votes_count += 1
        self.repo.session.commit()
        return serialize(suggestion)

    # Acción para obtener la cola de moderación filtrada por estado
    @exposed_action("read", groups=["feedback_group_moderator", "core_group_superadmin"])
    def get_moderation_queue(self, status: str = "pending"):
        return self.repo.session.query(Suggestion).filter(Suggestion.status == status).all()


class CommentService(BaseService):
    from ..models.feedback import Comment

    # Acciones para gestión de comentarios
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def publish_comment(self, id: int, note: str | None = None):
        comment = self.repo.session.get(Comment, id)
        if not comment:
            raise HTTPException(404, "Comment not found")

        comment.status = "published"
        comment.published_at = dt.datetime.now(dt.timezone.utc)
        comment.moderation_note = note
        self.repo.session.commit()
        return serialize(comment)
    # Acción para rechazar un comentario
    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reject_comment(self, id: int, note: str):
        comment = self.repo.session.get(Comment, id)
        if not comment:
            raise HTTPException(404, "Comment not found")

        comment.status = "rejected"
        comment.moderation_note = note
        self.repo.session.commit()
        return serialize(comment)


class TagService(BaseService):
    from ..models.feedback import Tag