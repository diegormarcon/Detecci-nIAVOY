#!/usr/bin/env python3
"""
Script mejorado para iniciar todos los servicios
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
import socket

def check_port(port):
    """Verificar si un puerto está en uso"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_backend():
    """Iniciar el backend FastAPI"""
    print("🚀 Iniciando Backend...")
    backend_dir = Path(__file__).parent / "backend"
    
    if check_port(8005):
        print("   ⚠️  Puerto 8005 ya en uso - Backend puede estar corriendo")
        return None
    
    venv_python = backend_dir / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
    
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    print("   ✅ Backend: http://localhost:8005")
    return subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"],
        cwd=backend_dir
    )

def start_frontend():
    """Iniciar el frontend React"""
    print("🚀 Iniciando Frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    if check_port(3000):
        print("   ⚠️  Puerto 3000 ya en uso - Frontend puede estar corriendo")
        return None
    
    # Usar npx directamente si npm tiene problemas
    node_path = "/Users/diego/nodejs/bin/node"
    npx_path = "/Users/diego/nodejs/bin/npx"
    
    if not os.path.exists(npx_path):
        # Intentar encontrar npx en el sistema
        import shutil
        npx_path = shutil.which("npx") or "npx"
    
    # Verificar node_modules
    if not (frontend_dir / "node_modules").exists():
        print("   📦 Instalando dependencias...")
        subprocess.run([npx_path, "--yes", "npm", "install"], cwd=frontend_dir, check=False)
    
    print("   ✅ Frontend: http://localhost:3000")
    return subprocess.Popen(
        [npx_path, "--yes", "vite", "--host", "--port", "3000"],
        cwd=frontend_dir
    )

def main():
    """Función principal"""
    print("=" * 70)
    print("🌐 Sistema de Detección VOI - Servidor Web Completo")
    print("=" * 70)
    
    processes = []
    
    try:
        # Iniciar backend
        backend_proc = start_backend()
        if backend_proc:
            processes.append(("Backend", backend_proc))
            time.sleep(3)
        
        # Iniciar frontend
        frontend_proc = start_frontend()
        if frontend_proc:
            processes.append(("Frontend", frontend_proc))
            time.sleep(5)
        
        print("\n" + "=" * 70)
        print("✅ SERVIDOR WEB INICIADO CORRECTAMENTE")
        print("=" * 70)
        print("\n📱 Accede a la aplicación:")
        print("   🌐 Frontend:  http://localhost:3000")
        print("   🔌 Backend:   http://localhost:8005")
        print("   📚 API Docs:  http://localhost:8005/docs")
        print("\n💡 Presiona Ctrl+C para detener todos los servicios")
        print("=" * 70 + "\n")
        
        # Esperar hasta Ctrl+C
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc and proc.poll() is not None:
                    print(f"⚠️  {name} se detuvo")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servidores...")
        for name, proc in processes:
            if proc:
                print(f"   Deteniendo {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("✅ Todos los servicios detenidos")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for name, proc in processes:
            if proc:
                proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
