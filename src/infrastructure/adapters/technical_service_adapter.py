from sqlalchemy.orm import Session
from src.domain.entities.technical_service import TechnicalService
from src.domain.ports.technical_service_port import ITechnicalService
from src.infrastructure.database.models import TechnicalServiceModel

class SQLAlchemyTechnicalServiceAdapter(ITechnicalService):
    """Clase que ejecuta todas las funciones definidas en el port"""
    def __init__(self, session: Session):
        self.session = session

    def get_service_by_folio(self, folio: str) -> TechnicalService | None:
        #hacemos la busqueda en la bd
        service_model = self.session.query(TechnicalServiceModel).filter(
            TechnicalServiceModel.folio == folio
        ).first()

        #si no existe el servicio retornamos None
        if not service_model:
            return None
        
        #mapeamos y convertimos de datos crudos de la bd a entidad de dominio
        return TechnicalService(
            service_id=service_model.service_id,
            folio=service_model.folio,
            status=service_model.status,
            reception_date=service_model.reception_date,
            service_reason=service_model.service_reason,
            service_summary=service_model.service_summary,
            on_hold_reason=service_model.on_hold_reason,
            cancellation_reason=service_model.cancellation_reason,
            completion_date=service_model.completion_date,
            delivered_at=service_model.delivered_at,
            is_delivered=service_model.is_delivered
        )