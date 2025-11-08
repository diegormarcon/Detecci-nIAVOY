#!/usr/bin/env python3
"""
Script para iniciar el sistema completo en desarrollo local
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print("Verificando dependencias...")
    
    # Verificar Python
    if sys.version_info < (3, 9):
        print("❌ Se requiere Python 3.9 o superior")
        return False
    
    # Verificar PostgreSQL (opcional, puede usar Docker)
    try:
        import psycopg2
        print("✅ psycopg2 instalado")
    except ImportError:
        print("⚠️  psycopg2 no instalado (se usará Docker para PostgreSQL)")
    
    return True

def start_backend():
    """Iniciar el backend FastAPI"""
    print("\n🚀 Iniciando Backend...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Verificar si existe venv
    venv_python = backend_dir / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
    
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    # Inicializar base de datos si es necesario
    print("Inicializando base de datos...")
    subprocess.run([python_cmd, "init_db.py"], cwd=backend_dir, check=False)
    
    # Iniciar servidor
    print("Iniciando servidor FastAPI en http://localhost:8000")
    return subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_frontend():
    """Iniciar el frontend React"""
    print("\n🚀 Iniciando Frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Verificar node_modules
    if not (frontend_dir / "node_modules").exists():
        print("Instalando dependencias de Node.js...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    print("Iniciando servidor de desarrollo en http://localhost:3000")
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():
    """Función principal"""
    print("=" * 60)
    print("Sistema de Detección VOI - Inicio Local")
    print("=" * 60)
    
    if not check_dependencies():
        sys.exit(1)
    
    processes = []
    
    try:
        # Iniciar backend
        backend_proc = start_backend()
        processes.append(("Backend", backend_proc))
        time.sleep(3)  # Esperar a que el backend inicie
        
        # Iniciar frontend
        frontend_proc = start_frontend()
        processes.append(("Frontend", frontend_proc))
        
        print("\n" + "=" * 60)
        print("✅ Sistema iniciado correctamente!")
        print("=" * 60)
        print("\nServicios disponibles:")
        print("  📱 Frontend:  http://localhost:3000")
        print("  🔌 Backend:   http://localhost:8000")
        print("  📚 API Docs:  http://localhost:8000/docs")
        print("\nPresiona Ctrl+C para detener todos los servicios")
        print("=" * 60 + "\n")
        
        # Esperar hasta que se presione Ctrl+C
        while True:
            time.sleep(1)
            # Verificar que los procesos sigan corriendo
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  {name} se detuvo inesperadamente")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servicios...")
        for name, proc in processes:
            print(f"  Deteniendo {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("✅ Todos los servicios detenidos")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for name, proc in processes:
            proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()

