"""Greenhouse integration service via Merge API for HR/recruiting functionality"""
import os
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GreenhouseService:
    def __init__(self, db_service=None):
        # API keys
        self.merge_api_key = os.getenv("MERGE_API_KEY")
        self.greenhouse_api_key = os.getenv("GREENHOUSE_API_KEY")
        
        # Base URLs
        self.merge_base_url = "https://api.merge.dev/api/ats/v1"
        
        # Headers for Merge API
        self.headers = {
            "Authorization": f"Bearer {self.merge_api_key}",
            "X-Account-Token": self.greenhouse_api_key,  # Greenhouse account token via Merge
            "Content-Type": "application/json"
        }
        
        # Import database service for caching
        if db_service is None:
            from database import db_service as default_db_service
            self.db_service = default_db_service
        else:
            self.db_service = db_service
            
        # Log configuration status
        if not self.merge_api_key:
            print("⚠️  WARNING: MERGE_API_KEY not found in environment variables")
            print("   Greenhouse integration will be disabled")
            self.enabled = False
        elif not self.greenhouse_api_key:
            print("⚠️  WARNING: GREENHOUSE_API_KEY not found in environment variables")
            print("   Greenhouse integration will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✅ Merge API configured for Greenhouse integration")
            
    async def get_candidates(self, limit: int = 50, stage: str = None) -> Dict[str, Any]:
        """Get candidates from Greenhouse via Merge API"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Greenhouse integration not configured",
                "candidates": []
            }
            
        try:
            url = f"{self.merge_base_url}/candidates"
            params = {"page_size": limit}
            
            if stage:
                params["stage"] = stage
                
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "candidates": data.get("results", []),
                "count": len(data.get("results", [])),
                "total": data.get("count", 0),
                "next": data.get("next"),
                "previous": data.get("previous")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching candidates: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch candidates: {str(e)}",
                "candidates": []
            }
    
    async def get_jobs(self, status: str = "open", limit: int = 50) -> Dict[str, Any]:
        """Get job postings from Greenhouse via Merge API"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Greenhouse integration not configured",
                "jobs": []
            }
            
        try:
            url = f"{self.merge_base_url}/jobs"
            params = {
                "page_size": limit,
                "status": status
            }
                
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "jobs": data.get("results", []),
                "count": len(data.get("results", [])),
                "total": data.get("count", 0)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching jobs: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch jobs: {str(e)}",
                "jobs": []
            }
    
    async def get_candidate_details(self, candidate_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific candidate"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Greenhouse integration not configured"
            }
            
        try:
            url = f"{self.merge_base_url}/candidates/{candidate_id}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "candidate": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching candidate details: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch candidate details: {str(e)}"
            }
    
    async def get_applications(self, candidate_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Get applications from Greenhouse"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Greenhouse integration not configured",
                "applications": []
            }
            
        try:
            url = f"{self.merge_base_url}/applications"
            params = {}
            
            if candidate_id:
                params["candidate_id"] = candidate_id
            if job_id:
                params["job_id"] = job_id
                
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "applications": data.get("results", []),
                "count": len(data.get("results", []))
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching applications: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch applications: {str(e)}",
                "applications": []
            }
    
    async def get_recruiting_metrics(self) -> Dict[str, Any]:
        """Get recruiting metrics and analytics"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Greenhouse integration not configured"
            }
            
        try:
            # Get multiple data points for metrics
            candidates_response = await self.get_candidates(limit=100)
            jobs_response = await self.get_jobs(limit=100)
            
            if not candidates_response["success"] or not jobs_response["success"]:
                return {
                    "success": False,
                    "error": "Failed to fetch data for metrics"
                }
            
            candidates = candidates_response["candidates"]
            jobs = jobs_response["jobs"]
            
            # Calculate basic metrics
            total_candidates = len(candidates)
            total_open_jobs = len(jobs)
            
            # Analyze candidate stages
            stage_counts = {}
            for candidate in candidates:
                stage = candidate.get("current_stage", {}).get("name", "Unknown")
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Calculate time-to-hire metrics (simplified)
            recent_hires = [c for c in candidates if c.get("hired_at")]
            avg_time_to_hire = None
            if recent_hires:
                # This would need more detailed calculation in production
                avg_time_to_hire = "7-14 days"  # Placeholder
            
            return {
                "success": True,
                "metrics": {
                    "total_candidates": total_candidates,
                    "total_open_jobs": total_open_jobs,
                    "candidates_by_stage": stage_counts,
                    "avg_time_to_hire": avg_time_to_hire,
                    "recent_hires_count": len(recent_hires)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recruiting metrics: {e}")
            return {
                "success": False,
                "error": f"Failed to generate metrics: {str(e)}"
            }
    
    async def search_candidates(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search candidates by name, email, or skills"""
        if not self.enabled:
            return {
                "success": False,
                "error": "Greenhouse integration not configured",
                "candidates": []
            }
            
        try:
            # Note: Actual search implementation depends on Merge API capabilities
            # This is a simplified version
            candidates_response = await self.get_candidates(limit=100)
            
            if not candidates_response["success"]:
                return candidates_response
            
            candidates = candidates_response["candidates"]
            
            # Simple text search across candidate data
            query_lower = query.lower()
            filtered_candidates = []
            
            for candidate in candidates:
                # Search in name, email, and other text fields
                searchable_text = " ".join([
                    str(candidate.get("first_name", "")),
                    str(candidate.get("last_name", "")),
                    str(candidate.get("email", "")),
                    str(candidate.get("phone_number", "")),
                    " ".join(candidate.get("tags", []))
                ]).lower()
                
                if query_lower in searchable_text:
                    filtered_candidates.append(candidate)
                    
                if len(filtered_candidates) >= limit:
                    break
            
            return {
                "success": True,
                "candidates": filtered_candidates,
                "count": len(filtered_candidates),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            return {
                "success": False,
                "error": f"Failed to search candidates: {str(e)}",
                "candidates": []
            }
