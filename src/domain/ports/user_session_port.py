from abc import ABC, abstractmethod
from src.domain.entities.user_session import UserSession

class ISessionRepository(ABC):
    @abstractmethod
    def get_session(self, user_id: int) -> UserSession:
        pass

    @abstractmethod
    def save_session(self, user_id: int, session: UserSession) -> None:
        pass