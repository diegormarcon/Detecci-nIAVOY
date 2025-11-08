from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CameraBase(BaseModel):
    name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rtsp_url: Optional[str] = None
    web_url: Optional[str] = None
    is_active: bool = True
    speed_limit: Optional[float] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rtsp_url: Optional[str] = None
    web_url: Optional[str] = None
    is_active: Optional[bool] = None
    speed_limit: Optional[float] = None
    calibration_matrix: Optional[List[List[float]]] = None
    calibration_points: Optional[Dict[str, Any]] = None


class CameraResponse(CameraBase):
    id: int
    calibration_matrix: Optional[List[List[float]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class IncidentBase(BaseModel):
    camera_id: int
    incident_type: str
    detected_class: Optional[str] = None
    track_id: Optional[int] = None
    speed_kmh: Optional[float] = None
    speed_limit: Optional[float] = None
    bbox: List[float] = Field(..., min_items=4, max_items=4)
    confidence: Optional[float] = None
    license_plate: Optional[str] = None
    timestamp: datetime
    extra_data: Optional[Dict[str, Any]] = None


class IncidentCreate(IncidentBase):
    frame_path: Optional[str] = None
    clip_path: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: int
    frame_path: Optional[str] = None
    clip_path: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class IncidentFilter(BaseModel):
    camera_id: Optional[int] = None
    incident_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    license_plate: Optional[str] = None
    min_speed: Optional[float] = None
    status: Optional[str] = None
    limit: int = 100
    offset: int = 0


class EventMessage(BaseModel):
    type: str  # detection, incident, speed, etc.
    camera_id: int
    data: Dict[str, Any]
    timestamp: datetime


class CalibrationRequest(BaseModel):
    pixel_points: List[List[float]] = Field(..., min_items=4, max_items=4)
    real_points: List[List[float]] = Field(..., min_items=4, max_items=4)  # En metros

