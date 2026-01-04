from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from src.domain.constants import TechnicalServiceStatus

@dataclass
class TechnicalService:
    folio: str
    service_reason: str
    status: TechnicalServiceStatus
    reception_date: datetime = datetime.utcnow()
    service_id: Optional[int] = None
    service_summary: Optional[str] = None
    on_hold_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    completion_date: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    is_delivered: bool = False