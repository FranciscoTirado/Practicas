# Documentación de módulos del backend

Este documento combina la documentación funcional y técnica de los tres módulos principales: `asset_lending`, `community_events` y `feedback_moderation`. Incluye objetivos, estructura, modelos, servicios y funcionalidades clave.

---

## 1. Módulo `asset_lending`

### Objetivo
Gestionar el préstamo de activos físicos, controlando su disponibilidad, mantenimiento y ciclo de vida de préstamos para asegurar un uso eficiente y seguro.

### Estructura de archivos
- `__manifest__.yaml`: Define el módulo, dependencias y recursos iniciales.
- `models/lending.py`: Modelos `Location`, `Asset`, `Loan`.
- `services/lending.py`: Servicios `LocationService`, `AssetService`, `LoanService`.
- `data/`: Grupos de seguridad y reglas ACL.
- `views/`: Configuración de UI para préstamos y activos.
- `tests/`: Pruebas unitarias.

### Modelos clave
Los archivos de modelo definen las entidades y metadata que el framework utiliza para asociar cada modelo a su servicio y generar la UI.
- `Location`: Ubicación de activos. Representa zonas físicas y se vincula a `Asset`.
- `Asset`: Recurso prestable con estado y ubicación. Consumido por `AssetService` y por `LoanService` al validar la creación y devolución de préstamos.
- `Loan`: Registro de préstamo. Su `__service__` apunta a `LoanService`, que maneja la creación, cierre y actualización de estado de los préstamos.

### Servicios principales
- `AssetService`: `mark_maintenance()`, `release_maintenance()` (manejo de mantenimiento).
- `LoanService`: `create()` (valida disponibilidad y crea préstamo), `return_asset()` (cierra préstamo), `search()` (detecta vencidos).

### Funcionalidades clave
- Validación de disponibilidad al crear préstamos.
- Conversión automática de fechas `dd/mm/yyyy` a UTC.
- Actualización automática de estados vencidos.
- Acciones administrativas con permisos (`asset_lending_group_manager`).

---

## 2. Módulo `community_events`

### Objetivo
Administrar eventos comunitarios, sesiones y inscripciones, facilitando la organización, publicación y gestión de asistencia para promover la participación.

### Estructura de archivos
- `__manifest__.yaml`: Definición del módulo.
- `models/`: `event.py`, `registration.py`, `session.py`.
- `services/`: `event.py`, `registration.py`.
- `data/`: ACL, grupos, configuraciones (`settings.yml`).
- `views/`: Menús y vistas UI.
- `tests/`: Pruebas de eventos.

### Modelos clave
Los archivos de modelo definen la estructura de datos y los servicios asociados para operaciones CRUD y acciones específicas.
- `Event`: Modelo principal de eventos. Su `__service__` apunta a `EventService`, que administra publicación, cierre, cancelación y reapertura.
- `Registration`: Modelo de inscripciones. Su `__service__` apunta a `RegistrationService`, que valida eventos publicados y gestiona confirmaciones, listas de espera y check-ins.
- `Session`: Modelo de sesiones. Asociado a `SessionService` como servicio base; se usa para vincular sesiones a eventos y en las vistas.

### Servicios principales
- `EventService`: `publish_event()`, `close_registration()`, `cancel_event()`, `reopen_event()`; normaliza fechas en `create()`/`update()`.
- `RegistrationService`: `confirm()`, `move_waitlist()`, `checkin()`, `bulk_checkin()`; valida eventos publicados en `create()`.

### Funcionalidades clave
- Normalización de fechas para eventos.
- Flujo de estados para eventos e inscripciones.
- Check-in individual y masivo.
- Acceso público a eventos publicados; permisos por grupos (`community_events_group_staff`).
- Configuraciones como capacidad por defecto y recordatorios.

---

## 3. Módulo `feedback_moderation`

### Objetivo
Moderación de feedback comunitario, permitiendo revisar, publicar o rechazar sugerencias y comentarios para mantener contenido apropiado y fomentar mejoras.

### Estructura de archivos
- `__manifest__.yaml`: Definición del módulo.
- `models/feedback.py`: Modelos `Suggestion`, `Comment`, `Tag`.
- `services/feedback.py`: Servicios `SuggestionService`, `CommentService`, `TagService`.
- `data/`: Grupos y ACL.
- `views/`: UI para moderación.

### Modelos clave
Los archivos de modelo definen las entidades de moderación y permiten al framework enlazar cada modelo con su servicio correspondiente.
- `Suggestion`: Modelo de sugerencias. Su `__service__` apunta a `SuggestionService`, que opera la publicación, rechazo, fusión y votación.
- `Comment`: Modelo de comentarios. Su `__service__` apunta a `CommentService`, que administra la moderación de comentarios.
- `Tag`: Modelo de etiquetas. Su `__service__` apunta a `TagService` y se usa para categorizar sugerencias.

### Servicios principales
- `SuggestionService`: `publish()`, `reject()`, `merge()`, `reopen()`, `vote()`, `get_moderation_queue()`.
- `CommentService`: `publish_comment()`, `reject_comment()`.
- `TagService`: Servicio base para etiquetas.

### Funcionalidades clave
- Flujo de moderación con notas internas.
- Votación en sugerencias.
- Fusión de sugerencias duplicadas.
- Acciones restringidas a moderadores (`feedback_group_moderator`).
- Serialización de resultados para API.

---

## Observaciones generales
- **Herencia**: Todos los servicios heredan de `BaseService`.
- **Permisos**: Controlados con `@exposed_action()` y grupos de seguridad.
- **Persistencia**: Usa `self.repo.session` (SQLAlchemy).
- **Campos**: Definidos con `field()` para metadata (público, editable, choices).
- **UI**: Vistas alineadas con estados de modelo y permisos.
- **Validaciones**: Estado y existencia verificados antes de cambios.
- **Serialización**: Resultados devueltos con `serialize()`.