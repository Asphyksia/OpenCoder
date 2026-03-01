FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir 'aider-chat[all]'

# Install frontend dependencies
WORKDIR /app/frontend
RUN npm install

# Go back to app directory
WORKDIR /app

# Expose ports
EXPOSE 8000 3000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENGPU_BASE_URL=https://relaygpu.com/backend/openai/v1

# Default command
CMD ["uvicorn", "opencoder.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
