#!/bin/bash
# Deploy the backend service to Railway

echo "Deploying hub backend service to Railway..."

# Get the current directory
ORIGINAL_DIR=$(pwd)

# Navigate to the backend directory
cd services/hub/backend

# Verify required files exist
if [ ! -f "Dockerfile" ]; then
  echo "Error: Dockerfile not found in $(pwd)"
  cd "$ORIGINAL_DIR"
  exit 1
fi

if [ ! -f "requirements.txt" ]; then
  echo "Error: requirements.txt not found in $(pwd)"
  cd "$ORIGINAL_DIR"
  exit 1
fi

if [ ! -f "main.py" ]; then
  echo "Error: main.py not found in $(pwd)"
  cd "$ORIGINAL_DIR"
  exit 1
fi

echo "Found required files in $(pwd)"
echo "Dockerfile: $(ls -la Dockerfile)"
echo "requirements.txt: $(ls -la requirements.txt)"
echo "main.py: $(ls -la main.py)"

# Deploy to Railway with explicit service name
echo "Deploying with Railway CLI..."
railway up --service hub-backend

# Return to original directory
cd "$ORIGINAL_DIR"

echo "Backend deployment complete!" 