from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import logging
import sys
import time

logger = logging.getLogger(__name__)

router = APIRouter()

# Procesos de detección activos
active_processes = {}


class StartDetectionRequest(BaseModel):
    camera_id: int
    source: str
    display: bool = True  # Por defecto mostrar video
    model: Optional[str] = None


@router.post("/start")
async def start_detection(request: StartDetectionRequest, background_tasks: BackgroundTasks):
    """
    Iniciar detección con una cámara específica
    """
    if request.camera_id in active_processes:
        existing = active_processes[request.camera_id]
        if existing.poll() is None:
            raise HTTPException(status_code=400, detail="Ya hay un proceso de detección activo para esta cámara")
        else:
            # Proceso terminado, limpiar
            del active_processes[request.camera_id]
    
    # Construir comando
    # Obtener la ruta del archivo actual y navegar al proyecto raíz
    current_file = os.path.abspath(__file__)
    # current_file está en: proyecto/backend/app/api/detection_control.py
    # Necesitamos: proyecto/detector/main.py
    api_dir = os.path.dirname(current_file)  # backend/app/api
    app_dir = os.path.dirname(api_dir)  # backend/app
    backend_dir = os.path.dirname(app_dir)  # backend
    project_root = os.path.dirname(backend_dir)  # proyecto raíz
    detector_path = os.path.join(project_root, "detector", "main.py")
    
    logger.info(f"Buscando detector en: {detector_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(detector_path):
        logger.error(f"Detector no encontrado en: {detector_path}")
        # Intentar ruta alternativa desde el directorio de trabajo
        cwd = os.getcwd()
        # Si estamos en backend/, subir un nivel
        if cwd.endswith('backend'):
            alt_path = os.path.join(os.path.dirname(cwd), "detector", "main.py")
        else:
            alt_path = os.path.join(cwd, "detector", "main.py")
        
        if os.path.exists(alt_path):
            detector_path = alt_path
            logger.info(f"Usando ruta alternativa: {detector_path}")
        else:
            # Último intento: buscar desde el directorio padre del backend
            parent_path = os.path.join(backend_dir, "..", "detector", "main.py")
            parent_path = os.path.abspath(parent_path)
            if os.path.exists(parent_path):
                detector_path = parent_path
                logger.info(f"Usando ruta del directorio padre: {detector_path}")
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Detector no encontrado. Buscado en: {detector_path}, {alt_path}, {parent_path}. Verifica que detector/main.py exista en el proyecto raíz."
                )
    
    logger.info(f"Detector encontrado en: {detector_path}")
    
    # Determinar el ejecutable de Python
    python_exe = sys.executable
    
    # Cambiar al directorio raíz del proyecto para que los imports funcionen
    project_root = os.path.dirname(backend_dir)
    
    cmd = [
        python_exe,
        detector_path,
        "--source", request.source,
        "--camera-id", str(request.camera_id),
        "--api-url", "http://localhost:8005"
    ]
    
    if request.display:
        cmd.append("--display")
    
    if request.model:
        cmd.extend(["--model", request.model])
    
    try:
        # Iniciar proceso en background
        # IMPORTANTE: Ejecutar desde el directorio raíz del proyecto para que los imports funcionen
        # En macOS, cv2.imshow necesita acceso a la pantalla
        # Usar archivo de log para capturar errores sin bloquear el proceso
        import tempfile
        log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log')
        log_file.close()
        
        if sys.platform != 'win32':
            # En macOS/Linux, redirigir a archivo de log
            with open(log_file.name, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,  # Escribir a archivo de log
                    stderr=subprocess.STDOUT,  # Redirigir stderr también
                    cwd=project_root,  # Ejecutar desde el proyecto raíz
                    start_new_session=True,  # Nueva sesión
                    env=dict(os.environ, DISPLAY=os.environ.get('DISPLAY', ':0'))  # Asegurar DISPLAY para cv2.imshow
                )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        
        active_processes[request.camera_id] = process
        
        logger.info(f"Detección iniciada para cámara {request.camera_id} con PID {process.pid}")
        logger.info(f"Comando ejecutado: {' '.join(cmd)}")
        logger.info(f"Directorio de trabajo: {project_root}")
        logger.info(f"Log file: {log_file.name}")
        
        # Esperar un momento para verificar que el proceso no crashee inmediatamente
        time.sleep(2)
        if process.poll() is not None:
            # Proceso terminó inmediatamente, leer el log
            error_msg = f"El detector se detuvo inmediatamente (código de salida: {process.returncode})"
            logger.error(error_msg)
            try:
                with open(log_file.name, 'r') as f:
                    log_content = f.read()
                    if log_content:
                        logger.error(f"Log del detector: {log_content[-1000:]}")
                        error_msg += f"\nÚltimos logs: {log_content[-500:]}"
            except Exception as e:
                logger.error(f"Error leyendo log: {e}")
            finally:
                try:
                    os.unlink(log_file.name)
                except:
                    pass
            del active_processes[request.camera_id]
            raise HTTPException(status_code=500, detail=error_msg + ". Revisa los logs del backend para más detalles.")
        
        return {
            "status": "started",
            "camera_id": request.camera_id,
            "source": request.source,
            "process_id": process.pid,
            "display": request.display,
            "message": "Detección iniciada. Si --display está activado, deberías ver una ventana con el video.",
            "log_file": log_file.name
        }
    except Exception as e:
        logger.error(f"Error iniciando detección: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al iniciar detección: {str(e)}")


@router.post("/stop/{camera_id}")
async def stop_detection(camera_id: int):
    """
    Detener detección para una cámara
    """
    if camera_id not in active_processes:
        raise HTTPException(status_code=404, detail="No hay proceso de detección activo para esta cámara")
    
    process = active_processes[camera_id]
    
    # Verificar si el proceso aún está corriendo
    if process.poll() is not None:
        # Proceso ya terminó
        del active_processes[camera_id]
        return {
            "status": "stopped",
            "camera_id": camera_id,
            "message": "El proceso ya había terminado"
        }
    
    try:
        # Terminar proceso
        if sys.platform != 'win32':
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        else:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        del active_processes[camera_id]
        
        logger.info(f"Detección detenida para cámara {camera_id}")
        
        return {
            "status": "stopped",
            "camera_id": camera_id
        }
    except Exception as e:
        logger.error(f"Error deteniendo detección: {e}")
        raise HTTPException(status_code=500, detail=f"Error al detener detección: {str(e)}")


@router.get("/status")
async def get_detection_status():
    """
    Obtener estado de todos los procesos de detección
    """
    # Limpiar procesos terminados
    finished = []
    for camera_id, process in active_processes.items():
        if process.poll() is not None:
            finished.append(camera_id)
    
    for camera_id in finished:
        del active_processes[camera_id]
    
    statuses = []
    for camera_id, process in active_processes.items():
        statuses.append({
            "camera_id": camera_id,
            "pid": process.pid,
            "running": process.poll() is None
        })
    
    return {
        "active_detections": len(active_processes),
        "processes": statuses
    }

