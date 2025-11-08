from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.schemas import (
    CameraCreate, CameraResponse, CameraUpdate, CalibrationRequest
)
from app.services.camera_service import CameraService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=CameraResponse)
async def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva cámara"""
    service = CameraService(db)
    return service.create_camera(camera)


@router.get("/", response_model=List[CameraResponse])
async def list_cameras(
    is_active: bool = Query(None),
    db: Session = Depends(get_db)
):
    """Listar todas las cámaras"""
    service = CameraService(db)
    return service.get_cameras(is_active)


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una cámara por ID"""
    service = CameraService(db)
    camera = service.get_camera_by_id(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    camera_update: CameraUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una cámara"""
    service = CameraService(db)
    camera = service.update_camera(camera_id, camera_update)
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return camera


@router.post("/{camera_id}/calibrate", response_model=CameraResponse)
async def calibrate_camera(
    camera_id: int,
    calibration: CalibrationRequest,
    db: Session = Depends(get_db)
):
    """Calibrar una cámara para medición de velocidad"""
    service = CameraService(db)
    camera = service.calibrate_camera(camera_id, calibration)
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return camera

