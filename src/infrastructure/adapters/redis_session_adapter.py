import json
import logging
from redis import Redis
from src.domain.entities.user_session import UserSession
from src.domain.constants import BotState
from src.domain.ports.user_session_port import ISessionRepository
from src.infrastructure.redis.redis_configuration import redis_settings

class RedisSessionRepository(ISessionRepository):
    def __init__(self, client: Redis):
        self.__redis = client
        self.__prefix = "bot_session:"

    def get_session(self, user_id: int) -> UserSession:
        try:
            data = self.__redis.get(f"{self.__prefix}{user_id}")
            if not data:
                return UserSession(state=BotState.START)
            
            decoded = json.loads(data) # type: ignore
            return UserSession(
                state=BotState[decoded['state']],
                metadata=decoded.get('metadata', {})
            )
        except Exception as e:
            logging.error(f"Redis Error: {e}")
            return UserSession(state=BotState.START)

    def save_session(self, user_id: int, session: UserSession) -> None:
        try:
            payload = {
                "state": session.state.name,
                "metadata": session.metadata
            }
            self.__redis.set(
                f"{self.__prefix}{user_id}", 
                json.dumps(payload), 
                ex=redis_settings.SESSION_TTL
            )
        except Exception as e:
            logging.error(f"Redis Save Error: {e}")