"""
ProCogia AI Hub - FastAPI backend for multi-agent management
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services (these should be local to the service)
try:
    from database_manager import db_manager
    SHARED_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Database manager not available: {e}")
    # Create a minimal fallback
    class MinimalDBManager:
        def test_connections(self):
            return {"hub": False}
        def is_hub_configured(self):
            return False
        def list_configured_agents(self):
            return []
    db_manager = MinimalDBManager()
    SHARED_SERVICES_AVAILABLE = False

# Import hub services
from hub.hub_api import router as hub_router
from hub.hub_database import hub_db_service

# Create FastAPI app
app = FastAPI(
    title="ProCogia AI Hub",
    description="Central hub for managing multiple AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.railway.app",  # Railway deployments
        "https://procogia.ai",    # Production domain
        "https://*.procogia.ai",  # Production subdomains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Authentication dependency (simplified for hub)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current authenticated user - simplified for hub service"""
    if not credentials:
        return None
    
    # For now, we'll implement a basic token validation
    # In production, this would integrate with your auth service
    token = credentials.credentials
    if token:
        # This is a placeholder - implement proper token validation
        return {"id": "user123", "email": "user@example.com", "name": "Hub User"}
    return None

async def require_auth(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authentication"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@app.get("/")
async def root():
    """Root endpoint for hub service"""
    return {
        "service": "ProCogia AI Hub",
        "version": "1.0.0",
        "description": "Central hub for managing multiple AI agents",
        "status": "active",
        "endpoints": {
            "hub_status": "/api/hub/status",
            "agents": "/api/hub/agents",
            "health": "/health"
        },
        "shared_services": SHARED_SERVICES_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "hub",
        "shared_services": SHARED_SERVICES_AVAILABLE
    }
    
    if SHARED_SERVICES_AVAILABLE:
        # Test database connections
        try:
            connection_status = db_manager.test_connections()
            health_status["database_connections"] = connection_status
            health_status["hub_configured"] = db_manager.is_hub_configured()
        except Exception as e:
            health_status["database_error"] = str(e)
            health_status["status"] = "degraded"
    
    return health_status

# Include hub routes
app.include_router(hub_router)

# Add some hub-specific routes
@app.get("/api/hub/info")
async def get_hub_info():
    """Get hub service information"""
    return {
        "name": "ProCogia AI Hub",
        "version": "1.0.0",
        "description": "Central management system for AI agents",
        "features": [
            "Multi-agent management",
            "User session tracking", 
            "Agent usage analytics",
            "Centralized authentication"
        ],
        "available_endpoints": [
            "/api/hub/status",
            "/api/hub/agents",
            "/api/hub/agents/{slug}",
            "/api/hub/users/{user_id}/agent-stats"
        ]
    }

@app.get("/api/system/info")
async def get_system_info():
    """Get system information for monitoring"""
    return {
        "service_type": "hub",
        "deployment_mode": os.getenv("DEPLOYMENT_MODE", "development"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "shared_services_available": SHARED_SERVICES_AVAILABLE,
        "hub_database_configured": db_manager.is_hub_configured() if SHARED_SERVICES_AVAILABLE else False
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))  # Different default port for hub
    uvicorn.run(app, host="0.0.0.0", port=port) 