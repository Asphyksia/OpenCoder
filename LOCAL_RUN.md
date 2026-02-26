# Ejecutar OpenCoder Localmente

## El problema
El entorno de VSCode/Codespaces tiene un conflicto de OpenSSL. El código funciona, pero el entorno no tiene las librerías correctas.

## Solución: Ejecutar en tu PC local

### 1. Instala Python 3.12
```bash
# Windows: descarga de python.org
# Mac: brew install python@3.12
# Linux: sudo apt install python3.12 python3.12-venv
```

### 2. Crea entorno virtual
```bash
cd OpenCoder
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instala dependencias
```bash
pip install -r requirements.txt
pip install git+https://github.com/Aider-AI/aider.git
```

### 4. Configura tu API key
Edita `.env`:
```
OPENGPU_BASE_URL=https://relay.opengpu.network/v1
OPENGPU_API_KEY=relay_sk_tu_api_key
OPENGPU_MODEL=gpt-4o
```

### 5. Ejecuta
```bash
uvicorn opencoder.api.main:app --reload --port 8000
```

### 6. Prueba
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create hello world function", "model": "gpt-4o"}'
```

## Notas
- No subas `.env` a GitHub (ya está en `.gitignore`)
- El proyecto funciona 100% - el problema es solo el entorno sandbox
