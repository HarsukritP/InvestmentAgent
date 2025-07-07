import os
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HubDatabaseManager:
    """Database manager specifically for the Hub service"""
    
    def __init__(self):
        """Initialize hub database connections"""
        # Hub Database
        self.hub_url = os.getenv('HUB_SUPABASE_URL')
        self.hub_key = os.getenv('HUB_SUPABASE_ANON_KEY')
        
        # Portfolio Database (for integration)
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
            # Initialize hub database
            if self.hub_url and self.hub_key:
                self.hub_client = create_client(self.hub_url, self.hub_key)
                logger.info("✅ Hub database connection initialized")
            else:
                logger.info("ℹ️  Hub database not configured yet")
            
            # Initialize portfolio database connection (for agent integration)
            if self.portfolio_url and self.portfolio_key:
                self.portfolio_client = create_client(self.portfolio_url, self.portfolio_key)
                self.agent_databases['portfolio-agent'] = self.portfolio_client
                logger.info("✅ Portfolio database connection initialized for integration")
            else:
                logger.warning("⚠️  Portfolio database credentials not found")
                
        except Exception as e:
            logger.error(f"❌ Error initializing database connections: {str(e)}")
            
        logger.info("✅ Hub database manager initialized")
    
    def get_hub_connection(self) -> Optional[Client]:
        """Get hub database client"""
        if not self.hub_client:
            logger.warning("⚠️  Hub database not configured yet")
        return self.hub_client
    
    def get_hub_client(self) -> Optional[Client]:
        """Alias for get_hub_connection"""
        return self.get_hub_connection()
    
    def get_agent_client(self, agent_slug: str) -> Optional[Client]:
        """Get database client for specific agent"""
        client = self.agent_databases.get(agent_slug)
        if not client:
            logger.warning(f"⚠️  No database configured for agent: {agent_slug}")
        return client
    
    def register_agent_database(self, agent_slug: str, database_url: str, database_key: str) -> bool:
        """Register a database for an agent"""
        try:
            client = create_client(database_url, database_key)
            self.agent_databases[agent_slug] = client
            logger.info(f"✅ Registered database for agent: {agent_slug}")
            return True
        except Exception as e:
            logger.error(f"❌ Error registering database for {agent_slug}: {str(e)}")
            return False
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections"""
        connection_status = {}
        
        # Test hub connection
        try:
            if self.hub_client:
                # Try a simple query
                self.hub_client.table('agents').select('count').execute()
                connection_status['hub'] = True
            else:
                connection_status['hub'] = False
        except Exception as e:
            logger.error(f"Hub connection test failed: {str(e)}")
            connection_status['hub'] = False
        
        # Test agent connections
        for agent_slug, client in self.agent_databases.items():
            try:
                if client:
                    # Basic connection test - this might fail if tables don't exist, but connection should work
                    client.auth.get_session()
                    connection_status[agent_slug] = True
                else:
                    connection_status[agent_slug] = False
            except Exception as e:
                logger.error(f"{agent_slug} connection test failed: {str(e)}")
                connection_status[agent_slug] = False
        
        return connection_status
    
    def is_hub_configured(self) -> bool:
        """Check if hub database is properly configured"""
        return self.hub_client is not None
    
    def list_configured_agents(self) -> List[str]:
        """List all configured agent databases"""
        return list(self.agent_databases.keys())
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            'hub_configured': self.is_hub_configured(),
            'hub_url_configured': bool(self.hub_url),
            'agent_count': len(self.agent_databases),
            'configured_agents': self.list_configured_agents()
        }

# Create a singleton instance
db_manager = HubDatabaseManager() 