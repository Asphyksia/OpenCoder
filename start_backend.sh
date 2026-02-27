#!/bin/bash
# Script para iniciar el backend de OpenCoder

# Activar el entorno virtual
source venv/bin/activate

# Configurar la variable de entorno si no está definida
if [ -z "$OPENGPU_API_KEY" ]; then
    export OPENGPU_API_KEY="relay_sk_a175218cff8db1b346a0add4031067eb17b59bd831013f9ac73f6a5b6cae6360"
fi

# Iniciar el servidor
uvicorn opencoder.api.main:app --port 8000 --reload
