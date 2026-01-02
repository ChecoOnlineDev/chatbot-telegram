from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", 5432)

#cambiar el host al nombre del servicio definido en el docker compose en produccion
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#punto de entrada a bd
engine = create_engine(str(DATABASE_URL))

#fabrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#funcion helper que obtiene sesiones de la bd
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()