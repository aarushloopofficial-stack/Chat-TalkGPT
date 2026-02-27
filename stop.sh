#!/bin/bash

# Chat&Talk GPT - Stop Services Script

set -e

echo "Stopping Chat&Talk GPT services..."
docker-compose down

echo "Services stopped."
