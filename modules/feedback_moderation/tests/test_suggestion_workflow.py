def test_suggestion_publish(session, suggestion_service):
    suggestion = suggestion_service.create({
        "title": "Nueva funcionalidad",
        "content": "Agregar modo oscuro"
    })

    result = suggestion_service.publish(suggestion["id"])
    assert result["status"] == "published"


def test_suggestion_reject(session, suggestion_service):
    suggestion = suggestion_service.create({
        "title": "Idea",
        "content": "Eliminar módulo"
    })

    result = suggestion_service.reject(
        suggestion["id"],
        note="No aplicable"
    )
    assert result["status"] == "rejected"


def test_suggestion_reopen(session, suggestion_service):
    suggestion = suggestion_service.create({
        "title": "Idea",
        "content": "Prueba"
    })

    suggestion_service.reject(suggestion["id"], note="No válida")
    result = suggestion_service.reopen(suggestion["id"])

    assert result["status"] == "pending"