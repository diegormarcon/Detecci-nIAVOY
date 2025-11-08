from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.models import Camera
from app.schemas.schemas import CameraCreate, CameraUpdate, CalibrationRequest
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)


class CameraService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_camera(self, camera_data: CameraCreate) -> Camera:
        """Crear una nueva cámara"""
        camera = Camera(**camera_data.model_dump())
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        logger.info(f"Cámara creada: {camera.id} - {camera.name}")
        return camera
    
    def get_camera_by_id(self, camera_id: int) -> Optional[Camera]:
        """Obtener cámara por ID"""
        return self.db.query(Camera).filter(Camera.id == camera_id).first()
    
    def get_cameras(self, is_active: Optional[bool] = None) -> List[Camera]:
        """Obtener todas las cámaras"""
        query = self.db.query(Camera)
        if is_active is not None:
            query = query.filter(Camera.is_active == is_active)
        return query.all()
    
    def update_camera(self, camera_id: int, camera_update: CameraUpdate) -> Optional[Camera]:
        """Actualizar una cámara"""
        camera = self.get_camera_by_id(camera_id)
        if not camera:
            return None
        
        update_data = camera_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(camera, key, value)
        
        self.db.commit()
        self.db.refresh(camera)
        logger.info(f"Cámara actualizada: {camera_id}")
        return camera
    
    def calibrate_camera(self, camera_id: int, calibration: CalibrationRequest) -> Optional[Camera]:
        """Calibrar una cámara para medición de velocidad"""
        camera = self.get_camera_by_id(camera_id)
        if not camera:
            return None
        
        # Calcular matriz de homografía usando OpenCV
        pixel_points = np.array(calibration.pixel_points, dtype=np.float32)
        real_points = np.array(calibration.real_points, dtype=np.float32)
        
        if len(pixel_points) < 4 or len(real_points) < 4:
            raise ValueError("Se necesitan al menos 4 puntos para calcular la homografía")
        
        homography_matrix, _ = cv2.findHomography(pixel_points, real_points, cv2.RANSAC, 5.0)
        
        if homography_matrix is None:
            raise ValueError("No se pudo calcular la homografía")
        
        # Guardar matriz y puntos de calibración
        camera.calibration_matrix = homography_matrix.tolist()
        # type: ignore[assignment] - SQLAlchemy JSON column acepta dict
        camera.calibration_points = {  # type: ignore
            "pixel_points": calibration.pixel_points,
            "real_points": calibration.real_points
        }
        
        self.db.commit()
        self.db.refresh(camera)
        logger.info(f"Cámara {camera_id} calibrada")
        return camera

