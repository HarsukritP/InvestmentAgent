#!/bin/bash
# Deploy the frontend service to Railway

echo "Deploying frontend service to Railway..."

# Navigate to the frontend directory
cd services/hub/frontend

# Deploy to Railway
railway up --service hub-frontend

echo "Frontend deployment complete!" 