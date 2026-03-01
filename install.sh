#!/bin/bash
# OpenCoder - Automatic Installation Script
# Installs all dependencies for Linux/macOS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   OpenCoder Installation Script      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" != "3" ]; then
    echo -e "${RED}Error: Python 3 required${NC}"
    exit 1
fi

if [ "$PYTHON_MINOR" -lt 10 ] || [ "$PYTHON_MINOR" -gt 12 ]; then
    echo -e "${YELLOW}Warning: Python $PYTHON_VERSION detected${NC}"
    echo -e "${YELLOW}OpenCoder works best with Python 3.10-3.12${NC}"
    if [ "$PYTHON_MINOR" -eq 13 ]; then
        echo -e "${RED}Error: Python 3.13 is NOT supported by Aider${NC}"
        echo "Please install Python 3.12"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Run from OpenCoder root directory${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install Aider
echo -e "${YELLOW}Installing Aider...${NC}"
pip install 'aider-chat[all]'

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Create .env file
echo -e "${YELLOW}Setting up environment file...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Edit .env and add your OpenGPU API key${NC}"
    echo "Get your key from: https://relay.opengpu.network"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Installation Complete!              ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OPENGPU_API_KEY"
echo "  2. Run: ./start.sh"
echo ""
