from dataclasses import dataclass, field
from enum import Enum, auto

#posibles estados de la conversacion con el bot
class BotState(Enum):
    START = auto()
    MAIN_MENU = auto()
    WAITING_FOR_FOLIO = auto()
    AI_ASSISTANT = auto()
    SUPPORT_CONNECT = auto()

#Opciones del menu principal del bot
class MainMenuOptions(Enum):
    CONSULTAR = "Consultar folio"
    IA = "Asistente IA"
    SOPORTE = "Soporte"
    VOLER = "Volver al menu principal"

#status posibles de un servicio tecnico a consultar
class TechnicalServiceStatus(Enum):
    PENDING = "pendiente"
    IN_PROGRESS = "en progreso"
    ON_HOLD = "en espera"
    COMPLETED = "completado"
    CANCELLED = "cancelado"
    

#estadarizando las respuestas del bot
@dataclass
class BotResponse:
    text: str
    buttons: list[str] = field(default_factory=list)

#Modelo de mensajes estandar que recibira el bot (lo que ocuparemos)
@dataclass
class HandleMessageDto:
    user_id: int
    message_text: str
    user_name: str