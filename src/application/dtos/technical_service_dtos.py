from pydantic import BaseModel
from src.application.dtos.bot_dtos import BotResponse


#mensaje que recibimos del usuario
class ServiceQueryRequest(BaseModel):
    message_text: str

#Dto de detalles de servicio estandarizados
class ServiceDetailsDto(BaseModel):
    folio: str
    status: str
    reception_date: str
    service_reason: str
    service_summary: str | None = None
    completion_date: str | None = None
    is_delivered: bool = False

#respuesta estandarizada para el usuario
class ServiceInfoResponse(BaseModel):
    found: bool = False
    friendly_message: str | BotResponse
    service_details: ServiceDetailsDto | None = None
    
