# Script para crear datos de ejemplo

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import Camera
from datetime import datetime

def create_sample_camera():
    """Crear una cámara de ejemplo"""
    db = SessionLocal()
    try:
        camera = Camera(
            name="Cámara Principal - Entrada",
            location="Entrada principal del barrio",
            latitude=-34.6037,
            longitude=-58.3816,
            rtsp_url="rtsp://example.com/stream",
            is_active=True,
            speed_limit=50.0
        )
        db.add(camera)
        db.commit()
        db.refresh(camera)
        print(f"Cámara creada: {camera.id} - {camera.name}")
        return camera
    except Exception as e:
        print(f"Error creando cámara: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creando datos de ejemplo...")
    create_sample_camera()
    print("¡Listo!")

