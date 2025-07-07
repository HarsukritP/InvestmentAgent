#!/bin/bash
# Deploy the backend service to Railway

echo "Deploying hub backend service to Railway..."

# Navigate to the backend directory
cd services/hub/backend

# Deploy to Railway
railway up --service hub-backend

echo "Backend deployment complete!" 