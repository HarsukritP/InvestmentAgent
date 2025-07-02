#!/bin/bash
# Portfolio Agent Deployment Script

echo "🚀 Deploying ProCogia Portfolio Agent Services..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm i -g @railway/cli"
    exit 1
fi

# Check if logged in
railway whoami || railway login

echo "📦 Deploying Portfolio Backend..."
cd services/portfolio-agent/backend
railway up --service portfolio-backend
cd ../../..

echo "🖥️ Deploying Portfolio Frontend..."
cd services/portfolio-agent/frontend
railway up --service portfolio-frontend
cd ../../..

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set up environment variables in Railway dashboard"
echo "2. Configure domain routing"
echo "3. Test the portfolio services" 