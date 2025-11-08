# Ejemplo de uso de la API

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8005"

# Crear una cámara
def create_camera():
    camera_data = {
        "name": "Cámara de Prueba",
        "location": "Calle Principal 123",
        "latitude": -34.6037,
        "longitude": -58.3816,
        "rtsp_url": "rtsp://example.com/stream",
        "is_active": True,
        "speed_limit": 50.0
    }
    
    response = requests.post(f"{API_URL}/api/cameras/", json=camera_data)
    print(f"Crear cámara: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    return None

# Calibrar una cámara
def calibrate_camera(camera_id):
    calibration_data = {
        "pixel_points": [
            [100, 200],
            [500, 200],
            [500, 400],
            [100, 400]
        ],
        "real_points": [
            [0, 0],
            [10, 0],
            [10, 5],
            [0, 5]
        ]
    }
    
    response = requests.post(
        f"{API_URL}/api/cameras/{camera_id}/calibrate",
        json=calibration_data
    )
    print(f"Calibrar cámara: {response.status_code}")
    return response.json()

# Crear un incidente
def create_incident(camera_id):
    incident_data = {
        "camera_id": camera_id,
        "incident_type": "speed",
        "detected_class": "car",
        "track_id": 1,
        "speed_kmh": 65.5,
        "speed_limit": 50.0,
        "bbox": [100, 200, 300, 400],
        "confidence": 0.85,
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(f"{API_URL}/api/incidents/", json=incident_data)
    print(f"Crear incidente: {response.status_code}")
    return response.json()

# Listar incidentes
def list_incidents():
    response = requests.get(f"{API_URL}/api/incidents/")
    incidents = response.json()
    print(f"Total de incidentes: {len(incidents)}")
    return incidents

if __name__ == "__main__":
    print("Ejemplos de uso de la API")
    print("=" * 50)
    
    # Crear cámara
    camera = create_camera()
    if camera:
        camera_id = camera["id"]
        
        # Calibrar cámara
        calibrate_camera(camera_id)
        
        # Crear incidente
        create_incident(camera_id)
    
    # Listar incidentes
    list_incidents()

