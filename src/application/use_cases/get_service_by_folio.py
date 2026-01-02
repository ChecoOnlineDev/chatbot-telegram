from src.application.dtos.bot_dtos import HandleMessageDto
from src.application.dtos.technical_service_dtos import ServiceDetailsDto, ServiceInfoResponse
from src.domain.ports.technical_service_port import ITechnicalService
from src.application.services.folio_validator import FolioValidatorService

class GetServiceByFolioUseCase:
    def __init__(
        self,
        service_port: ITechnicalService
    ):
        self.service_port = service_port
    
    def execute(self, request: HandleMessageDto) -> ServiceInfoResponse:
        folio = FolioValidatorService.extract_and_validate_folio(request.message_text)
        
        #si no se encuentra un folio valido en el mensaje del usuario
        if not folio:
            return ServiceInfoResponse(
                found = False,
                friendly_message="No se encontro un folio valido en tu mensaje, verifica y vuelve a intentar"
            )
            
        found_service_entity = self.service_port.get_service_by_folio(folio)
        
        #si no se encuentra ningun servicio asociado a ese folio
        if not found_service_entity:
            return ServiceInfoResponse(
                found= False,
                friendly_message=f"No se encontro ningun registro de algun servicio asociado al folio {folio}"
            )
        return self.build_success_response(found_service_entity)
    
    
    
    def build_success_response(self, entity) -> ServiceInfoResponse:
        #formato de fecha
        date_fmt = "%d/%m/%Y"
        
        # Diccionario de traducción de estados
        status_translations = {
            "PENDING": "📥 Recibido",
            "IN_PROGRESS": "🛠️ En proceso",
            "COMPLETED": "✅ Terminado",
            "CANCELLED": "🚫 Cancelado",
            "ON_HOLD": "⏳ En espera"
        }
        
        status_friendly = status_translations.get(entity.status.name, entity.status.value)

        # Creamos el objeto de detalles (el tercer atributo que pediste)
        details = ServiceDetailsDto(
            folio=entity.folio,
            status=status_friendly, # type: ignore
            reception_date=entity.reception_date.strftime(date_fmt),
            service_reason=entity.service_reason,
            service_summary=entity.service_summary,
            completion_date=entity.completion_date.strftime(date_fmt) if entity.completion_date else None,
            is_delivered=entity.is_delivered
        )

        # Construimos el mensaje amigable final
        msg = f"¡Hola! 👋 El folio **{details.folio}** está: **{details.status}**."
        if entity.status.name == "COMPLETED":
            msg += "\n\nYa puedes pasar por tu equipo a la sucursal."

        return ServiceInfoResponse(
            found=True,
            friendly_message=msg,
            service_details=details
        )
        