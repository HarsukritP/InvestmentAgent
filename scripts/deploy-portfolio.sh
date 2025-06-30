#!/bin/bash

echo "🚀 Deploying Portfolio Agent Service to Railway..."

# Set the deployment root to portfolio service
cd services/portfolio-agent

# Deploy backend
echo "📦 Deploying Portfolio Backend..."
railway up --service portfolio-backend

# Deploy frontend  
echo "🎨 Deploying Portfolio Frontend..."
railway up --service portfolio-frontend

echo "✅ Portfolio Agent deployment complete!"
echo "Backend: Check Railway dashboard for backend URL"
echo "Frontend: Check Railway dashboard for frontend URL" 