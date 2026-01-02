from abc import ABC, abstractmethod
from src.domain.entities.technical_service import TechnicalServiceEntity

class ITechnicalService(ABC):
    """Consulta el servicio tecnico en base al folio, lo mapea y devuelve una entidad de dominio"""
    @abstractmethod
    def get_service_by_folio(self, folio: str) -> TechnicalServiceEntity | None:
        pass