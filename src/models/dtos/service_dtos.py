from dataclasses import dataclass

@dataclass(frozen=True)
class FolioDto:
    raw_text: str
    normalized_folio: str | None

#info que viene del modelo de folio service en la bd
@dataclass(frozen=True)
class ServiceStatusDto:
    folio: str
    status: str
    technician_name: str
    last_update: str

@dataclass(frozen=True)
class ButtonsDto:
    text: str
    buttons: list[str]
    
@dataclass(frozen=True)
class HandleMessageDto:
    user_id: int          # ID único para rastrear el estado (user_states)
    message_text: str     # Lo que el usuario escribió
    user_name: str   # Opcional, para personalizar mensajes