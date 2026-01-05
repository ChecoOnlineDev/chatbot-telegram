from typing import Any, Dict
from pydantic import BaseModel, Field
from src.domain.constants import BotState

class UserSession(BaseModel):
    state: BotState
    metadata: Dict[str, Any] = Field(default_factory=dict)