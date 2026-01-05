# 🦅 XROM Systems Bot: Anatomía y Guía Técnica

> "La simplicidad es la máxima sofisticación." - Leonardo da Vinci

Este documento desglosa el bot de Telegram de XROM Systems. No solo explica *qué* hace, sino *por qué* está diseñado así y *cómo* fluye la información átomo por átomo.

---

## 🏗 El Concepto: Clean Architecture

Imagina tu software como una cebolla.
*   **El Centro (Dominio)**: Son tus reglas sagradas. "Un usuario tiene una sesión", "Un ticket tiene un folio". No saben nada de Telegram ni de bases de datos.
*   **La Capa Media (Aplicación)**: Son los gerentes. Dicen: "Cuando alguien pida un folio, búscalo y responde". Coordinan, pero no hacen el trabajo sucio.
*   **La Capa Externa (Infraestructura)**: Son los obreros. Telegram, Postgres, Redis. Aquí está el código que se ensucia las manos.

Esta separación permite que si mañana Telegram desaparece y te mudas a WhatsApp, **tu centro y capa media no cambian**. Solo cambias los obreros externos.

---

## 💉 El Corazón: Inyección de Dependencias (`Container`)

Aquí ocurre la magia. En lugar de que tus archivos digan `import Postgres`, dicen "Necesito *una* base de datos, no me importa cuál". El `Container` es quien se encarga de darles esa base de datos al arrancar.

### 📜 Archivo: `src/infrastructure/container.py`

Es el director de orquesta. **De aquí nace todo.**

```python
class Container(containers.DeclarativeContainer):
    
    # 1. Configuración
    # Lee tu archivo .env y lo hace accesible
    config = providers.Configuration()

    # 2. Recursos Compartidos (Infraestructura Base)
    # Crea UNA sola conexión a la DB y a Redis para toda la app.
    db = providers.Singleton(Database, db_url=config.db.url)
    
    # 3. Adaptadores (Los Obreros)
    # Aquí dice: "Cuando alguien pida un ISessionRepository, dale un RedisSessionAdapter"
    user_session_repository = providers.Factory(
        RedisSessionAdapter, 
        redis_client=redis_resource
    )

    # 4. Casos de Uso (Los Gerentes)
    # Inyecta al obrero (repo) dentro del gerente (Use Case)
    # 4. Casos de Uso (Los Gerentes)
    # Inyecta al obrero (repo) dentro del gerente (Use Case)
    handle_conversation_use_case = providers.Factory(
        HandleConversationUseCase,
        session_repo=user_session_repository,  # <--- CONEXIÓN MÁGICA
        views=bot_views_dict,
        get_service_use_case=get_service_by_folio_use_case
    )

    # Nota: Se eliminó el BotController para simplificar el flujo. 
    # Los Handlers llaman directamente al Use Case.
```

---

## 🗺 Mapa de Dependencias: ¿Quién llama a quién?

Esta sección explica de dónde viene cada pieza clave en los archivos principales.

### 1. `telegram_handlers.py` (La Entrada)
*   **Ubicación**: `src/infrastructure/presentation/bot/handlers/`
*   **Rol**: Traducir "Telegram" a "Python Puro".
*   **Importa y Usa**:
    *   `HandleConversationUseCase` (Inyectado por el Container).
    *   `HandleMessageDto` (De `src/application/dtos/bot_dtos.py`): Para empaquetar los datos.
    *   `dependency_injector.wiring`: `Provide` y `inject` para pedirle ayuda al Contenedor.

### 2. `handler_conversation.py` (El Cerebro)
*   **Ubicación**: `src/application/use_cases/`
*   **Rol**: Máquina de estados. Decide si estás saludando, pidiendo folio o en soporte.
*   **Importa y Usa**:
    *   `ISessionRepository` (Interfaz en `src/domain/ports/`): Para leer/guardar estado del usuario (sin saber que es Redis).
    *   `bot_views.py` (De `src/infrastructure/presentation/bot/views/`): Para saber QUÉ texto responder.

---

## 🔄 El Flujo TOTAL (Start-to-Finish)

Sigue la ruta de una petición desde que le das `Enter` en la terminal hasta que el usuario ve el mensaje.

### Fase 1: El Arranque (`main.py`)
1.  **Ejecución**: Corres `python main.py`.
2.  **Container**: Se crea `container = Container()`.
3.  **Wiring**: `container.init_resources()` conecta todos los cables. Ahora las funciones con `@inject` ya tienen sus dependencias listas.
4.  **Bot**: `ApplicationBuilder` arranca el loop de Telegram y carga los handlers.

### Fase 2: El Mensaje ("Consultar Folio")
5.  **Telegram**: El usuario escribe "consultar folio". Telegram API envía un JSON al bot.
6.  **Handler**: `telegram_handlers.handle_telegram_message` atrapa el JSON.
    *   Extrae `user_id`, `text`.
    *   Crea `HandleMessageDto`.
    *   Llama a `conversation_handler.execute(input_dto)`.

### Fase 3: La Decisión (Clean Core)
7.  **Use Case**:
    *   Llama al Repo (`Redis`) -> "Dame la sesión del usuario 123".
    *   El Repo (`RedisSessionAdapter`) descarga de Redis y devuelve un objeto `UserSession`.
    *   El Use Case ve: Estado actual = `MAIN_MENU`. Mensaje = "consultar folio".
    *   Lógica: "Ah, quiere consultar. Cambio estado a `WAITING_FOR_FOLIO`".
    *   Llama al Repo (`Redis`) -> "Guarda la nueva sesión".
    *   Busca la Vista: `views['consult'].request_folio_message()`.

### Fase 4: La Respuesta
8.  **Vista**: `bot_views.py` retorna un objeto `BotResponse`:
    *   Texto: `<b>Consulta de Servicio</b>...` (HTML)
    *   Botones: `["volver al menu"]`
9.  **Vuelta atrás**:
    *   Vista -> Use Case -> Handler.
10. **Handler (`Telegram`)**:
    *   Recibe el `BotResponse`.
    *   Convierte la lista de botones a `InlineKeyboardMarkup`.
    *   Dispara: `update.effective_message.reply_text(..., parse_mode='HTML')`.

11. **Usuario**: Ve el mensaje bonito en su celular. 📱

---

Esta estructura garantiza que puedes cambiar Redis por Mongo, o Telegram por WhatsApp, sin romper la lógica de tu negocio (`Fase 3`). Eso es Clean Architecture.
