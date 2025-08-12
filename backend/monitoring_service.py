"""
Monitoring Service for Investment Agent
Aggregates health data and determines alert conditions
"""
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self, db_service, market_service, ai_agent, auth_service, market_context_service):
        # Service dependencies
        self.db_service = db_service
        self.market_service = market_service
        self.ai_agent = ai_agent
        self.auth_service = auth_service
        self.market_context_service = market_context_service
        
        # Monitoring configuration (require repeated failures and debounce)
        self.alert_threshold_critical = int(os.getenv("ALERT_THRESHOLD_CRITICAL", "3"))
        self.alert_threshold_warning = int(os.getenv("ALERT_THRESHOLD_WARNING", "2"))
        self.alert_debounce_minutes_critical = int(os.getenv("ALERT_DEBOUNCE_MINUTES_CRITICAL", "60"))
        self.alert_debounce_minutes_warning = int(os.getenv("ALERT_DEBOUNCE_MINUTES_WARNING", "30"))
        
        # Service failure tracking
        self.failure_counts = {}
        self.last_alert_times = {}
        self.service_metrics = {}
        
        logger.info("Monitoring service initialized")
    
    async def perform_comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check with timing and detailed metrics"""
        start_time = time.time()
        
        # Check database connection with timing
        db_status, db_time = await self._check_database_health()
        
        # Check AI service with timing
        ai_status, ai_time = await self._check_ai_health()
        
        # Check market data service with timing
        market_status, market_time = await self._check_market_data_health()
        
        # Check market context service with timing
        context_status, context_time = await self._check_market_context_health()
        
        # Check auth service
        auth_status = self._check_auth_health()
        
        # Check portfolio service (always healthy as it's internal logic)
        portfolio_status = {"status": "healthy", "response_time": 0}
        
        # Aggregate all service data
        services = {
            "database": {**db_status, "response_time": db_time},
            "ai_agent": {**ai_status, "response_time": ai_time},
            "market_data": {**market_status, "response_time": market_time},
            "market_context": {**context_status, "response_time": context_time},
            "auth": auth_status,
            "portfolio": portfolio_status
        }
        
        # Check configuration status
        configuration = self._check_configuration()
        
        # Determine overall status
        overall_status = self._determine_overall_status(services)
        
        # Update failure tracking
        self._update_failure_tracking(services)
        
        total_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        health_data = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services,
            "configuration": configuration,
            "total_check_time_ms": round(total_time, 2),
            "monitoring_metadata": {
                "failure_counts": self.failure_counts.copy(),
                "last_alert_times": {k: v.isoformat() for k, v in self.last_alert_times.items()},
                "thresholds": {
                    "critical": self.alert_threshold_critical,
                    "warning": self.alert_threshold_warning
                }
            }
        }
        
        return health_data
    
    async def _check_database_health(self) -> Tuple[Dict[str, Any], float]:
        """Check database health with timing"""
        start_time = time.time()
        
        try:
            # Use existing database test connection method
            await self.db_service.test_connection()
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "error": None,
                "connection_active": True
            }, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "error": str(e),
                "connection_active": False
            }, response_time
    
    async def _check_ai_health(self) -> Tuple[Dict[str, Any], float]:
        """Check AI agent health with timing"""
        start_time = time.time()
        
        try:
            # Use existing AI agent health check
            ai_status = self.ai_agent.health_check()
            
            response_time = (time.time() - start_time) * 1000
            
            # Enhance with additional checks
            enhanced_status = {
                **ai_status,
                "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
            }
            
            return enhanced_status, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "error": str(e),
                "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
            }, response_time
    
    async def _check_market_data_health(self) -> Tuple[Dict[str, Any], float]:
        """Check market data service health with timing"""
        start_time = time.time()
        
        try:
            # Use existing market service health check
            market_status = self.market_service.health_check()
            
            response_time = (time.time() - start_time) * 1000
            
            # Enhance with additional metrics
            enhanced_status = {
                **market_status,
                "auto_refresh_active": self.market_service._auto_refresh_task is not None,
                "watchlist_size": len(self.market_service._watchlist_symbols),
                "last_refresh": self.market_service._last_refresh.isoformat()
            }
            
            return enhanced_status, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "error": str(e),
                "auto_refresh_active": False
            }, response_time
    
    async def _check_market_context_health(self) -> Tuple[Dict[str, Any], float]:
        """Check market context service health with timing"""
        start_time = time.time()
        
        try:
            # Check API key configuration
            fred_configured = bool(os.getenv("FRED_API_KEY"))
            news_configured = bool(os.getenv("NEWS_API_KEY"))
            
            response_time = (time.time() - start_time) * 1000
            
            if not fred_configured:
                return {
                    "status": "error",
                    "error": "FRED_API_KEY not configured",
                    "fred_configured": False,
                    "news_configured": news_configured
                }, response_time
            elif not news_configured:
                return {
                    "status": "error", 
                    "error": "NEWS_API_KEY not configured",
                    "fred_configured": fred_configured,
                    "news_configured": False
                }, response_time
            else:
                return {
                    "status": "healthy",
                    "error": None,
                    "fred_configured": True,
                    "news_configured": True
                }, response_time
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "error": str(e),
                "fred_configured": bool(os.getenv("FRED_API_KEY")),
                "news_configured": bool(os.getenv("NEWS_API_KEY"))
            }, response_time
    
    def _check_auth_health(self) -> Dict[str, Any]:
        """Check authentication service health (supports Auth0 or Google OAuth)"""
        try:
            auth0_configured = bool(
                self.auth_service.auth0_domain and
                self.auth_service.auth0_client_id
            )
            google_configured = bool(
                self.auth_service.google_client_id and
                self.auth_service.google_client_secret
            )

            configured = auth0_configured or google_configured
            provider = "auth0" if auth0_configured else ("google" if google_configured else "none")

            return {
                "status": "healthy" if configured else "warning",
                "error": None if configured else "OAuth not fully configured",
                "provider": provider,
                "auth0_configured": auth0_configured,
                "google_oauth_configured": google_configured,
                "response_time": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "provider": "unknown",
                "auth0_configured": False,
                "google_oauth_configured": False,
                "response_time": 0
            }
    
    def _check_configuration(self) -> Dict[str, bool]:
        """Check environment configuration status"""
        return {
            "twelvedata_key_configured": bool(os.getenv("TWELVEDATA_API_KEY")),
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "oauth_configured": bool(
                (self.auth_service.auth0_domain and self.auth_service.auth0_client_id) or
                (self.auth_service.google_client_id and self.auth_service.google_client_secret)
            ),
            "supabase_configured": bool(
                os.getenv("SUPABASE_URL") and 
                os.getenv("SUPABASE_ANON_KEY")
            ),
            "fred_api_key_configured": bool(os.getenv("FRED_API_KEY")),
            "news_api_key_configured": bool(os.getenv("NEWS_API_KEY")),
            "smtp_configured": bool(
                os.getenv("SMTP_USER") and 
                os.getenv("SMTP_PASSWORD")
            )
        }
    
    def _determine_overall_status(self, services: Dict[str, Any]) -> str:
        """Determine overall system status from individual service statuses"""
        critical_services = ["database", "ai_agent"]
        important_services = ["market_data", "market_context"]
        
        # Check for critical service failures
        for service_name in critical_services:
            if services[service_name]["status"] == "error":
                return "degraded"
        
        # Check for important service failures
        failed_important = sum(
            1 for service_name in important_services 
            if services[service_name]["status"] == "error"
        )
        
        if failed_important >= 2:
            return "degraded"
        elif failed_important >= 1:
            return "warning"
        
        # Check for any warnings
        warning_count = sum(
            1 for service_data in services.values()
            if service_data["status"] == "warning"
        )
        
        if warning_count > 0:
            return "warning"
        
        return "healthy"
    
    def _update_failure_tracking(self, services: Dict[str, Any]) -> None:
        """Update failure tracking for each service"""
        for service_name, service_data in services.items():
            current_status = service_data["status"]
            
            # Initialize tracking if not exists
            if service_name not in self.failure_counts:
                self.failure_counts[service_name] = 0
            
            # Update failure count
            if current_status == "error":
                self.failure_counts[service_name] += 1
            else:
                # Reset failure count on successful check
                self.failure_counts[service_name] = 0
    
    def should_send_alert(self, services: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Determine if an alert should be sent and what type"""
        failed_services = {
            name: data for name, data in services.items() 
            if data["status"] == "error"
        }
        
        if not failed_services:
            return False, "none", {}
        
        # Check for new critical failures
        critical_failures = {}
        for service_name, service_data in failed_services.items():
            failure_count = self.failure_counts.get(service_name, 0)
            
            # Send alert if failure count reaches threshold
            if failure_count >= self.alert_threshold_critical:
                # Debounce using configurable window
                last_alert = self.last_alert_times.get(service_name)
                debounce = timedelta(minutes=self.alert_debounce_minutes_critical)
                if not last_alert or datetime.now() - last_alert > debounce:
                    critical_failures[service_name] = service_data
                    self.last_alert_times[service_name] = datetime.now()
        
        if critical_failures:
            return True, "critical", critical_failures
        
        # Check for warning level failures
        warning_failures = {}
        for service_name, service_data in failed_services.items():
            failure_count = self.failure_counts.get(service_name, 0)
            
            if failure_count >= self.alert_threshold_warning:
                last_alert = self.last_alert_times.get(f"{service_name}_warning")
                debounce = timedelta(minutes=self.alert_debounce_minutes_warning)
                if not last_alert or datetime.now() - last_alert > debounce:
                    warning_failures[service_name] = service_data
                    self.last_alert_times[f"{service_name}_warning"] = datetime.now()
        
        if warning_failures:
            return True, "warning", warning_failures
        
        return False, "none", {}
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring service statistics"""
        return {
            "failure_counts": self.failure_counts.copy(),
            "last_alert_times": {
                k: v.isoformat() for k, v in self.last_alert_times.items()
            },
            "thresholds": {
                "critical": self.alert_threshold_critical,
                "warning": self.alert_threshold_warning
            },
            "monitoring_active": True,
            "services_monitored": [
                "database", "ai_agent", "market_data", 
                "market_context", "auth", "portfolio"
            ]
        }
    
    def reset_failure_tracking(self, service_name: Optional[str] = None) -> None:
        """Reset failure tracking for a specific service or all services"""
        if service_name:
            self.failure_counts[service_name] = 0
            # Remove related alert times
            for key in list(self.last_alert_times.keys()):
                if key.startswith(service_name):
                    del self.last_alert_times[key]
        else:
            self.failure_counts.clear()
            self.last_alert_times.clear()
        
        logger.info(f"Reset failure tracking for {service_name or 'all services'}")

# This will be initialized in main.py with service dependencies