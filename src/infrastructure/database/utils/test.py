from datetime import datetime, timedelta
from src.infrastructure.database.configuration import SessionLocal
from src.infrastructure.database.models import TechnicalService
from src.domain.constants import TechnicalServiceStatus
# from src.application.services.folio_validator import FolioValidatorService 

def insert_test_data():
    db = SessionLocal()
    
    # Estos folios ya cumplen con el formato XROM-XXXXX que produce tu Regex
    test_services = [
        {
            "folio": "XROM-12345", 
            "status": TechnicalServiceStatus.PENDING,
            "reason": "Mantenimiento preventivo laptop gaming",
            "summary": "Limpieza interna y cambio de pasta térmica."
        },
        {
            "folio": "XROM-ABCDE", 
            "status": TechnicalServiceStatus.IN_PROGRESS,
            "reason": "Mantenimiento de Hardware",
            "summary": "Revisión de voltajes en fuente de poder."
        },
        {
            "folio": "XROM-999", 
            "status": TechnicalServiceStatus.COMPLETED,
            "reason": "Instalación de Software",
            "summary": "Se instaló suite de diseño y drivers actualizados."
        }
    ]

    try:
        for data in test_services:
            # Verificamos si ya existe
            exists = db.query(TechnicalService).filter_by(folio=data["folio"]).first()
            if not exists:
                new_service = TechnicalService(
                    folio=data["folio"],
                    status=data["status"],
                    reception_date=datetime.now() - timedelta(days=2),
                    service_reason=data["reason"],
                    service_summary=data["summary"],
                    is_delivered=False
                )
                db.add(new_service)
                print(f"✅ Insertado: {data['folio']}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
    
    #python -m src.infrastructure.database.utils.test comando para ejecutar el script