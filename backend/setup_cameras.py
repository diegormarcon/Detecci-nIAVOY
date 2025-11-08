import requests
import json
from datetime import datetime

API_URL = "http://localhost:8005"

def create_external_camera():
    """Crear una cámara externa de ejemplo"""
    
    print("Creando cámara externa...")
    print("\nTipos de cámaras soportadas:")
    print("1. RTSP: rtsp://usuario:password@ip:puerto/stream")
    print("2. HTTP: http://ip:puerto/video")
    print("3. USB: número de dispositivo (0, 1, 2...)")
    print("4. Archivo: ruta al archivo de video")
    
    print("\nEjemplo de configuración:")
    
    # Ejemplo 1: Cámara RTSP
    camera_rtsp = {
        "name": "Cámara Externa RTSP",
        "location": "Entrada Principal",
        "latitude": -34.6037,
        "longitude": -58.3816,
        "rtsp_url": "rtsp://admin:password123@192.168.1.100:554/stream1",
        "is_active": True,
        "speed_limit": 50.0
    }
    
    # Ejemplo 2: Cámara HTTP
    camera_http = {
        "name": "Cámara Externa HTTP",
        "location": "Calle Secundaria",
        "latitude": -34.6040,
        "longitude": -58.3820,
        "web_url": "http://192.168.1.101:8080/video",
        "is_active": True,
        "speed_limit": 40.0
    }
    
    # Ejemplo 3: Cámara USB local
    camera_usb = {
        "name": "Cámara USB Local",
        "location": "Oficina",
        "latitude": -34.6035,
        "longitude": -58.3815,
        "rtsp_url": None,  # Se usará el número de dispositivo directamente
        "is_active": True,
        "speed_limit": 30.0
    }
    
    try:
        # Crear cámara RTSP de ejemplo
        response = requests.post(f"{API_URL}/api/cameras/", json=camera_rtsp)
        if response.status_code == 200:
            cam = response.json()
            print(f"\n✅ Cámara RTSP creada: ID {cam['id']} - {cam['name']}")
            print(f"   URL: {cam.get('rtsp_url', 'N/A')}")
        
        # Crear cámara HTTP de ejemplo
        response = requests.post(f"{API_URL}/api/cameras/", json=camera_http)
        if response.status_code == 200:
            cam = response.json()
            print(f"✅ Cámara HTTP creada: ID {cam['id']} - {cam['name']}")
            print(f"   URL: {cam.get('web_url', 'N/A')}")
        
        # Crear cámara USB de ejemplo
        response = requests.post(f"{API_URL}/api/cameras/", json=camera_usb)
        if response.status_code == 200:
            cam = response.json()
            print(f"✅ Cámara USB creada: ID {cam['id']} - {cam['name']}")
        
        print("\n" + "="*60)
        print("Para usar estas cámaras con el detector:")
        print("="*60)
        print("\nCámara RTSP:")
        print(f"  python detector/main.py --source rtsp://admin:password123@192.168.1.100:554/stream1 --camera-id {camera_rtsp.get('id', 1)} --display")
        print("\nCámara HTTP:")
        print(f"  python detector/main.py --source http://192.168.1.101:8080/video --camera-id {camera_http.get('id', 2)} --display")
        print("\nCámara USB (dispositivo 0):")
        print(f"  python detector/main.py --source 0 --camera-id {camera_usb.get('id', 3)} --display")
        print("\n" + "="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al backend")
        print("   Asegúrate de que el backend esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_cameras():
    """Listar todas las cámaras"""
    try:
        response = requests.get(f"{API_URL}/api/cameras/")
        cameras = response.json()
        
        print(f"\n📹 Cámaras registradas ({len(cameras)}):")
        print("="*60)
        for cam in cameras:
            print(f"\nID: {cam['id']} - {cam['name']}")
            print(f"  Ubicación: {cam.get('location', 'N/A')}")
            print(f"  Estado: {'✅ Activa' if cam.get('is_active') else '❌ Inactiva'}")
            if cam.get('rtsp_url'):
                print(f"  RTSP: {cam['rtsp_url']}")
            if cam.get('web_url'):
                print(f"  HTTP: {cam['web_url']}")
            if cam.get('speed_limit'):
                print(f"  Límite velocidad: {cam['speed_limit']} km/h")
            if cam.get('calibration_matrix'):
                print(f"  Calibración: ✅ Configurada")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("Configuración de Cámaras Externas")
    print("="*60)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_cameras()
    else:
        create_external_camera()
        print("\n")
        list_cameras()

