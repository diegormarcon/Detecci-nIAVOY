from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from app.api import incidents, cameras, events, evidence, camera_detection, detection_control
from app.db.database import engine, Base
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Inicializando base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")
    yield
    # Shutdown
    logger.info("Cerrando aplicación...")


app = FastAPI(
    title="Sistema de Detección de Infracciones VOI",
    description="API para detección en tiempo real de vehículos, infracciones y medición de velocidad",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3050", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(camera_detection.router, prefix="/api/camera-detection", tags=["camera-detection"])
app.include_router(detection_control.router, prefix="/api/detection", tags=["detection"])


@app.get("/")
async def root():
    return {
        "message": "Sistema de Detección de Infracciones VOI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

