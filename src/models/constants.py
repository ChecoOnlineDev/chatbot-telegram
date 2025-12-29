from dataclasses import field, dataclass
from enum import Enum, auto
from typing import List

#posibles estados de la conversacion con el bot
class BotState(Enum):
    START = auto()
    MAIN_MENU = auto()
    WAITING_FOR_FOLIO = auto()
    AI_ASSISTANT = auto()
    SUPPORT_CONNECT = auto()

class MainMenuOptions(Enum):
    CONSULTAR = "Consultar folio"
    IA = "Asistente IA"
    SOPORTE = "Soporte"
    VOLER = "Volver al menu principal"
    

@dataclass
class BotResponse:
    text: str
    buttons: List[str] = field(default_factory=list)