from dataclasses import dataclass
from datetime import datetime
from src.domain.constants import TechnicalServiceStatus

@dataclass(frozen=True)
class TechnicalServiceEntity:
    folio: str
    status: TechnicalServiceStatus
    reception_date: datetime
    service_reason: str
    
    #campos opcionales que aparecen segun el status del servicio
    service_summary: str | None
    on_hold_reason: str | None
    cancellation_reason: str | None
    completion_date: datetime | None
    delivered_at: datetime | None
    is_delivered : bool | None = False #este status solo es posible activarlo 
    #cuando el status sea o cancelado o terminado