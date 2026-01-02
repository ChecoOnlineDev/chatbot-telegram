from src.infrastructure.database.configuration import SessionLocal
from src.infrastructure.adapters.technical_service_adapter import SQLAlchemyTechnicalServiceAdapter
from src.application.use_cases.get_service_by_folio import GetServiceByFolioUseCase
from src.application.dtos.bot_dtos import HandleMessageDto
import json

def run_test():
    # 1. Preparar la conexión (Infraestructura)
    db_session = SessionLocal()
    
    try:
        # 2. Instanciar el adaptador (Repository)
        # Asegúrate de que el nombre de la clase sea el que definimos antes
        repository = SQLAlchemyTechnicalServiceAdapter(db_session)
        
        # 3. Instanciar el Caso de Uso (Aplicación)
        # Inyectamos el adaptador en el puerto
        use_case = GetServiceByFolioUseCase(service_port=repository)
        
        # 4. Simular entradas del usuario (Diferentes casos)
        test_inputs = [
            "Hola, quiero saber de mi folio xrom-12345",   # Folio válido (sucio)
            "Estado del pedido XROM ABCDE",                 # Folio con espacios
            "No tengo idea de qué es un folio",           # Sin folio
            "XROM-999"                                  # Folio que no existe en DB
        ]
        
        print("--- INICIANDO PRUEBAS DE XROM SYSTEMS ---\n")
        
        for text in test_inputs:
            print(f"📥 Usuario dice: '{text}'")
            
            # Crear el DTO de entrada
            request_dto = HandleMessageDto(
                user_id=123,
                user_name="Usuario Test",
                message_text=text
            )
            
            # EJECUTAR CASO DE USO
            response = use_case.execute(request_dto)
            
            # 5. Mostrar resultados
            print(f"🤖 Bot responde: {response.friendly_message}")
            
            if response.found and response.service_details:
                # Imprimir detalles en formato JSON bonito para debug
                details = response.service_details.model_dump()
                print(f"📊 Detalles Técnicos: {json.dumps(details, indent=2, ensure_ascii=False)}")
            
            print("-" * 40)

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    run_test()