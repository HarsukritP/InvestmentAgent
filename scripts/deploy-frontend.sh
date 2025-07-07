#!/bin/bash
# Deploy the frontend service to Railway

echo "Deploying hub frontend service to Railway..."

# Get the current directory
ORIGINAL_DIR=$(pwd)

# Navigate to the frontend directory
cd services/hub/frontend

# Verify required files exist
if [ ! -f "Dockerfile" ]; then
  echo "Error: Dockerfile not found in $(pwd)"
  cd "$ORIGINAL_DIR"
  exit 1
fi

if [ ! -f "package.json" ]; then
  echo "Error: package.json not found in $(pwd)"
  cd "$ORIGINAL_DIR"
  exit 1
fi

echo "Found required files in $(pwd)"
echo "Dockerfile: $(ls -la Dockerfile)"
echo "package.json: $(ls -la package.json)"

# Deploy to Railway with explicit service name
echo "Deploying with Railway CLI..."
railway up --service hub-frontend

# Return to original directory
cd "$ORIGINAL_DIR"

echo "Frontend deployment complete!" 