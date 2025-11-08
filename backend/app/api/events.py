from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Gestor de conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nueva conexión WebSocket. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Conexión WebSocket cerrada. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje WebSocket: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para eventos en tiempo real"""
    await manager.connect(websocket)
    try:
        while True:
            # El cliente puede enviar mensajes de suscripción
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    camera_id = message.get("camera_id")
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "camera_id": camera_id,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Función para que otros módulos envíen eventos
async def broadcast_event(event_type: str, camera_id: int, data: Dict[str, Any]):
    """Función helper para enviar eventos a todos los clientes conectados"""
    message = {
        "type": event_type,
        "camera_id": camera_id,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

