# init_db.py
from src.infrastructure.database.configuration import engine
from src.infrastructure.database.models import Base, TechnicalService 

"""Script para tomar todos los modelos asociado a la clase Base y crearlos"""
def create_tables():
    print("Capturando metadatos y creando tablas...")
    try:
        # Esto busca todas las tablas vinculadas a 'Base' y las crea en el 'engine'
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente en la base de datos.")
    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")

if __name__ == "__main__":
    create_tables()
#este script solo funciona una vez porque crea tablas que no existan NO ACTUALIZA