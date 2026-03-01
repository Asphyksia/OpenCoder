#!/bin/bash
# Script para iniciar el backend de OpenCoder

# Cargar variables de entorno desde .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activar el entorno virtual
source venv/bin/activate

# Configurar la variable de entorno si no está definida
if [ -z "$OPENGPU_API_KEY" ]; then
    echo "ERROR: OPENGPU_API_KEY no está definida. Añádela al archivo .env"
    exit 1
fi

if [ -z "$OPENGPU_BASE_URL" ]; then
    export OPENGPU_BASE_URL="https://relaygpu.com/backend/openai/v1"
fi

# Iniciar el servidor
uvicorn opencoder.api.main:app --port 8001 --reload
