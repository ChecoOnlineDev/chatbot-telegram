from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

class BotState(Enum):
    START = auto()
    MAIN_MENU = auto()
    WAITING_FOR_FOLIO = auto()
    AI_ASSISTANT = auto()
    SUPPORT_CONNECT = auto()

@dataclass(frozen=True)
class UserSessionDto:
    """Representa el estado guardado en Redis"""
    state: BotState
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        # Convertimos el Enum a string para JSON
        data = asdict(self)
        data['state'] = self.state.name
        import json
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "UserSessionDto":
        import json
        data = json.loads(json_str)
        return cls(
            state=BotState[data['state']],
            metadata=data.get('metadata', {})
        )

@dataclass(frozen=True)
class BotResponseDto:
    """Respuesta estandarizada que el bot enviará al usuario"""
    text: str
    buttons: list[str] = field(default_factory=list)



import redis
import logging

class SessionRepository:
    def __init__(self, redis_client: redis.Redis):
        self.__redis = redis_client
        self.__prefix = "session:"
        self.__ttl = 3600  # 1 hora de expiración para optimizar memoria

    def get_by_user_id(self, user_id: int) -> UserSessionDto:
        try:
            raw_data = self.__redis.get(f"{self.__prefix}{user_id}")
            if not raw_data:
                return UserSessionDto(state=BotState.START)
            return UserSessionDto.from_json(raw_data) # type: ignore
        except Exception as e:
            logging.error(f"Error recuperando sesión de Redis: {e}")
            return UserSessionDto(state=BotState.START)

    def save(self, user_id: int, session: UserSessionDto):
        try:
            self.__redis.set(
                f"{self.__prefix}{user_id}", 
                session.to_json(), 
                ex=self.__ttl
            )
        except Exception as e:
            logging.error(f"Error guardando sesión en Redis: {e}")