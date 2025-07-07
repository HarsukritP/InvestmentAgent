#!/bin/bash
# Deploy the backend service to Railway

echo "Deploying hub backend service to Railway..."

# Navigate to the backend directory
cd services/hub/backend

# Verify Dockerfile exists
if [ ! -f "Dockerfile" ]; then
  echo "Error: Dockerfile not found in $(pwd)"
  exit 1
else
  echo "Found Dockerfile at $(pwd)/Dockerfile"
fi

# Deploy to Railway
railway up --service hub-backend --dockerfile ./Dockerfile

echo "Backend deployment complete!" 