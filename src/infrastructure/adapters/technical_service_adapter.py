from sqlalchemy.orm import Session
from src.domain.entities.technical_service import TechnicalServiceEntity
from src.domain.ports.technical_service_port import ITechnicalService
from src.infrastructure.database.models import TechnicalService

"""Clase que ejecuta todas las funciones definidas en el port"""
class SQLAlchemyTechnicalServiceAdapter(ITechnicalService):
    def __init__(self, session: Session):
        self.session = session

    def get_service_by_folio(self, folio: str) -> TechnicalServiceEntity | None:
        #hacemos la busqueda en la bd
        service = self.session.query(TechnicalService).filter(
            TechnicalService.folio == folio
        ).first()

        #si no existe el servicio retornamos None
        if not service:
            return None
        
        #mapeamos y convertimos de datos crudos de la bd a entidad de dominio
        service_entity = TechnicalServiceEntity(
            folio=service.folio,
            status=service.status,
            reception_date=service.reception_date,
            service_reason=service.service_reason,
            service_summary=service.service_summary,
            on_hold_reason=service.on_hold_reason,
            cancellation_reason=service.cancellation_reason,
            completion_date=service.completion_date,
            delivered_at=service.delivered_at,
            is_delivered=service.is_delivered
        )
        
        return service_entity