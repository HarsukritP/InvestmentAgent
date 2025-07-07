#!/bin/bash
# Deploy portfolio agent services individually from their own directories
# 
# IMPORTANT: Each service is deployed from its own isolated directory
# and cannot access files outside that directory. This ensures:
# - Clean separation of concerns
# - No cross-service dependencies during deployment
# - Each service is self-contained with its own dependencies

set -e  # Exit on any error

echo "🚀 Deploying Portfolio Agent Services Individually..."

# Function to deploy a service from its directory
deploy_service() {
    local service_dir="$1"
    local service_name="$2"
    
    echo "📦 Deploying $service_name..."
    echo "   Directory: $service_dir"
    
    # Save current directory
    ORIGINAL_DIR=$(pwd)
    
    # Navigate to service directory
    cd "$service_dir"
    
    # Verify we're in the right place
    echo "   Current directory: $(pwd)"
    echo "   Files in directory:"
    ls -la
    
    # Run setup script if it exists
    if [ -f "setup.sh" ]; then
        echo "   Running setup script..."
        chmod +x setup.sh
        ./setup.sh
    fi
    
    # Check for required files
    if [ ! -f "railway.json" ] && [ ! -f "railway.toml" ]; then
        echo "❌ Error: railway.json or railway.toml not found in $(pwd)"
        cd "$ORIGINAL_DIR"
        return 1
    fi
    
    echo "✅ Found required Railway configuration"
    
    # Initialize Railway in this directory if needed
    if [ ! -f ".railway" ] && [ ! -d ".railway" ]; then
        echo "   Initializing Railway in this directory..."
        railway login || echo "Already logged in"
    fi
    
    # Deploy
    echo "   Deploying with Railway..."
    railway up --service "$service_name" --detach
    
    # Return to original directory
    cd "$ORIGINAL_DIR"
    
    echo "✅ $service_name deployed successfully"
    echo ""
}

echo "Starting individual service deployments..."
echo ""

# Deploy backend first
deploy_service "services/portfolio-agent/backend" "portfolio-agent-backend"

# Deploy frontend
deploy_service "services/portfolio-agent/frontend" "portfolio-agent-frontend"

echo "🎉 All portfolio agent services deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure environment variables in Railway dashboard"
echo "2. Check service logs for any startup issues"
echo "3. Test the API endpoints"
echo "4. Set up custom domains if needed" 