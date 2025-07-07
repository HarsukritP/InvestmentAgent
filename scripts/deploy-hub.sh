#!/bin/bash
# Deploy both hub services to Railway

echo "Deploying hub services to Railway..."

# Deploy backend
echo "Deploying hub backend..."
./scripts/deploy-hub-backend.sh

# Deploy frontend
echo "Deploying hub frontend..."
./scripts/deploy-frontend.sh

echo "Hub deployment complete!" 