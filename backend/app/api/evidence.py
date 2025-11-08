from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.db.database import get_db
from app.models.models import Evidence
from app.core.config import settings
import os

router = APIRouter()


@router.get("/{evidence_id}")
async def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db)
):
    """Obtener evidencia (frame o clip) por ID"""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    
    file_path = Path(evidence.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        file_path,
        media_type=evidence.mime_type or "image/jpeg",
        filename=file_path.name
    )


@router.get("/incident/{incident_id}")
async def get_incident_evidence(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todas las evidencias de un incidente"""
    evidences = db.query(Evidence).filter(Evidence.incident_id == incident_id).all()
    return [{
        "id": e.id,
        "type": e.evidence_type,
        "file_path": e.file_path,
        "created_at": e.created_at
    } for e in evidences]

