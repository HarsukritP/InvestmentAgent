import os
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiDatabaseManager:
    def __init__(self):
        """Initialize multiple database connections"""
        # Hub Database (will be created later)
        self.hub_url = os.getenv('HUB_SUPABASE_URL')
        self.hub_key = os.getenv('HUB_SUPABASE_ANON_KEY')
        
        # Portfolio Database (existing - your current setup)
        self.portfolio_url = os.getenv('PORTFOLIO_SUPABASE_URL', os.getenv('SUPABASE_URL'))  # Fallback to current
        self.portfolio_key = os.getenv('PORTFOLIO_SUPABASE_ANON_KEY', os.getenv('SUPABASE_ANON_KEY'))  # Fallback to current
        
        # Initialize clients only if credentials are available
        self.hub_client: Optional[Client] = None
        self.portfolio_client: Optional[Client] = None
        
        # Agent Database Registry
        self.agent_databases: Dict[str, Client] = {}
        
        self._initialize_connections()
        
    def _initialize_connections(self):
        """Initialize database connections safely"""
        try:
            # Initialize portfolio database (existing connection)
            if self.portfolio_url and self.portfolio_key:
                self.portfolio_client = create_client(self.portfolio_url, self.portfolio_key)
                self.agent_databases['portfolio-agent'] = self.portfolio_client
                logger.info("✅ Portfolio database connection initialized")
            else:
                logger.warning("⚠️  Portfolio database credentials not found")
            
            # Initialize hub database (when available)
            if self.hub_url and self.hub_key:
                self.hub_client = create_client(self.hub_url, self.hub_key)
                logger.info("✅ Hub database connection initialized")
            else:
                logger.info("ℹ️  Hub database not configured yet (will be set up in Phase 1)")
                
        except Exception as e:
            logger.error(f"❌ Error initializing database connections: {str(e)}")
            raise
        
        logger.info("✅ Multi-database manager initialized successfully")
    
    def get_hub_client(self) -> Optional[Client]:
        """Get hub database client"""
        if not self.hub_client:
            logger.warning("⚠️  Hub database not configured yet")
        return self.hub_client
    
    def get_agent_client(self, agent_slug: str) -> Optional[Client]:
        """Get database client for specific agent"""
        client = self.agent_databases.get(agent_slug)
        if not client:
            logger.warning(f"⚠️  No database configured for agent: {agent_slug}")
        return client
    
    def register_agent_database(self, agent_slug: str, database_url: str, database_key: str):
        """Register a new agent database connection"""
        try:
            client = create_client(database_url, database_key)
            self.agent_databases[agent_slug] = client
            logger.info(f"✅ Registered database for agent: {agent_slug}")
        except Exception as e:
            logger.error(f"❌ Failed to register database for agent {agent_slug}: {str(e)}")
            raise
    
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
        if self.hub_client:
            try:
                # Simple test query
                self.hub_client.table('agents').select('count').limit(1).execute()
                results['hub'] = True
            except:
                results['hub'] = False
        else:
            results['hub'] = False
        
        # Test agent connections
        for agent_slug, client in self.agent_databases.items():
            try:
                # Simple test query (users table should exist in portfolio DB)
                if agent_slug == 'portfolio-agent':
                    client.table('users').select('count').limit(1).execute()
                else:
                    # For other agents, just test the connection
                    client.table('users').select('count').limit(1).execute()
                results[agent_slug] = True
            except:
                results[agent_slug] = False
        
        return results

# Global multi-database manager instance
# This will be imported by other modules
db_manager = MultiDatabaseManager() 