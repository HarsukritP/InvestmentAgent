#!/bin/bash
# Master Deployment Script for ProCogia AI Agent Hub

echo "🚀 ProCogia AI Agent Hub Deployment"
echo "=================================="
echo ""
echo "This script will deploy all services to Railway."
echo ""
echo "Available deployment options:"
echo "1) Deploy everything (hub + portfolio agent)"
echo "2) Deploy hub services only"
echo "3) Deploy portfolio agent services only"
echo ""

read -p "Select an option (1-3): " option

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm i -g @railway/cli"
    exit 1
fi

# Check if logged in
railway whoami || railway login

case $option in
    1)
        echo "📦 Deploying ALL services..."
        
        # Deploy hub backend
        echo "🔹 Deploying Hub Backend..."
        cd services/hub/backend
        railway up --service hub-backend
        cd ../../..
        
        # Deploy hub frontend
        echo "🔹 Deploying Hub Frontend..."
        cd services/hub/frontend
        railway up --service hub-frontend
        cd ../../..
        
        # Deploy portfolio backend
        echo "🔹 Deploying Portfolio Backend..."
        cd services/portfolio-agent/backend
        railway up --service portfolio-backend
        cd ../../..
        
        # Deploy portfolio frontend
        echo "🔹 Deploying Portfolio Frontend..."
        cd services/portfolio-agent/frontend
        railway up --service portfolio-frontend
        cd ../../..
        
        echo "✅ All services deployed successfully!"
        ;;
    2)
        echo "📦 Deploying Hub services only..."
        
        # Deploy hub backend
        echo "🔹 Deploying Hub Backend..."
        cd services/hub/backend
        railway up --service hub-backend
        cd ../../..
        
        # Deploy hub frontend
        echo "🔹 Deploying Hub Frontend..."
        cd services/hub/frontend
        railway up --service hub-frontend
        cd ../../..
        
        echo "✅ Hub services deployed successfully!"
        ;;
    3)
        echo "📦 Deploying Portfolio Agent services only..."
        
        # Deploy portfolio backend
        echo "🔹 Deploying Portfolio Backend..."
        cd services/portfolio-agent/backend
        railway up --service portfolio-backend
        cd ../../..
        
        # Deploy portfolio frontend
        echo "🔹 Deploying Portfolio Frontend..."
        cd services/portfolio-agent/frontend
        railway up --service portfolio-frontend
        cd ../../..
        
        echo "✅ Portfolio Agent services deployed successfully!"
        ;;
    *)
        echo "❌ Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Next steps:"
echo "1. Set up environment variables in Railway dashboard"
echo "2. Configure domain routing"
echo "3. Test the services" 