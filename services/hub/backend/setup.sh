#!/bin/bash
# Setup script for hub backend

echo "Setting up hub backend..."

# Check if shared directory exists at project root level
if [ -d "../../shared" ]; then
    echo "Copying shared modules from project root..."
    cp -r ../../shared/* .
    echo "✅ Shared modules copied successfully"
else
    echo "⚠️ Shared directory not found at project root"
    
    # Check if shared directory exists at repository root level
    if [ -d "../../../shared" ]; then
        echo "Copying shared modules from repository root..."
        cp -r ../../../shared/* .
        echo "✅ Shared modules copied successfully"
    else
        echo "❌ Shared directory not found at repository root either"
        echo "Creating minimal database_manager.py..."
        
        # Create a minimal database_manager.py if it doesn't exist
        if [ ! -f "database_manager.py" ]; then
            cat > database_manager.py << 'EOF'
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Minimal database manager implementation for hub backend"""
    
    def __init__(self):
        self.hub_connection = None
        logger.warning("Using minimal database manager implementation")
    
    def get_hub_connection(self):
        """Get connection to hub database"""
        logger.warning("Hub connection not implemented in minimal version")
        return None

# Create singleton instance
db_manager = DatabaseManager()
EOF
            echo "✅ Created minimal database_manager.py"
        fi
    fi
fi

echo "Hub backend setup complete!" 