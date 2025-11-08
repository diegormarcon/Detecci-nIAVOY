# Script de ejemplo para probar el detector localmente

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detection.yolo_detector import YOLODetector
from detector.tracking.byte_tracker import ByteTracker
from detector.speed.speed_calculator import SpeedCalculator
import cv2
import numpy as np

def main():
    # Inicializar componentes
    detector = YOLODetector(model_path="yolov8n.pt")
    tracker = ByteTracker()
    speed_calc = SpeedCalculator()
    
    # Abrir video de prueba
    cap = cv2.VideoCapture(0)  # Cámara 0, o cambiar a ruta de video
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara/video")
        return
    
    print("Presiona 'q' para salir")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detectar
        detections = detector.detect(frame)
        
        # Trackear
        tracks = tracker.update(detections)
        
        # Dibujar resultados
        for track in tracks:
            x1, y1, x2, y2 = map(int, track['bbox'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"ID:{track['track_id']} {track['class_name']}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow('Detector', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

