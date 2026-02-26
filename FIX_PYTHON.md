# Cómo arreglar Python en tu PC

Tu Python 3.12 está corrupto (faltan módulos como _socket, _posixsubprocess).

## Solución: Reinstalar Python

Abre una terminal y ejecuta:

```bash
# 1. Actualizar repositorios
sudo apt update

# 2. Reinstalar Python 3.12 completo
sudo apt install --reinstall python3.12 python3.12-venv python3.12-dev

# 3. Verificar que funciona
python3.12 --version
```

## Luego, configurar OpenCoder:

```bash
cd OpenCoder

# Crear entorno virtual
python3.12 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
pip install git+https://github.com/Aider-AI/aider.git

# Configurar API Key (ver .env.example)
# Copia .env.example a .env y configura tu API key de OpenGPU
cp .env.example .env
# Edita .env y pon tu API key

# Ejecutar
uvicorn opencoder.api.main:app --port 8000
```
