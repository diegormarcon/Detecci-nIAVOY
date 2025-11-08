from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
import cv2
import sys
import os
import logging
import numpy as np
import io
import base64
from PIL import Image

logger = logging.getLogger(__name__)

router = APIRouter()

# Almacenar frames procesados por cámara
camera_frames = {}

@router.get("/detect")
async def detect_cameras(max_cameras: int = 10):
    """
    Detectar cámaras USB y dispositivos de video disponibles
    """
    available_cameras = []
    
    # Detectar cámaras USB (índices numéricos)
    for i in range(max_cameras):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                    available_cameras.append({
                        'id': i,
                        'name': f'Cámara USB {i}',
                        'source': str(i),
                        'type': 'usb',
                        'resolution': f'{width}x{height}',
                        'fps': fps,
                        'available': True
                    })
                cap.release()
        except Exception as e:
            logger.warning(f"Error probando cámara {i}: {e}")
            continue
    
    # Detectar dispositivos de video Linux (/dev/video*)
    if sys.platform != 'win32':
        for i in range(max_cameras):
            device_path = f'/dev/video{i}'
            if os.path.exists(device_path):
                try:
                    cap = cv2.VideoCapture(device_path)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                            available_cameras.append({
                                'id': f'video{i}',
                                'name': f'Dispositivo Video {i}',
                                'source': device_path,
                                'type': 'device',
                                'resolution': f'{width}x{height}',
                                'fps': fps,
                                'available': True
                            })
                        cap.release()
                except Exception as e:
                    logger.warning(f"Error probando dispositivo {device_path}: {e}")
                    continue
    
    return {
        'cameras': available_cameras,
        'total': len(available_cameras)
    }

@router.get("/stream/{camera_id}")
async def get_camera_stream(camera_id: int):
    """
    Obtener frame actual de la cámara con detecciones
    """
    if camera_id not in camera_frames:
        raise HTTPException(status_code=404, detail="No hay frame disponible para esta cámara")
    
    frame_data = camera_frames[camera_id]
    
    # Convertir frame a JPEG
    _, buffer = cv2.imencode('.jpg', frame_data['frame'], [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    return StreamingResponse(
        io.BytesIO(buffer.tobytes()),
        media_type="image/jpeg"
    )

@router.post("/update-frame/{camera_id}")
async def update_camera_frame_endpoint(camera_id: int, frame: UploadFile = File(...)):
    """
    Actualizar frame de una cámara (llamado por el detector)
    """
    try:
        # Leer imagen del request
        image_data = await frame.read()
        nparr = np.frombuffer(image_data, np.uint8)
        frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame_bgr is not None:
            camera_frames[camera_id] = {
                'frame': frame_bgr,
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
            return {"status": "updated"}
        else:
            return {"status": "error", "message": "No se pudo decodificar la imagen"}
    except Exception as e:
        logger.error(f"Error actualizando frame: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/frame/{camera_id}")
async def get_camera_frame(camera_id: int):
    """
    Obtener frame actual como base64 para mostrar en el frontend
    """
    if camera_id not in camera_frames:
        raise HTTPException(status_code=404, detail="No hay frame disponible para esta cámara")
    
    frame_data = camera_frames[camera_id]
    frame = frame_data['frame']
    
    # Convertir BGR a RGB para mostrar en navegador
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convertir a JPEG y luego a base64
    _, buffer = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 85])
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        'frame': f'data:image/jpeg;base64,{frame_base64}',
        'timestamp': frame_data.get('timestamp'),
        'fps': frame_data.get('fps', 0)
    }
