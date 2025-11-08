# Script de inicialización de la base de datos
# Este script crea las tablas necesarias

from app.db.database import engine, Base
from app.models.models import Camera, Incident, Evidence

if __name__ == "__main__":
    print("Creando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente!")

