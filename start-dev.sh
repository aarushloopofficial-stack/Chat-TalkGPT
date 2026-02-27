#!/bin/bash

# Chat&Talk GPT - Development Startup Script
# This script starts the development environment using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Chat&Talk GPT - Development Mode${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from template..."
    if [ -f .env.docker ]; then
        cp .env.docker .env
        echo -e "${YELLOW}Please edit .env file and add your API keys${NC}"
    else
        echo -e "${RED}Error: No .env template found${NC}"
        exit 1
    fi
fi

# Build images
echo -e "${GREEN}Building Docker images...${NC}"
docker-compose build

# Start services
echo -e "${GREEN}Starting services...${NC}"
docker-compose up -d

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
sleep 10

# Check health
echo -e "${GREEN}Checking services health...${NC}"
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Backend is healthy (port 8000)${NC}"
else
    echo -e "${RED}✗ Backend is not responding (port 8000)${NC}"
fi

if [ "$FRONTEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is healthy (port 3000)${NC}"
else
    echo -e "${RED}✗ Frontend is not responding (port 3000)${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Services Started Successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Frontend:    http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:     docker-compose down"
echo ""

# Open browser (optional - commented out by default)
# if command -v xdg-open &> /dev/null; then
#     xdg-open http://localhost:3000
# fi
