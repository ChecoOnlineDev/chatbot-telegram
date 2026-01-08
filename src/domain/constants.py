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
    CONSULTAR = "Consultar Folio"
    IA = "Asistente IA"
    SOPORTE = "Soporte"
    VOLVER = "Volver Al Menú Principal"

#status posibles de un servicio tecnico a consultar
class TechnicalServiceStatus(Enum):
    PENDING = "pendiente"
    IN_PROGRESS = "en progreso"
    ON_HOLD = "en espera"
    COMPLETED = "completado"
    CANCELLED = "cancelado"

class Platform(Enum):
    TELEGRAM = "TELEGRAM"
    WHATSAPP = "WHATSAPP"

