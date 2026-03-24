from .services.checklist import PracticeChecklistService
# Importamos el override
from .services.checklist_item_override import PracticeChecklistItemAutoCloseService

# Registramos el override como el servicio oficial para los ítems
services = {
    "practice_checklist.checklist": PracticeChecklistService,
    "practice_checklist.checklist_item": PracticeChecklistItemAutoCloseService,
}