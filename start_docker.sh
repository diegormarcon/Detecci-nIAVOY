#!/bin/bash
# Script para iniciar el sistema con Docker Compose

echo "=========================================="
echo "Sistema de Detección VOI"
echo "=========================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "🐳 Iniciando servicios con Docker Compose..."

# Construir e iniciar servicios
docker-compose up --build

echo "✅ Servicios iniciados"
echo ""
echo "Servicios disponibles:"
echo "  📱 Frontend:  http://localhost:3000"
echo "  🔌 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener"

