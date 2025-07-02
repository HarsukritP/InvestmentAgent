from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import sys
import os
from pathlib import Path

# Try to import from shared directory first
try:
    from database_manager import db_manager
    print("Successfully imported database_manager from path")
except ImportError:
    # If that fails, try to find it in the project structure
    try:
        project_root = Path(__file__).parent.parent.parent.parent.parent  # Go up to project root
        shared_path = os.path.join(project_root, "shared")
        sys.path.append(str(shared_path))
        from database_manager import db_manager
        print(f"Successfully imported database_manager from {shared_path}")
    except ImportError as e:
        print(f"Warning: Shared services not available: {e}")
        # Create a minimal implementation for testing
        class MinimalDBManager:
            def get_hub_connection(self):
                return None
        db_manager = MinimalDBManager()

# Configure logging
logger = logging.getLogger(__name__)

class HubDatabaseService:
    """Service for interacting with the hub database"""
    
    def __init__(self):
        self.supabase = None
        try:
            # Get connection from database manager
            self.supabase = db_manager.get_hub_connection()
            if self.supabase:
                print("Hub database connection established")
            else:
                print("Warning: Hub database connection not available")
        except Exception as e:
            print(f"Error connecting to hub database: {e}")
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents"""
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table("agents").select("*").eq("is_active", True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching agents: {e}")
            return []
    
    async def get_agent_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get agent by slug"""
        if not self.supabase:
            return None
        
        try:
            response = self.supabase.table("agents").select("*").eq("slug", slug).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching agent {slug}: {e}")
            return None

    # Agent Management Methods
    async def register_agent(self, name: str, slug: str, description: str, 
                           detailed_description: str = None, icon_url: str = None, 
                           api_prefix: str = None, frontend_route: str = None, 
                           database_url: str = None) -> Optional[Dict[str, Any]]:
        """Register a new agent in Hub Database"""
        hub_client = self.supabase
        if not hub_client:
            logger.error("Hub database not configured")
            return None
            
        try:
            agent_data = {
                'name': name,
                'slug': slug,
                'description': description,
                'detailed_description': detailed_description,
                'icon_url': icon_url,
                'api_prefix': api_prefix,
                'frontend_route': frontend_route,
                'database_url': database_url
            }
            result = hub_client.table('agents').insert(agent_data).execute()
            logger.info(f"Registered agent: {name} ({slug})")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return None

    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all active agents from Hub Database"""
        hub_client = self.supabase
        if not hub_client:
            logger.warning("Hub database not configured, returning empty list")
            return []
            
        try:
            result = hub_client.table('agents').select('*').eq('status', 'active').execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting agents: {str(e)}")
            return []

    async def update_user_agent_usage(self, user_id: str, agent_slug: str, time_spent: int = None) -> bool:
        """Update user's agent usage statistics in Hub Database"""
        hub_client = self.supabase
        if not hub_client:
            logger.warning("Hub database not configured")
            return False
            
        try:
            # Get current user data
            user_result = hub_client.table('users').select('agent_usage').eq('id', user_id).execute()
            if not user_result.data:
                return False
            
            current_usage = user_result.data[0].get('agent_usage', {})
            agent_stats = current_usage.get(agent_slug, {
                'time_spent': 0,
                'access_count': 0,
                'last_accessed': None
            })
            
            # Update stats
            if time_spent:
                agent_stats['time_spent'] = agent_stats.get('time_spent', 0) + time_spent
            agent_stats['access_count'] = agent_stats.get('access_count', 0) + 1
            agent_stats['last_accessed'] = datetime.utcnow().isoformat()
            
            # Update user record
            current_usage[agent_slug] = agent_stats
            hub_client.table('users').update({'agent_usage': current_usage}).eq('id', user_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating user agent usage: {str(e)}")
            return False

    async def get_user_agent_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's agent usage statistics from Hub Database"""
        hub_client = self.supabase
        if not hub_client:
            logger.warning("Hub database not configured")
            return {}
            
        try:
            result = hub_client.table('users').select('agent_usage').eq('id', user_id).execute()
            if result.data:
                return result.data[0].get('agent_usage', {})
            return {}
        except Exception as e:
            logger.error(f"Error getting user agent stats: {str(e)}")
            return {}

    async def track_agent_access(self, user_id: str, agent_slug: str) -> bool:
        """Track when user accesses an agent"""
        return await self.update_user_agent_usage(user_id, agent_slug)
    
    async def create_user_session(self, user_id: str, agent_slug: str) -> Optional[Dict[str, Any]]:
        """Create a new user session for tracking"""
        hub_client = self.supabase
        if not hub_client:
            logger.warning("Hub database not configured")
            return None
            
        try:
            session_data = {
                'user_id': user_id,
                'agent_slug': agent_slug,
                'session_start': datetime.utcnow().isoformat()
            }
            result = hub_client.table('user_sessions').insert(session_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating user session: {str(e)}")
            return None
    
    async def end_user_session(self, session_id: str, time_spent: int) -> bool:
        """End a user session and record time spent"""
        hub_client = self.supabase
        if not hub_client:
            logger.warning("Hub database not configured")
            return False
            
        try:
            update_data = {
                'session_end': datetime.utcnow().isoformat(),
                'time_spent': time_spent
            }
            hub_client.table('user_sessions').update(update_data).eq('id', session_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error ending user session: {str(e)}")
            return False

# Create a singleton instance
hub_db_service = HubDatabaseService() 