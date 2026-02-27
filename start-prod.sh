#!/bin/bash

# Chat&Talk GPT - Production Startup Script
# This script starts the production environment using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Chat&Talk GPT - Production Mode${NC}"
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
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env file with your configuration"
    exit 1
fi

# Validate required environment variables
echo -e "${YELLOW}Validating environment configuration...${NC}"

if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=$" .env; then
    echo -e "${RED}Error: GROQ_API_KEY is not set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configuration valid${NC}"

# Build images with no cache for production
echo -e "${GREEN}Building production Docker images (clean build)...${NC}"
docker-compose build --no-cache

# Stop any existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down || true

# Start services in detached mode
echo -e "${GREEN}Starting production services...${NC}"
docker-compose up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 15

# Check health
echo -e "${GREEN}Checking services health...${NC}"
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Backend is healthy (port 8000)${NC}"
else
    echo -e "${RED}✗ Backend is not responding (port 8000)${NC}"
    echo "Check logs: docker-compose logs backend"
    exit 1
fi

if [ "$FRONTEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is healthy (port 3000)${NC}"
else
    echo -e "${RED}✗ Frontend is not responding (port 3000)${NC}"
    echo "Check logs: docker-compose logs frontend"
    exit 1
fi

# Show resource usage
echo ""
echo -e "${GREEN}Container resource usage:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Production Services Started!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Frontend:    http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:     docker-compose down"
echo "To restart: docker-compose restart"
echo ""
