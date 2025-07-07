#!/bin/bash
# Deploy hub services individually from their own directories

set -e  # Exit on any error

echo "🚀 Deploying Hub Services Individually..."

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
    
    # Check for required files
    if [ ! -f "Dockerfile" ]; then
        echo "❌ Error: Dockerfile not found in $(pwd)"
        cd "$ORIGINAL_DIR"
        return 1
    fi
    
    if [ ! -f "railway.toml" ]; then
        echo "❌ Error: railway.toml not found in $(pwd)"
        cd "$ORIGINAL_DIR"
        return 1
    fi
    
    echo "✅ Found required files"
    
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
deploy_service "services/hub/backend" "hub-backend"

# Deploy frontend
deploy_service "services/hub/frontend" "hub-frontend"

echo "🎉 All hub services deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure environment variables in Railway dashboard"
echo "2. Check service logs for any startup issues"
echo "3. Test the API endpoints"
echo "4. Set up custom domains if needed" 