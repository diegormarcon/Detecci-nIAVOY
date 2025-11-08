import numpy as np
from typing import List, Tuple, Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ByteTracker:
    """Tracker multi-objeto usando algoritmo ByteTrack"""
    
    def __init__(self, min_hits: int = 3, max_age: int = 30, iou_threshold: float = 0.3):
        """
        Inicializar tracker ByteTrack
        
        Args:
            min_hits: Número mínimo de detecciones para confirmar un track
            max_age: Número de frames sin detección antes de eliminar track
            iou_threshold: Umbral IoU para asociar detecciones con tracks
        """
        self.min_hits = min_hits
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        
        self.tracked_tracks: List[Track] = []
        self.lost_tracks: List[Track] = []
        self.removed_tracks: List[Track] = []
        self.frame_count = 0
        self.next_id = 1
        
        logger.info("ByteTracker inicializado")
    
    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Actualizar tracks con nuevas detecciones
        
        Args:
            detections: Lista de detecciones del frame actual
            
        Returns:
            Lista de tracks activos con formato:
            {
                'track_id': int,
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int,
                'class_name': str,
                'age': int,
                'hits': int
            }
        """
        self.frame_count += 1
        
        # Preparar detecciones
        det_boxes = np.array([d['bbox'] for d in detections])
        det_scores = np.array([d['confidence'] for d in detections])
        det_classes = np.array([d['class_id'] for d in detections])
        
        # Inicializar unmatched_dets para el caso cuando no hay tracks existentes
        unmatched_dets = list(range(len(detections)))
        
        # Actualizar tracks existentes
        if len(self.tracked_tracks) > 0:
            tracked_boxes = np.array([t.bbox for t in self.tracked_tracks])
            iou_matrix = self._compute_iou(det_boxes, tracked_boxes)
            
            # Asociar detecciones con tracks existentes
            matched, unmatched_dets, unmatched_trks = self._associate_detections_to_trackers(
                iou_matrix, det_boxes, tracked_boxes
            )
            
            # Actualizar tracks emparejados
            for m in matched:
                det_idx, trk_idx = m
                self.tracked_tracks[trk_idx].update(detections[det_idx])
            
            # Tracks no emparejados -> lost
            for trk_idx in unmatched_trks:
                self.tracked_tracks[trk_idx].mark_lost()
                self.lost_tracks.append(self.tracked_tracks[trk_idx])
            
            self.tracked_tracks = [t for t in self.tracked_tracks if t.state == 'tracked']
        
        # Procesar detecciones no emparejadas
        unmatched_detections = [detections[i] for i in unmatched_dets] if len(detections) > 0 and len(unmatched_dets) > 0 else []
        
        # Intentar asociar con tracks perdidos
        if len(self.lost_tracks) > 0 and len(unmatched_detections) > 0:
            lost_boxes = np.array([t.bbox for t in self.lost_tracks])
            det_boxes_unmatched = np.array([d['bbox'] for d in unmatched_detections])
            iou_matrix = self._compute_iou(det_boxes_unmatched, lost_boxes)
            
            matched_lost, unmatched_dets_lost, unmatched_lost = self._associate_detections_to_trackers(
                iou_matrix, det_boxes_unmatched, lost_boxes
            )
            
            # Reactivar tracks perdidos
            for m in matched_lost:
                det_idx, lost_idx = m
                self.lost_tracks[lost_idx].update(unmatched_detections[det_idx])
                self.tracked_tracks.append(self.lost_tracks[lost_idx])
            
            self.lost_tracks = [t for t in self.lost_tracks if t not in self.tracked_tracks]
            
            # Actualizar unmatched_detections con las que no se emparejaron
            unmatched_detections = [unmatched_detections[i] for i in unmatched_dets_lost]
        
        # Crear nuevos tracks para detecciones no emparejadas
        for det in unmatched_detections:
            if det['confidence'] > 0.5:  # Solo tracks de alta confianza
                new_track = Track(self.next_id, det, self.frame_count)
                self.tracked_tracks.append(new_track)
                self.next_id += 1
        
        # Eliminar tracks antiguos
        self.tracked_tracks = [t for t in self.tracked_tracks if t.age < self.max_age]
        self.lost_tracks = [t for t in self.lost_tracks if t.age < self.max_age]
        
        # Retornar tracks activos
        active_tracks = []
        for track in self.tracked_tracks:
            if track.hits >= self.min_hits:
                active_tracks.append({
                    'track_id': track.track_id,
                    'bbox': track.bbox,
                    'confidence': track.confidence,
                    'class_id': track.class_id,
                    'class_name': track.class_name,
                    'age': track.age,
                    'hits': track.hits,
                    'history': track.history[-10:]  # Últimas 10 posiciones
                })
        
        return active_tracks
    
    def _compute_iou(self, boxes1: np.ndarray, boxes2: np.ndarray) -> np.ndarray:
        """Calcular matriz IoU entre dos conjuntos de boxes"""
        if len(boxes1) == 0 or len(boxes2) == 0:
            return np.zeros((len(boxes1), len(boxes2)))
        
        # Calcular intersección
        x1_max = np.maximum(boxes1[:, 0][:, np.newaxis], boxes2[:, 0])
        y1_max = np.maximum(boxes1[:, 1][:, np.newaxis], boxes2[:, 1])
        x2_min = np.minimum(boxes1[:, 2][:, np.newaxis], boxes2[:, 2])
        y2_min = np.minimum(boxes1[:, 3][:, np.newaxis], boxes2[:, 3])
        
        intersection = np.maximum(0, x2_min - x1_max) * np.maximum(0, y2_min - y1_max)
        
        # Calcular áreas
        area1 = (boxes1[:, 2] - boxes1[:, 0]) * (boxes1[:, 3] - boxes1[:, 1])
        area2 = (boxes2[:, 2] - boxes2[:, 0]) * (boxes2[:, 3] - boxes2[:, 1])
        
        # Calcular IoU
        union = area1[:, np.newaxis] + area2 - intersection
        iou = intersection / np.maximum(union, 1e-8)
        
        return iou
    
    def _associate_detections_to_trackers(self, iou_matrix: np.ndarray, 
                                         detections: np.ndarray, 
                                         trackers: np.ndarray) -> Tuple[List, List, List]:
        """Asociar detecciones con trackers usando IoU"""
        if iou_matrix.size == 0:
            return [], list(range(len(detections))), list(range(len(trackers)))
        
        # Greedy matching
        matched_indices = []
        unmatched_dets = list(range(len(detections)))
        unmatched_trks = list(range(len(trackers)))
        
        # Ordenar por IoU descendente
        if iou_matrix.size > 0:
            iou_pairs = []
            for i in range(len(detections)):
                for j in range(len(trackers)):
                    if iou_matrix[i, j] > self.iou_threshold:
                        iou_pairs.append((iou_matrix[i, j], i, j))
            
            iou_pairs.sort(reverse=True)
            
            for iou_val, det_idx, trk_idx in iou_pairs:
                if det_idx in unmatched_dets and trk_idx in unmatched_trks:
                    matched_indices.append((det_idx, trk_idx))
                    unmatched_dets.remove(det_idx)
                    unmatched_trks.remove(trk_idx)
        
        return matched_indices, unmatched_dets, unmatched_trks


class Track:
    """Representa un track individual"""
    
    def __init__(self, track_id: int, detection: Dict[str, Any], frame_id: int):
        self.track_id = track_id
        self.bbox = detection['bbox']
        self.confidence = detection['confidence']
        self.class_id = detection['class_id']
        self.class_name = detection['class_name']
        self.state = 'tracked'
        self.hits = 1
        self.age = 0
        self.time_since_update = 0
        self.history = [detection['bbox']]
        self.first_seen = frame_id
    
    def update(self, detection: Dict[str, Any]):
        """Actualizar track con nueva detección"""
        self.bbox = detection['bbox']
        self.confidence = detection['confidence']
        self.class_id = detection['class_id']
        self.class_name = detection['class_name']
        self.state = 'tracked'
        self.hits += 1
        self.time_since_update = 0
        self.history.append(detection['bbox'])
        if len(self.history) > 30:
            self.history.pop(0)
    
    def mark_lost(self):
        """Marcar track como perdido"""
        self.state = 'lost'
        self.time_since_update += 1
        self.age += 1

