from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import datetime


class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    rtsp_url = Column(String(500))
    web_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    calibration_matrix = Column(JSON)  # Matriz de homografía para velocidad
    calibration_points = Column(JSON)  # Puntos de calibración
    speed_limit = Column(Float)  # Límite de velocidad en km/h
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    incidents = relationship("Incident", back_populates="camera")


class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    incident_type = Column(String(50), nullable=False)  # speed, helmet, zone_invasion, etc.
    detected_class = Column(String(50))  # car, motorcycle, person, etc.
    track_id = Column(Integer)  # ID del tracker
    speed_kmh = Column(Float)  # Velocidad detectada
    speed_limit = Column(Float)  # Límite de velocidad
    bbox = Column(JSON)  # [x1, y1, x2, y2]
    confidence = Column(Float)
    license_plate = Column(String(20))  # Matrícula detectada
    timestamp = Column(DateTime(timezone=True), nullable=False)
    frame_path = Column(String(500))  # Ruta al frame guardado
    clip_path = Column(String(500))  # Ruta al clip de video
    extra_data = Column(JSON)  # Metadatos adicionales
    status = Column(String(20), default="pending")  # pending, reviewed, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    camera = relationship("Camera", back_populates="incidents")


class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    evidence_type = Column(String(20))  # frame, clip, metadata
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Tamaño en bytes
    mime_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

