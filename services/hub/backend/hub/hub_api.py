from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Optional, Any
import logging
from pydantic import BaseModel
from datetime import datetime

from .hub_database import hub_db_service

# Import database manager from local copy
try:
    from database_manager import db_manager
except ImportError:
    # Create a minimal fallback
    class MinimalDBManager:
        def test_connections(self):
            return {"hub": False}
        def is_hub_configured(self):
            return False
        def list_configured_agents(self):
            return []
    db_manager = MinimalDBManager()

# Configure logging
logger = logging.getLogger(__name__)

# Create APIRouter for hub endpoints
router = APIRouter(prefix="/api/hub", tags=["hub"])

# Pydantic models for request/response
class AgentInfo(BaseModel):
    name: str
    slug: str
    description: str
    detailed_description: Optional[str] = None
    icon_url: Optional[str] = None
    api_prefix: Optional[str] = None
    frontend_route: Optional[str] = None

class AgentRegistration(AgentInfo):
    database_url: Optional[str] = None

class UserAgentAccess(BaseModel):
    agent_slug: str
    time_spent: Optional[int] = None

class SystemStatus(BaseModel):
    status: str
    hub_configured: bool
    agents_configured: List[str]
    connection_status: Dict[str, bool]

# Hub Status and Health Endpoints
@router.get("/status", response_model=SystemStatus)
async def get_hub_status():
    """Get current hub system status"""
    try:
        connection_status = db_manager.test_connections()
        return SystemStatus(
            status="active",
            hub_configured=db_manager.is_hub_configured(),
            agents_configured=db_manager.list_configured_agents(),
            connection_status=connection_status
        )
    except Exception as e:
        logger.error(f"Error getting hub status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get hub status")

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Agent Management Endpoints
@router.get("/agents", response_model=List[Dict[str, Any]])
async def get_agents():
    """Get all available agents"""
    try:
        agents = await hub_db_service.get_all_agents()
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agents")

@router.get("/agents/{agent_slug}", response_model=Dict[str, Any])
async def get_agent(agent_slug: str):
    """Get specific agent information"""
    try:
        agent = await hub_db_service.get_agent_by_slug(agent_slug)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agent")

@router.post("/agents", response_model=Dict[str, Any])
async def register_agent(agent: AgentRegistration):
    """Register a new agent (admin only - will add auth later)"""
    try:
        result = await hub_db_service.register_agent(
            name=agent.name,
            slug=agent.slug,
            description=agent.description,
            detailed_description=agent.detailed_description,
            icon_url=agent.icon_url,
            api_prefix=agent.api_prefix,
            frontend_route=agent.frontend_route,
            database_url=agent.database_url
        )
        if not result:
            raise HTTPException(status_code=400, detail="Failed to register agent")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register agent")

# User Session and Usage Tracking
@router.post("/users/{user_id}/agent-access")
async def track_agent_access(user_id: str, access: UserAgentAccess):
    """Track user access to an agent"""
    try:
        success = await hub_db_service.track_agent_access(
            user_id=user_id,
            agent_slug=access.agent_slug
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to track agent access")
        return {"message": "Agent access tracked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking agent access: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track agent access")

@router.get("/users/{user_id}/agent-stats", response_model=Dict[str, Any])
async def get_user_agent_stats(user_id: str):
    """Get user's agent usage statistics"""
    try:
        stats = await hub_db_service.get_user_agent_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user agent stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user stats")

# Database Setup Endpoints (for migration)
@router.get("/database/configured")
async def check_database_configuration():
    """Check if hub database is properly configured"""
    return {
        "hub_configured": db_manager.is_hub_configured(),
        "portfolio_configured": 'portfolio-agent' in db_manager.list_configured_agents(),
        "total_agents": len(db_manager.list_configured_agents())
    }

@router.get("/database/connection-test")
async def test_database_connections():
    """Test all database connections"""
    try:
        connection_status = db_manager.test_connections()
        return {"connections": connection_status}
    except Exception as e:
        logger.error(f"Error testing connections: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test database connections")

# Migration Helper Endpoints (temporary, for setup phase)
@router.post("/setup/initialize-hub")
async def initialize_hub_setup():
    """Initialize hub setup (placeholder for setup phase)"""
    return {
        "message": "Hub setup endpoint ready",
        "next_steps": [
            "Create hub database in Supabase",
            "Configure HUB_SUPABASE_URL and HUB_SUPABASE_ANON_KEY",
            "Run database migration scripts",
            "Register portfolio agent"
        ]
    } 