from typing import Any
from src.domain.constants import BotState
from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserSession:
    state: BotState
    metadata: dict[str, Any] = field(default_factory=dict)