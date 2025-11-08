import cv2
import sys
import os

def detect_available_cameras(max_cameras=10):
    """
    Detectar cámaras disponibles en el sistema
    
    Returns:
        Lista de diccionarios con información de cámaras disponibles
    """
    available_cameras = []
    
    # Probar cámaras desde 0 hasta max_cameras
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Intentar leer un frame para verificar que funciona
            ret, frame = cap.read()
            if ret and frame is not None:
                # Obtener propiedades de la cámara
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                
                available_cameras.append({
                    'id': i,
                    'name': f'Cámara {i}',
                    'source': str(i),
                    'type': 'usb',
                    'resolution': f'{width}x{height}',
                    'fps': fps,
                    'available': True
                })
            cap.release()
    
    # También verificar dispositivos de video en Linux/Mac
    if sys.platform != 'win32':
        video_devices = []
        for i in range(max_cameras):
            device_path = f'/dev/video{i}'
            if os.path.exists(device_path):
                cap = cv2.VideoCapture(device_path)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        video_devices.append({
                            'id': f'video{i}',
                            'name': f'Dispositivo Video {i}',
                            'source': device_path,
                            'type': 'device',
                            'available': True
                        })
                    cap.release()
        
        available_cameras.extend(video_devices)
    
    return available_cameras

if __name__ == "__main__":
    cameras = detect_available_cameras()
    print(f"Cámaras detectadas: {len(cameras)}")
    for cam in cameras:
        print(f"  - {cam['name']}: {cam['source']}")

