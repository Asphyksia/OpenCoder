#!/bin/bash
# OpenCoder - Docker Installation Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   OpenCoder Docker Installation      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Checking for docker compose plugin...${NC}"
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✓ Docker Compose found${NC}"

# Check for API key
if [ -z "$OPENGPU_API_KEY" ]; then
    echo -e "${YELLOW}Enter your OpenGPU API key:${NC}"
    read -s API_KEY
    export OPENGPU_API_KEY=$API_KEY
fi

echo ""
echo -e "${YELLOW}Building Docker images...${NC}"
$COMPOSE_CMD build

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Docker Installation Complete!       ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To start OpenCoder:"
echo "  $COMPOSE_CMD up -d"
echo ""
echo "To view logs:"
echo "  $COMPOSE_CMD logs -f"
echo ""
