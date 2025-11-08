#!/bin/bash
# Script para iniciar el servidor web completo usando Docker

echo "=========================================="
echo "🌐 Sistema de Detección VOI"
echo "=========================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    echo "   Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "🐳 Iniciando servicios con Docker Compose..."
echo ""
echo "Esto iniciará:"
echo "  ✅ Backend API en http://localhost:8005"
echo "  ✅ Frontend UI en http://localhost:3000"
echo "  ✅ PostgreSQL"
echo "  ✅ Redis"
echo ""
echo "Presiona Ctrl+C para detener"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
docker-compose up --build

