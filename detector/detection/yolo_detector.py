from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
import torch
import logging

logger = logging.getLogger(__name__)


class YOLODetector:
    """Detector de objetos usando YOLOv8"""
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.25, iou_threshold: float = 0.45):
        """
        Inicializar detector YOLO
        
        Args:
            model_path: Ruta al modelo YOLO (.pt)
            confidence: Umbral de confianza mínimo
            iou_threshold: Umbral IoU para NMS
        """
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.iou_threshold = iou_threshold
        
        # Clases de interés para detección de tráfico
        self.class_names = self.model.names
        self.vehicle_classes = {
            'car': 2,
            'motorcycle': 3,
            'bus': 5,
            'truck': 7,
            'person': 0
        }
        
        logger.info(f"Detector YOLO inicializado con modelo: {model_path}")
        logger.info(f"Dispositivo: {self.model.device}")
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detectar objetos en un frame
        
        Args:
            frame: Frame de video (BGR)
            
        Returns:
            Lista de detecciones con formato:
            {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int,
                'class_name': str
            }
        """
        results = self.model.predict(
            frame,
            conf=self.confidence,
            iou=self.iou_threshold,
            verbose=False,
            device=self.model.device
        )
        
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            
            for i in range(len(boxes)):
                box = boxes[i]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = self.class_names[class_id]
                
                # Solo incluir clases de interés
                if class_id in self.vehicle_classes.values() or class_name in ['person', 'bicycle']:
                    detections.append({
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name
                    })
        
        return detections
    
    def detect_helmet(self, frame: np.ndarray, person_bbox: List[float]) -> bool:
        """
        Detectar casco en una región de persona/moto
        
        Args:
            frame: Frame completo
            person_bbox: Bounding box de la persona/moto [x1, y1, x2, y2]
            
        Returns:
            True si se detecta casco, False en caso contrario
        """
        # Recortar región de interés (parte superior del bbox)
        x1, y1, x2, y2 = person_bbox
        height = y2 - y1
        roi = frame[int(y1):int(y1 + height * 0.4), int(x1):int(x2)]
        
        if roi.size == 0:
            return False
        
        # Detectar objetos en ROI (casco sería clase específica si está entrenado)
        # Por ahora, usar detección genérica o modelo específico de casco
        # TODO: Entrenar o usar modelo específico para cascos
        results = self.model.predict(roi, conf=0.3, verbose=False)
        
        # Buscar objetos pequeños en la parte superior (posible casco)
        # Esta es una aproximación simplificada
        return False  # Placeholder - requiere modelo específico de cascos

