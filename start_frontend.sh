#!/bin/bash
# Script para iniciar el frontend cuando npm tiene problemas

cd "$(dirname "$0")/frontend"

echo "🚀 Iniciando Frontend..."

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no encontrado"
    exit 1
fi

NODE_PATH="/Users/diego/nodejs/bin/node"
NPX_PATH="/Users/diego/nodejs/bin/npx"

# Verificar si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    $NPX_PATH --yes npm install
fi

# Iniciar servidor de desarrollo
echo "🌐 Iniciando servidor en http://localhost:3000"
$NPX_PATH --yes vite --host --port 3000

