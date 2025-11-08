# Sistema de Detección de Infracciones de Tráfico con IA

Sistema completo para detección en tiempo real de vehículos, motos, cascos, matrículas, ocupación y medición de velocidad en video.

## 🎯 Características Principales

- ✅ Detección en tiempo real: vehículos, motos, cascos, matrículas
- ✅ Tracking multi-objeto con ByteTrack
- ✅ Medición de velocidad por vehículo
- ✅ Detección de ocupación (personas en vehículos)
- ✅ Invasión de zonas
- ✅ Interfaz web moderna con React
- ✅ API REST con FastAPI
- ✅ Almacenamiento de evidencias (frames, clips, metadatos)
- ✅ Búsqueda por acta, fecha, matrícula
- ✅ Optimizado para edge computing (Jetson, Coral, GPU)

## 🏗️ Arquitectura

```
┌─────────────┐
│   Cámaras   │
│  (RTSP/Web) │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Edge Detector  │  ← YOLOv8 + ByteTrack + Speed Calc
│  (Jetson/GPU)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Backend API    │  ← FastAPI + PostgreSQL + Redis
│  (FastAPI)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Frontend      │  ← React + WebSocket + Leaflet
│   (React)       │
└─────────────────┘
```

## 📦 Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional con PostGIS
- **Redis** - Caché y cola de trabajos
- **SQLAlchemy** - ORM
- **Pydantic** - Validación de datos

### Detección y Tracking
- **YOLOv8** (Ultralytics) - Detección de objetos
- **ByteTrack** - Tracking multi-objeto eficiente
- **OpenCV** - Procesamiento de video e imágenes
- **NumPy** - Cálculos matemáticos

### Frontend
- **React** - Framework UI
- **Tailwind CSS** - Estilos modernos
- **WebSocket** - Comunicación en tiempo real
- **Leaflet** - Mapas interactivos

### Infraestructura
- **Docker** - Contenedores
- **Docker Compose** - Orquestación local
- **Nginx** - Proxy reverso (producción)

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose instalados
- Python 3.9+ (para desarrollo local)
- CUDA (opcional, para GPU)

### Instalación

1. **Clonar el repositorio**
```bash
cd "Deteccion IA VOI"
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Construir y ejecutar con Docker Compose**
```bash
docker-compose up --build
```

4. **Acceder a la aplicación**
- Frontend: http://localhost:3050
- Backend API: http://localhost:8005
- API Docs: http://localhost:8005/docs

### Desarrollo Local

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Detector (procesamiento de video)
```bash
cd detector
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --source video.mp4 --camera-id 1
```

## 📁 Estructura del Proyecto

```
.
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── api/         # Endpoints
│   │   ├── models/      # Modelos de DB
│   │   ├── schemas/     # Schemas Pydantic
│   │   ├── services/    # Lógica de negocio
│   │   └── main.py      # Aplicación principal
│   └── requirements.txt
│
├── detector/             # Módulo de detección
│   ├── detection/       # YOLOv8 detector
│   ├── tracking/        # ByteTrack tracker
│   ├── speed/           # Cálculo de velocidad
│   └── main.py          # Pipeline principal
│
├── frontend/            # Aplicación React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas
│   │   └── services/    # Servicios API
│   └── package.json
│
├── docker-compose.yml   # Orquestación de servicios
├── .env.example         # Variables de entorno ejemplo
└── README.md
```

## 🔧 Configuración

### Calibración de Velocidad

Para medir velocidad con precisión, necesitas calibrar la cámara:

1. Identifica 4 puntos conocidos en la escena (marcas en la calzada)
2. Mide las distancias reales entre esos puntos
3. Usa la herramienta de calibración en el frontend o API
4. Guarda la matriz de homografía para esa cámara

Ejemplo de calibración:
```python
from detector.speed.calibration import calibrate_camera

# Puntos en píxeles y sus coordenadas reales en metros
pixel_points = [(100, 200), (500, 200), (500, 400), (100, 400)]
real_points = [(0, 0), (10, 0), (10, 5), (0, 5)]  # metros

homography_matrix = calibrate_camera(pixel_points, real_points)
```

## 📊 API Endpoints Principales

- `POST /api/incidents` - Registrar incidente
- `GET /api/incidents` - Listar incidentes (con filtros)
- `GET /api/cameras` - Listar cámaras
- `POST /api/cameras/{id}/calibrate` - Calibrar cámara
- `GET /api/events/stream` - WebSocket para eventos en tiempo real
- `GET /api/evidence/{id}` - Obtener evidencia (frame/clip)

## 🎯 Próximos Pasos (Roadmap)

### Fase 1 - MVP ✅
- [x] Detector YOLOv8
- [x] Tracker ByteTrack
- [x] Cálculo de velocidad
- [x] API básica
- [x] Frontend básico

### Fase 2 - Robustez
- [ ] OCR de matrículas (EasyOCR/Tesseract)
- [ ] Almacenamiento en S3
- [ ] Reglas configurables por zona
- [ ] Validaciones avanzadas

### Fase 3 - Edge & Escalabilidad
- [ ] Optimización ONNX/TensorRT
- [ ] Despliegue en Jetson
- [ ] Kubernetes para producción
- [ ] Autoescalado

### Fase 4 - Producción
- [ ] Tests de campo
- [ ] Calibraciones por sitio
- [ ] Seguridad y cumplimiento legal
- [ ] CI/CD para modelos

## 📝 Licencia

Este proyecto es privado y confidencial.

## 🤝 Contribución

Para contribuir, por favor crea un issue o pull request.
