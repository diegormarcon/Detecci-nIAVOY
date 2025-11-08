#!/usr/bin/env python3
"""
Script para iniciar detección automática con cámara seleccionada
"""

import sys
import os
import argparse
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.main import main as detector_main
from detector.utils.camera_detector import detect_available_cameras

def main():
    parser = argparse.ArgumentParser(description='Iniciar detección con cámara seleccionada')
    parser.add_argument('--camera-id', type=int, help='ID de la cámara en el sistema')
    parser.add_argument('--api-url', type=str, default='http://localhost:8005',
                       help='URL del backend API')
    parser.add_argument('--auto-select', action='store_true',
                       help='Seleccionar automáticamente la primera cámara disponible')
    parser.add_argument('--display', action='store_true',
                       help='Mostrar video en ventana')
    
    args = parser.parse_args()
    
    # Detectar cámaras disponibles
    print("🔍 Detectando cámaras disponibles...")
    cameras = detect_available_cameras()
    
    if not cameras:
        print("❌ No se detectaron cámaras disponibles")
        print("   Asegúrate de que tu cámara esté conectada")
        return
    
    print(f"✅ Se detectaron {len(cameras)} cámara(s):")
    for i, cam in enumerate(cameras):
        print(f"   {i+1}. {cam['name']} - {cam['source']}")
    
    # Seleccionar cámara
    if args.auto_select or len(cameras) == 1:
        selected = cameras[0]
        print(f"\n✅ Seleccionando automáticamente: {selected['name']}")
    else:
        print("\nSelecciona una cámara:")
        for i, cam in enumerate(cameras):
            print(f"  {i+1}. {cam['name']}")
        
        choice = input("Número de cámara (1-{}): ".format(len(cameras)))
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(cameras):
                selected = cameras[idx]
            else:
                print("Selección inválida, usando la primera cámara")
                selected = cameras[0]
        except:
            print("Selección inválida, usando la primera cámara")
            selected = cameras[0]
    
    # Obtener camera_id del sistema si no se proporcionó
    camera_id = args.camera_id
    if not camera_id:
        # Intentar obtener de la API o usar 1 por defecto
        try:
            response = requests.get(f"{args.api_url}/api/cameras/")
            if response.status_code == 200:
                system_cameras = response.json()
                if system_cameras:
                    camera_id = system_cameras[0]['id']
                else:
                    camera_id = 1
            else:
                camera_id = 1
        except:
            camera_id = 1
    
    print(f"\n🚀 Iniciando detección...")
    print(f"   Cámara: {selected['name']}")
    print(f"   Fuente: {selected['source']}")
    print(f"   Camera ID: {camera_id}")
    print(f"   Presiona Ctrl+C para detener\n")
    
    # Ejecutar detector
    sys.argv = [
        'main.py',
        '--source', selected['source'],
        '--camera-id', str(camera_id),
        '--api-url', args.api_url
    ]
    
    if args.display:
        sys.argv.append('--display')
    
    detector_main()

if __name__ == "__main__":
    main()

