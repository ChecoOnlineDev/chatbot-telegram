# Documentación Técnica del Proyecto XROM Systems Bot

Este documento describe la arquitectura, flujo de datos y procedimientos para extender o modificar la funcionalidad del bot de Telegram.

## Arquitectura

El proyecto sigue una **Arquitectura Hexagonal (Ports and Adapters)** para desacoplar la lógica de negocio de la infraestructura externa.

### Estructura de Directorios Clave

*   `src/domain/`: **Núcleo**. Contiene Entidades (`UserSession`, `TechnicalService`), Puertos (Interfaces `ISessionRepository`) y Constantes (`BotState`). **Sin dependencias externas.**
*   `src/application/`: **Lógica de Negocio**. Contiene Casos de Uso (`HandleConversationUseCase`) y DTOs. Orquesta el flujo.
*   `src/infrastructure/`: **Implementación**. Contiene Adaptadores (`telegram_handlers`, `sqlalchemy_adapter`), Base de Datos, Redis y el Contenedor de Inyección.

---

## Guía de Desarrollo: Cómo Modificar el Bot

A continuación se detallan los pasos exactos y líneas de código necesarias para cambios comunes.

### 1. Agregar una Opción al Menú Principal

**Objetivo**: Agregar un botón "Ubicación" que responda con una dirección fija.

#### Paso 1: Definir la Constante (Dominio)
Archivo: `src/domain/constants.py`
```python
class MainMenuOptions(Enum):
    CONSULTAR = "Consultar Folio"
    IA = "Asistente IA"
    SOPORTE = "Soporte"
    UBICACION = "Ubicación"  # <-- AGREGAR ESTO
```

#### Paso 2: Crear la Respuesta Visual (Infraestructura)
Archivo: `src/infrastructure/presentation/bot/views/bot_views.py`

1.  Actualizar la lista de botones en `NavigationMenuBotView`:
    ```python
    def main_menu_buttons() -> list:
        return [
            MainMenuOptions.CONSULTAR.value,
            MainMenuOptions.UBICACION.value, # <-- AGREGAR ESTO
            # ...
        ]
    ```
2.  Crear el método que retorna el mensaje en `CommonBotView`:
    ```python
    @staticmethod
    def location_message() -> BotResponse:
        return BotResponse(
            text="📍 Estamos ubicados en Av. Tecnológico #123, Centro.",
            buttons=NavigationMenuBotView.back_to_main_menu_button()
        )
    ```

#### Paso 3: Conectar la Lógica del Menú (Aplicación)
Archivo: `src/application/use_cases/handler_conversation.py`

En el método `_handle_main_menu`:
```python
    def _handle_main_menu(self, dto: HandleMessageDto, session: UserSession) -> BotResponse:
        selection = dto.message_text.strip().lower()

        # ... otros if ...

        # <-- AGREGAR ESTE BLOQUE
        if selection == MainMenuOptions.UBICACION.value.lower():
             return self.views['common'].location_message()
```

---

### 2. Cambiar de Tecnología (Refactorización)

**Objetivo**: Cambiar el almacenamiento de sesiones de **Redis** a **Memoria RAM (Diccionario)** para desarrollo local sin Docker.

#### Paso 1: Crear el Nuevo Adaptador
Archivo Nuevo: `src/infrastructure/adapters/memory_session_adapter.py`

Debe implementar la interfaz del dominio `ISessionRepository`.

```python
from typing import Dict
from src.domain.ports.user_session_port import ISessionRepository
from src.domain.entities.user_session import UserSession

class MemorySessionRepository(ISessionRepository):
    def __init__(self):
        self._storage: Dict[int, UserSession] = {}

    def save_session(self, user_id: int, session: UserSession) -> None:
        self._storage[user_id] = session

    def get_session(self, user_id: int) -> UserSession:
        return self._storage.get(user_id, UserSession()) # Retorna sesión default si no existe
```

#### Paso 2: Cambiar la Inyección de Dependencias
Archivo: `src/infrastructure/container.py`

El contenedor controla qué implementación usa toda la aplicación. Solo necesitas cambiarlo aquí.

```python
# Importar el nuevo adaptador
from src.infrastructure.adapters.memory_session_adapter import MemorySessionRepository

class Container(containers.DeclarativeContainer):
    
    # ... (configuraciones previas)

    # COMENTAR O ELIMINAR LA IMPLEMENTACIÓN DE REDIS
    # session_repository = providers.Factory(
    #     RedisSessionAdapter,
    #     client=redis_client
    # )

    # AGREGAR LA NUEVA IMPLEMENTACIÓN (Singleton para mantener estado en memoria)
    session_repository = providers.Singleton(
        MemorySessionRepository
    )

    # El resto del código (conversation_handler, etc.) NO SE TOCA.
    # Automáticamente comenzarán a usar MemorySessionRepository.
```

---

### 3. Explicación del Flujo y Container

#### Inyección de Dependencias (`src/infrastructure/container.py`)
Este archivo es el único lugar donde se instancian las clases principales.
*   `providers.Singleton`: Crea una única instancia compartida (ej. Conexión a DB).
*   `providers.Factory`: Crea una instancia nueva cada vez que se inyecta.
*   **Wiring**: Conecta estas instancias con los decoradores `@inject` en los handlers.

#### Flujo de una Solicitud (Ej. "Consultar Folio")

1.  **Entrada**: `telegram_handlers.py` recibe el JSON de Telegram.
2.  **DTO**: Se convierte a `HandleMessageDto` (independiente de Telegram).
3.  **Ejecución**: Se llama a `conversation_handler.execute(dto)`.
4.  **Estado**: El caso de uso pide la sesión al `session_repository` (Redis/Memoria).
5.  **Lógica**:
    *   Verifica `BotState`.
    *   Valida entrada con `FolioValidatorService` (si aplica).
    *   Ejecuta lógica de negocio (ej. buscar en DB vía `get_service_use_case`).
6.  **Salida**: El caso de uso obtiene una respuesta visual de `views` (`bot_views.py`) y la retorna.
7.  **Respuesta**: `telegram_handlers.py` traduce el objeto `BotResponse` a la API de Telegram (`send_message`).

---
*Documentación Técnica Actualizada - XROM Systems*
