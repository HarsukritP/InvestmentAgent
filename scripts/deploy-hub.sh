#!/bin/bash
# Hub Deployment Script

echo "🚀 Deploying ProCogia AI Hub Services..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm i -g @railway/cli"
    exit 1
fi

# Check if logged in
railway whoami || railway login

echo "📦 Deploying Hub Backend..."
cd services/hub/backend
railway up --service hub-backend
cd ../../..

echo "🖥️ Deploying Hub Frontend..."
cd services/hub/frontend
railway up --service hub-frontend
cd ../../..

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set up environment variables in Railway dashboard"
echo "2. Configure domain routing"
echo "3. Test the hub services" 