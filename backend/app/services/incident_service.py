from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.models.models import Incident
from app.schemas.schemas import IncidentCreate, IncidentFilter
import logging

logger = logging.getLogger(__name__)


class IncidentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_incident(self, incident_data: IncidentCreate) -> Incident:
        """Crear un nuevo incidente"""
        incident = Incident(**incident_data.model_dump())
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        logger.info(f"Incidente creado: {incident.id}")
        return incident
    
    def get_incident_by_id(self, incident_id: int) -> Optional[Incident]:
        """Obtener incidente por ID"""
        return self.db.query(Incident).filter(Incident.id == incident_id).first()
    
    def get_incidents(self, filters: IncidentFilter) -> List[Incident]:
        """Obtener incidentes con filtros"""
        query = self.db.query(Incident)
        
        if filters.camera_id:
            query = query.filter(Incident.camera_id == filters.camera_id)
        
        if filters.incident_type:
            query = query.filter(Incident.incident_type == filters.incident_type)
        
        if filters.start_date:
            query = query.filter(Incident.timestamp >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Incident.timestamp <= filters.end_date)
        
        if filters.license_plate:
            query = query.filter(Incident.license_plate.ilike(f"%{filters.license_plate}%"))
        
        if filters.min_speed:
            query = query.filter(Incident.speed_kmh >= filters.min_speed)
        
        if filters.status:
            query = query.filter(Incident.status == filters.status)
        
        query = query.order_by(Incident.timestamp.desc())
        query = query.offset(filters.offset).limit(filters.limit)
        
        return query.all()
    
    def update_status(self, incident_id: int, status: str) -> Optional[Incident]:
        """Actualizar estado de un incidente"""
        incident = self.get_incident_by_id(incident_id)
        if incident:
            incident.status = status
            self.db.commit()
            self.db.refresh(incident)
        return incident

