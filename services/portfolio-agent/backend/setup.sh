#!/bin/bash
# Setup script for portfolio agent backend

echo "Setting up portfolio agent backend..."

# Check if database_manager.py exists and is properly configured
if [ -f "database_manager.py" ]; then
    echo "✅ database_manager.py already exists"
else
    echo "Creating database_manager.py..."
    
    cat > database_manager.py << 'EOF'
import os
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioDatabaseManager:
    """Database manager specifically for the Portfolio Agent service"""
    
    def __init__(self):
        """Initialize portfolio database connections"""
        # Hub Database (for integration)
        self.hub_url = os.getenv('HUB_SUPABASE_URL')
        self.hub_key = os.getenv('HUB_SUPABASE_ANON_KEY')
        
        # Portfolio Database (main database for this service)
        self.portfolio_url = os.getenv('PORTFOLIO_SUPABASE_URL', os.getenv('SUPABASE_URL'))
        self.portfolio_key = os.getenv('PORTFOLIO_SUPABASE_ANON_KEY', os.getenv('SUPABASE_ANON_KEY'))
        
        # Initialize clients
        self.hub_client: Optional[Client] = None
        self.portfolio_client: Optional[Client] = None
        
        # Agent database registry
        self.agent_databases: Dict[str, Client] = {}
        
        self._initialize_connections()
        
    def _initialize_connections(self):
        """Initialize database connections safely"""
        try:
            # Initialize portfolio database (main connection)
            if self.portfolio_url and self.portfolio_key:
                self.portfolio_client = create_client(self.portfolio_url, self.portfolio_key)
                self.agent_databases['portfolio-agent'] = self.portfolio_client
                logger.info("✅ Portfolio database connection initialized")
            else:
                logger.warning("⚠️  Portfolio database credentials not found")
            
            # Initialize hub database (for integration when available)
            if self.hub_url and self.hub_key:
                self.hub_client = create_client(self.hub_url, self.hub_key)
                logger.info("✅ Hub database connection initialized for integration")
            else:
                logger.info("ℹ️  Hub database not configured yet")
                
        except Exception as e:
            logger.error(f"❌ Error initializing database connections: {str(e)}")
            
        logger.info("✅ Portfolio database manager initialized")
    
    def get_hub_client(self) -> Optional[Client]:
        """Get hub database client"""
        if not self.hub_client:
            logger.warning("⚠️  Hub database not configured yet")
        return self.hub_client
    
    def get_hub_connection(self) -> Optional[Client]:
        """Alias for get_hub_client"""
        return self.get_hub_client()
    
    def get_agent_client(self, agent_slug: str) -> Optional[Client]:
        """Get database client for specific agent"""
        client = self.agent_databases.get(agent_slug)
        if not client:
            logger.warning(f"⚠️  No database configured for agent: {agent_slug}")
        return client
    
    def register_agent_database(self, agent_slug: str, database_url: str, database_key: str) -> bool:
        """Register a new agent database connection"""
        try:
            client = create_client(database_url, database_key)
            self.agent_databases[agent_slug] = client
            logger.info(f"✅ Registered database for agent: {agent_slug}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register database for agent {agent_slug}: {str(e)}")
            return False
    
    def list_configured_agents(self) -> List[str]:
        """Get list of agents with configured databases"""
        return list(self.agent_databases.keys())
    
    def is_hub_configured(self) -> bool:
        """Check if hub database is configured"""
        return self.hub_client is not None
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections"""
        results = {}
        
        # Test hub connection
        try:
            if self.hub_client:
                # Simple test query
                self.hub_client.table('agents').select('count').limit(1).execute()
                results['hub'] = True
            else:
                results['hub'] = False
        except Exception as e:
            logger.error(f"Hub connection test failed: {str(e)}")
            results['hub'] = False
        
        # Test agent connections
        for agent_slug, client in self.agent_databases.items():
            try:
                if client:
                    # Simple test query (users table should exist in portfolio DB)
                    client.table('users').select('count').limit(1).execute()
                    results[agent_slug] = True
                else:
                    results[agent_slug] = False
            except Exception as e:
                logger.error(f"{agent_slug} connection test failed: {str(e)}")
                results[agent_slug] = False
        
        return results
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            'hub_configured': self.is_hub_configured(),
            'portfolio_configured': bool(self.portfolio_client),
            'agent_count': len(self.agent_databases),
            'configured_agents': self.list_configured_agents()
        }

# Global database manager instance
# This will be imported by other modules
db_manager = PortfolioDatabaseManager()
EOF
    echo "✅ Created database_manager.py"
fi

# Ensure proper file permissions
chmod +x setup.sh

echo "Portfolio agent backend setup complete!" 