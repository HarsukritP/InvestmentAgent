#!/bin/bash

echo "🚀 Deploying Hub Service to Railway..."

# Set the deployment root to hub service
cd services/hub

# Deploy backend
echo "📦 Deploying Hub Backend..."
railway up --service hub-backend

# Deploy frontend  
echo "🎨 Deploying Hub Frontend..."
railway up --service hub-frontend

echo "✅ Hub deployment complete!"
echo "Backend: Check Railway dashboard for backend URL"
echo "Frontend: Check Railway dashboard for frontend URL" 