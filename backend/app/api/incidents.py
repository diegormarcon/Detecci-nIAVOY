from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.models import Incident, Camera
from app.schemas.schemas import (
    IncidentCreate, IncidentResponse, IncidentFilter,
    CameraCreate, CameraResponse, CameraUpdate, CalibrationRequest
)
from app.services.incident_service import IncidentService
from app.services.camera_service import CameraService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo incidente"""
    service = IncidentService(db)
    return service.create_incident(incident)


@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    camera_id: Optional[int] = Query(None),
    incident_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    license_plate: Optional[str] = Query(None),
    min_speed: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Listar incidentes con filtros"""
    service = IncidentService(db)
    filters = IncidentFilter(
        camera_id=camera_id,
        incident_type=incident_type,
        start_date=start_date,
        end_date=end_date,
        license_plate=license_plate,
        min_speed=min_speed,
        status=status,
        limit=limit,
        offset=offset
    )
    return service.get_incidents(filters)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un incidente por ID"""
    service = IncidentService(db)
    incident = service.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incident


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: int,
    status: str = Query(..., regex="^(pending|reviewed|approved|rejected)$"),
    db: Session = Depends(get_db)
):
    """Actualizar el estado de un incidente"""
    service = IncidentService(db)
    incident = service.update_status(incident_id, status)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return {"status": "updated", "incident_id": incident_id, "new_status": status}

