import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def calculate_homography_matrix(pixel_points: np.ndarray, real_points: np.ndarray) -> np.ndarray:
    """
    Calcular matriz de homografía para mapear píxeles a coordenadas reales
    
    Args:
        pixel_points: Array de puntos en píxeles (N, 2) - mínimo 4 puntos
        real_points: Array de puntos reales en metros (N, 2) - mínimo 4 puntos
        
    Returns:
        Matriz de homografía (3x3)
    """
    if len(pixel_points) < 4 or len(real_points) < 4:
        raise ValueError("Se necesitan al menos 4 puntos para calcular la homografía")
    
    pixel_points = np.array(pixel_points, dtype=np.float32)
    real_points = np.array(real_points, dtype=np.float32)
    
    # Calcular homografía usando OpenCV
    H, _ = cv2.findHomography(pixel_points, real_points, cv2.RANSAC, 5.0)
    
    if H is None:
        raise ValueError("No se pudo calcular la homografía")
    
    logger.info("Matriz de homografía calculada exitosamente")
    return H


def pixel_to_real(pixel_point: np.ndarray, homography_matrix: np.ndarray) -> np.ndarray:
    """
    Convertir punto de píxeles a coordenadas reales
    
    Args:
        pixel_point: Punto en píxeles [x, y]
        homography_matrix: Matriz de homografía (3x3)
        
    Returns:
        Punto en coordenadas reales [x, y] en metros
    """
    pixel_homogeneous = np.array([pixel_point[0], pixel_point[1], 1.0])
    real_homogeneous = homography_matrix @ pixel_homogeneous
    real_point = real_homogeneous[:2] / real_homogeneous[2]
    return real_point


def calculate_speed(bbox1: List[float], bbox2: List[float], 
                    homography_matrix: np.ndarray,
                    time_delta: float) -> float:
    """
    Calcular velocidad entre dos bounding boxes
    
    Args:
        bbox1: Bounding box inicial [x1, y1, x2, y2]
        bbox2: Bounding box final [x1, y1, x2, y2]
        homography_matrix: Matriz de homografía
        time_delta: Diferencia de tiempo en segundos
        
    Returns:
        Velocidad en km/h
    """
    # Calcular centro de cada bbox
    center1 = np.array([
        (bbox1[0] + bbox1[2]) / 2,
        (bbox1[1] + bbox1[3]) / 2
    ])
    center2 = np.array([
        (bbox2[0] + bbox2[2]) / 2,
        (bbox2[1] + bbox2[3]) / 2
    ])
    
    # Convertir a coordenadas reales
    real1 = pixel_to_real(center1, homography_matrix)
    real2 = pixel_to_real(center2, homography_matrix)
    
    # Calcular distancia en metros
    distance_m = np.linalg.norm(real2 - real1)
    
    # Calcular velocidad (m/s -> km/h)
    if time_delta > 0:
        speed_ms = distance_m / time_delta
        speed_kmh = speed_ms * 3.6
    else:
        speed_kmh = 0.0
    
    return speed_kmh


class SpeedCalculator:
    """Calculador de velocidad para objetos trackeados"""
    
    def __init__(self, homography_matrix: Optional[np.ndarray] = None,
                 fps: int = 10,
                 min_distance: float = 2.0,
                 filter_window: int = 5):
        """
        Inicializar calculador de velocidad
        
        Args:
            homography_matrix: Matriz de homografía (3x3)
            fps: Frames por segundo del video
            min_distance: Distancia mínima en metros para calcular velocidad
            filter_window: Ventana de filtrado para suavizar velocidades
        """
        self.homography_matrix = homography_matrix
        self.fps = fps
        self.min_distance = min_distance
        self.filter_window = filter_window
        self.track_histories: Dict[int, List[Dict[str, Any]]] = {}
        
        logger.info("SpeedCalculator inicializado")
    
    def update_homography(self, homography_matrix: np.ndarray):
        """Actualizar matriz de homografía"""
        self.homography_matrix = homography_matrix
        logger.info("Matriz de homografía actualizada")
    
    def calculate_track_speed(self, track_id: int, bbox: List[float], 
                             timestamp: float) -> Optional[float]:
        """
        Calcular velocidad para un track
        
        Args:
            track_id: ID del track
            bbox: Bounding box actual [x1, y1, x2, y2]
            timestamp: Timestamp del frame
            
        Returns:
            Velocidad en km/h o None si no se puede calcular
        """
        if self.homography_matrix is None:
            logger.warning("Matriz de homografía no configurada")
            return None
        
        # Inicializar historial si no existe
        if track_id not in self.track_histories:
            self.track_histories[track_id] = []
        
        # Agregar punto actual
        self.track_histories[track_id].append({
            'bbox': bbox,
            'timestamp': timestamp
        })
        
        # Mantener solo ventana reciente
        if len(self.track_histories[track_id]) > self.filter_window * 2:
            self.track_histories[track_id] = self.track_histories[track_id][-self.filter_window * 2:]
        
        history = self.track_histories[track_id]
        
        # Necesitamos al menos 2 puntos
        if len(history) < 2:
            return None
        
        # Calcular velocidad usando puntos separados por filter_window
        if len(history) >= self.filter_window:
            idx1 = len(history) - self.filter_window
            idx2 = len(history) - 1
            
            bbox1 = history[idx1]['bbox']
            bbox2 = history[idx2]['bbox']
            time_delta = history[idx2]['timestamp'] - history[idx1]['timestamp']
            
            speed = calculate_speed(bbox1, bbox2, self.homography_matrix, time_delta)
            
            # Filtrar velocidades muy bajas o erróneas
            if speed < 0 or speed > 200:  # Velocidad máxima razonable
                return None
            
            return speed
        
        return None
    
    def get_average_speed(self, track_id: int) -> Optional[float]:
        """Obtener velocidad promedio de un track"""
        if track_id not in self.track_histories:
            return None
        
        history = self.track_histories[track_id]
        if len(history) < 2:
            return None
        
        speeds = []
        for i in range(1, len(history)):
            bbox1 = history[i-1]['bbox']
            bbox2 = history[i]['bbox']
            time_delta = history[i]['timestamp'] - history[i-1]['timestamp']
            
            if time_delta > 0:
                speed = calculate_speed(bbox1, bbox2, self.homography_matrix, time_delta)
                if 0 < speed < 200:
                    speeds.append(speed)
        
        if len(speeds) > 0:
            return np.mean(speeds)
        
        return None
    
    def remove_track(self, track_id: int):
        """Eliminar historial de un track"""
        if track_id in self.track_histories:
            del self.track_histories[track_id]

