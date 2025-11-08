import cv2
import argparse
import logging
import time
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
import os
import requests

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detection.yolo_detector import YOLODetector
from detector.tracking.byte_tracker import ByteTracker
from detector.speed.speed_calculator import SpeedCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CameraStream:
    """Manejador de streams de cámaras externas"""
    
    @staticmethod
    def open_stream(source: str, timeout: int = 5, max_retries: int = 3):
        """
        Abrir stream de video con soporte para múltiples protocolos
        
        Args:
            source: Fuente de video (RTSP, HTTP, archivo, número de cámara)
            timeout: Timeout en segundos
            max_retries: Número máximo de reintentos
            
        Returns:
            cv2.VideoCapture object o None si falla
        """
        cap = None
        
        # Detectar tipo de fuente
        if source.isdigit():
            # Cámara USB local
            logger.info(f"Abriendo cámara USB: {source}")
            cap = cv2.VideoCapture(int(source))
        elif source.startswith('rtsp://'):
            # Stream RTSP
            logger.info(f"Abriendo stream RTSP: {source}")
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            # Configurar buffer pequeño para RTSP
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        elif source.startswith('http://') or source.startswith('https://'):
            # Stream HTTP/HTTPS
            logger.info(f"Abriendo stream HTTP: {source}")
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        elif source.startswith('/dev/video'):
            # Dispositivo de video Linux
            logger.info(f"Abriendo dispositivo de video: {source}")
            cap = cv2.VideoCapture(source)
        else:
            # Archivo de video
            logger.info(f"Abriendo archivo de video: {source}")
            cap = cv2.VideoCapture(source)
        
        # Intentar abrir con reintentos
        for attempt in range(max_retries):
            if cap is not None and cap.isOpened():
                # Verificar que realmente puede leer frames
                ret, frame = cap.read()
                if ret and frame is not None:
                    logger.info(f"Stream abierto exitosamente en intento {attempt + 1}")
                    cap.set(cv2.CAP_PROP_FPS, 30)  # Intentar establecer FPS
                    return cap
                else:
                    logger.warning(f"Stream abierto pero no puede leer frames, reintentando...")
                    cap.release()
            
            if attempt < max_retries - 1:
                logger.info(f"Reintentando conexión ({attempt + 1}/{max_retries})...")
                time.sleep(2)
                # Recrear captura
                if source.startswith('rtsp://') or source.startswith('http://') or source.startswith('https://'):
                    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                elif source.isdigit():
                    cap = cv2.VideoCapture(int(source))
                else:
                    cap = cv2.VideoCapture(source)
        
        logger.error(f"No se pudo abrir la fuente después de {max_retries} intentos")
        return None


class VideoProcessor:
    """Procesador de video con detección, tracking y cálculo de velocidad"""
    
    def __init__(self, camera_id: int, api_url: str = "http://localhost:8005",
                 model_path: str = "yolov8n.pt", homography_matrix=None, speed_limit=None):
        self.camera_id = camera_id
        self.api_url = api_url
        self.detector = YOLODetector(model_path=model_path)
        self.tracker = ByteTracker()
        self.speed_calculator = SpeedCalculator(homography_matrix=homography_matrix)
        self.speed_limit = speed_limit or 50.0
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        
        # Cargar información de la cámara desde el backend
        self._load_camera_info()
        
        logger.info(f"VideoProcessor inicializado para cámara {camera_id}")
    
    def _load_camera_info(self):
        """Cargar información de la cámara desde el backend"""
        try:
            response = requests.get(f"{self.api_url}/api/cameras/{self.camera_id}", timeout=5)
            if response.status_code == 200:
                camera_data = response.json()
                if camera_data.get('calibration_matrix'):
                    matrix = np.array(camera_data['calibration_matrix'])
                    self.speed_calculator.update_homography(matrix)
                    logger.info("Matriz de homografía cargada desde el backend")
                if camera_data.get('speed_limit'):
                    self.speed_limit = camera_data['speed_limit']
                    logger.info(f"Límite de velocidad cargado: {self.speed_limit} km/h")
        except Exception as e:
            logger.warning(f"No se pudo cargar información de la cámara: {e}")
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Procesar un frame: detectar, trackear y calcular velocidad
        
        Args:
            frame: Frame de video (BGR)
            
        Returns:
            Frame anotado con detecciones y velocidades
        """
        self.frame_count += 1
        timestamp = time.time()
        
        # Detectar objetos
        detections = self.detector.detect(frame)
        
        # Trackear objetos
        tracks = self.tracker.update(detections)
        
        # Calcular velocidad y dibujar resultados
        annotated_frame = frame.copy()
        incidents = []
        
        for track in tracks:
            track_id = track['track_id']
            bbox = track['bbox']
            class_name = track['class_name']
            confidence = track['confidence']
            
            # Calcular velocidad
            speed_kmh = self.speed_calculator.calculate_track_speed(
                track_id, bbox, timestamp
            )
            
            # Dibujar bbox
            x1, y1, x2, y2 = map(int, bbox)
            color = self._get_color_for_class(class_name)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Etiqueta con ID y velocidad
            label = f"ID:{track_id} {class_name}"
            if speed_kmh is not None:
                label += f" {speed_kmh:.1f} km/h"
                # Resaltar si excede límite
                if speed_kmh > self.speed_limit * 1.1:
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            cv2.putText(annotated_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Verificar infracciones
            incident = self._check_incidents(track, speed_kmh)
            if incident:
                incidents.append(incident)
        
        # Enviar incidentes al backend
        if incidents:
            self._send_incidents(incidents)
        
        # Enviar frame procesado al backend para visualización
        self._send_frame_to_backend(annotated_frame)
        
        # Calcular FPS
        if self.frame_count % 30 == 0:
            current_time = time.time()
            self.fps = 30 / (current_time - self.last_fps_time)
            self.last_fps_time = current_time
        
        # Mostrar FPS y límite de velocidad
        cv2.putText(annotated_frame, f"FPS: {self.fps:.1f} | Limite: {self.speed_limit} km/h", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return annotated_frame
    
    def _get_color_for_class(self, class_name: str) -> tuple:
        """Obtener color para una clase"""
        colors = {
            'car': (0, 255, 0),      # Verde
            'motorcycle': (255, 0, 0),  # Azul
            'bus': (0, 0, 255),      # Rojo
            'truck': (255, 165, 0),  # Naranja
            'person': (255, 0, 255)  # Magenta
        }
        return colors.get(class_name, (255, 255, 255))
    
    def _check_incidents(self, track: dict, speed_kmh: float) -> dict:
        """
        Verificar si hay infracciones
        
        Args:
            track: Información del track
            speed_kmh: Velocidad calculada
            
        Returns:
            Diccionario con información del incidente o None
        """
        incident = None
        
        # Verificar velocidad con tolerancia del 10%
        if speed_kmh and speed_kmh > self.speed_limit * 1.1:
            incident = {
                'camera_id': self.camera_id,
                'incident_type': 'speed',
                'detected_class': track['class_name'],
                'track_id': track['track_id'],
                'speed_kmh': speed_kmh,
                'speed_limit': self.speed_limit,
                'bbox': track['bbox'],
                'confidence': track['confidence'],
                'timestamp': datetime.now().isoformat(),
                'extra_data': {
                    'hits': track['hits'],
                    'age': track['age']
                }
            }
        
        return incident
    
    def _send_incidents(self, incidents: list):
        """Enviar incidentes al backend API"""
        try:
            url = f"{self.api_url}/api/incidents/"
            for incident in incidents:
                response = requests.post(url, json=incident, timeout=2)
                if response.status_code == 200:
                    logger.info(f"Incidente enviado: {incident['incident_type']} - Track {incident['track_id']} - {incident['speed_kmh']:.1f} km/h")
                else:
                    logger.warning(f"Error enviando incidente: {response.status_code}")
        except Exception as e:
            logger.error(f"Error enviando incidentes al backend: {e}")
    
    def _send_frame_to_backend(self, frame: np.ndarray):
        """Enviar frame procesado al backend para visualización en el navegador"""
        try:
            # Redimensionar frame para reducir tamaño (opcional, para eficiencia)
            height, width = frame.shape[:2]
            if width > 1280:
                scale = 1280 / width
                new_width = 1280
                new_height = int(height * scale)
                frame_resized = cv2.resize(frame, (new_width, new_height))
            else:
                frame_resized = frame
            
            # Enviar frame al backend
            url = f"{self.api_url}/api/camera-detection/update-frame/{self.camera_id}"
            # Convertir frame a JPEG
            _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
            files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
            
            requests.post(url, files=files, timeout=0.1)  # Timeout corto para no bloquear
        except Exception as e:
            # No es crítico si falla, solo logging ocasional
            pass  # Silenciar errores de envío de frame para no saturar logs


def main():
    parser = argparse.ArgumentParser(
        description='Procesador de video con detección y tracking - Soporta RTSP, HTTP, archivos y cámaras USB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Cámara USB local
  python main.py --source 0 --camera-id 1 --display
  
  # Stream RTSP
  python main.py --source rtsp://user:pass@192.168.1.100:554/stream --camera-id 1 --display
  
  # Stream HTTP
  python main.py --source http://192.168.1.100:8080/video --camera-id 1 --display
  
  # Archivo de video
  python main.py --source video.mp4 --camera-id 1 --display
  
  # Sin display (solo procesamiento)
  python main.py --source rtsp://camera-url --camera-id 1
        """
    )
    parser.add_argument('--source', type=str, required=True,
                       help='Fuente de video: número de cámara (0,1,2...), RTSP (rtsp://...), HTTP (http://...), o archivo')
    parser.add_argument('--camera-id', type=int, required=True,
                       help='ID de la cámara en el sistema')
    parser.add_argument('--api-url', type=str, default='http://localhost:8005',
                       help='URL del backend API')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Ruta al modelo YOLO')
    parser.add_argument('--output', type=str, default=None,
                       help='Ruta para guardar video procesado (opcional)')
    parser.add_argument('--display', action='store_true',
                       help='Mostrar video en ventana')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='Número máximo de reintentos para conectar')
    
    args = parser.parse_args()
    
    # Inicializar procesador
    processor = VideoProcessor(
        camera_id=args.camera_id,
        api_url=args.api_url,
        model_path=args.model
    )
    
    # Abrir fuente de video con soporte mejorado
    cap = CameraStream.open_stream(args.source, max_retries=args.max_retries)
    
    if cap is None:
        logger.error(f"No se pudo abrir la fuente de video: {args.source}")
        logger.error("Verifica que:")
        logger.error("  - La URL RTSP/HTTP sea correcta")
        logger.error("  - La cámara USB esté conectada")
        logger.error("  - El archivo de video exista")
        return
    
    # Obtener propiedades del video
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video: {width}x{height} @ {fps} FPS")
    
    # Configurar escritor de video si es necesario
    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        logger.info(f"Guardando video en: {args.output}")
    
    logger.info("Iniciando procesamiento de video...")
    logger.info("Presiona 'q' para salir (si --display está activado)")
    
    frame_skip = max(1, fps // 10)  # Procesar ~10 FPS para eficiencia
    frame_idx = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("No se pudo leer frame, reintentando...")
                time.sleep(0.1)
                continue
            
            frame_idx += 1
            
            # Procesar cada N frames para eficiencia
            if frame_idx % frame_skip == 0:
                # Procesar frame
                annotated_frame = processor.process_frame(frame)
                
                # Guardar si es necesario
                if writer:
                    writer.write(annotated_frame)
                
                # Mostrar si es necesario
                if args.display:
                    cv2.imshow('Video Processor - Presiona Q para salir', annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    
    except KeyboardInterrupt:
        logger.info("Procesamiento interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}", exc_info=True)
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        logger.info("Procesamiento finalizado")


if __name__ == "__main__":
    main()
