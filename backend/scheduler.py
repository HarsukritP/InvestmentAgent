"""
Background Scheduler for Investment Agent Monitoring System
Manages automated email sending schedule using asyncio background tasks
"""
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import traceback

# Configure logging
logger = logging.getLogger(__name__)

class MonitoringScheduler:
    def __init__(self, monitoring_service, email_service):
        self.monitoring_service = monitoring_service
        self.email_service = email_service
        
        # Configuration
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.interval_hours = int(os.getenv("MONITORING_INTERVAL_HOURS", "1"))
        self.interval_seconds = self.interval_hours * 3600  # Convert to seconds
        
        # Task management
        self._monitoring_task = None
        self._is_running = False
        self._last_check_time = None
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "emails_sent": 0,
            "critical_alerts_sent": 0,
            "last_successful_check": None,
            "last_failed_check": None,
            "uptime_start": datetime.now()
        }
        
        logger.info(f"Monitoring scheduler initialized - Enabled: {self.monitoring_enabled}, Interval: {self.interval_hours}h")
    
    def start_monitoring(self) -> None:
        """Start the background monitoring task"""
        if not self.monitoring_enabled:
            logger.info("Monitoring is disabled, not starting scheduler")
            return
        
        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Monitoring task already running")
            return
        
        # Start the background task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._is_running = True
        
        logger.info(f"Started monitoring scheduler with {self.interval_hours} hour interval")
    
    def stop_monitoring(self) -> None:
        """Stop the background monitoring task"""
        self._is_running = False
        
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            logger.info("Stopped monitoring scheduler")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop that runs continuously"""
        logger.info("Starting monitoring loop")
        
        # Perform initial check after a short delay
        await asyncio.sleep(30)  # 30 second startup delay
        
        while self._is_running:
            try:
                # Perform health check and send emails
                await self._perform_monitoring_cycle()
                
                # Reset consecutive failure count on success
                self._consecutive_failures = 0
                
                # Wait for next interval
                await asyncio.sleep(self.interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Increment consecutive failure count
                self._consecutive_failures += 1
                
                # If too many consecutive failures, increase delay
                if self._consecutive_failures >= self._max_consecutive_failures:
                    delay = min(300, 60 * self._consecutive_failures)  # Max 5 minutes
                    logger.error(f"Too many consecutive failures ({self._consecutive_failures}), waiting {delay} seconds")
                    await asyncio.sleep(delay)
                else:
                    # Regular retry delay
                    await asyncio.sleep(60)  # 1 minute before retry
        
        logger.info("Monitoring loop ended")
    
    async def _perform_monitoring_cycle(self) -> None:
        """Perform a complete monitoring cycle"""
        cycle_start_time = datetime.now()
        self.stats["total_checks"] += 1
        
        try:
            logger.info("Starting monitoring cycle")
            
            # Perform comprehensive health check
            health_data = await self.monitoring_service.perform_comprehensive_health_check()
            
            # Log health status
            overall_status = health_data.get("status", "unknown")
            check_time = health_data.get("total_check_time_ms", 0)
            logger.info(f"Health check completed - Status: {overall_status}, Time: {check_time}ms")
            
            # Check if alerts should be sent
            should_alert, alert_type, failed_services = self.monitoring_service.should_send_alert(
                health_data.get("services", {})
            )
            
            # Send appropriate emails
            email_sent = False
            
            if should_alert and alert_type == "critical":
                # Send critical alert
                logger.warning(f"Sending critical alert for services: {list(failed_services.keys())}")
                email_sent = await self.email_service.send_critical_alert(health_data, failed_services)
                
                if email_sent:
                    self.stats["critical_alerts_sent"] += 1
                    logger.info("Critical alert email sent successfully")
                else:
                    logger.error("Failed to send critical alert email")
            
            elif should_alert and alert_type == "warning":
                # Send status report with warning emphasis
                logger.warning(f"Sending warning status report for services: {list(failed_services.keys())}")
                email_sent = await self.email_service.send_status_report(health_data)
                
                if email_sent:
                    logger.info("Warning status report email sent successfully")
                else:
                    logger.error("Failed to send warning status report email")
            
            else:
                # Send regular hourly status report
                logger.info("Sending regular status report")
                email_sent = await self.email_service.send_status_report(health_data)
                
                if email_sent:
                    logger.info("Regular status report email sent successfully")
                else:
                    logger.error("Failed to send regular status report email")
            
            # Update statistics
            if email_sent:
                self.stats["emails_sent"] += 1
            
            self.stats["successful_checks"] += 1
            self.stats["last_successful_check"] = cycle_start_time.isoformat()
            self._last_check_time = cycle_start_time
            
            cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
            logger.info(f"Monitoring cycle completed successfully in {cycle_duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.stats["failed_checks"] += 1
            self.stats["last_failed_check"] = cycle_start_time.isoformat()
            
            # Try to send a failure notification (but don't fail if this fails too)
            try:
                await self._send_monitoring_failure_alert(str(e))
            except Exception as alert_error:
                logger.error(f"Failed to send monitoring failure alert: {str(alert_error)}")
            
            raise  # Re-raise to trigger retry logic
    
    async def _send_monitoring_failure_alert(self, error_message: str) -> None:
        """Send alert about monitoring system failure"""
        try:
            subject = "🚨 CRITICAL: Investment Agent Monitoring System Failure"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 20px;">
                <div style="background-color: #f44336; color: white; padding: 15px; border-radius: 5px;">
                    <h2>🚨 MONITORING SYSTEM FAILURE</h2>
                    <p><strong>Time:</strong> {datetime.now().isoformat()}</p>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #fff0f0; border: 2px solid #f44336; border-radius: 5px;">
                    <h3>Error Details</h3>
                    <p><strong>Error:</strong> {error_message}</p>
                    <p><strong>Consecutive Failures:</strong> {self._consecutive_failures}</p>
                    <p><strong>Last Successful Check:</strong> {self.stats.get('last_successful_check', 'Never')}</p>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
                    <h3>Immediate Actions Required</h3>
                    <ul>
                        <li>Check Railway deployment logs for detailed error information</li>
                        <li>Verify monitoring service configuration</li>
                        <li>Test email service connectivity</li>
                        <li>Monitor system recovery</li>
                    </ul>
                </div>
                
                <p style="font-size: 12px; color: #666; margin-top: 20px;">
                    Investment Agent Monitoring System - ProCogia AI
                </p>
            </body>
            </html>
            """
            
            await self.email_service.send_email(subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send monitoring failure alert: {str(e)}")
    
    async def trigger_immediate_check(self) -> Dict[str, Any]:
        """Trigger an immediate health check and email (for testing/manual trigger)"""
        try:
            logger.info("Triggering immediate monitoring check")
            await self._perform_monitoring_cycle()
            
            return {
                "success": True,
                "message": "Immediate check completed successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Immediate check failed: {str(e)}")
            return {
                "success": False,
                "message": f"Immediate check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and statistics"""
        uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            "enabled": self.monitoring_enabled,
            "running": self._is_running,
            "interval_hours": self.interval_hours,
            "last_check": self._last_check_time.isoformat() if self._last_check_time else None,
            "consecutive_failures": self._consecutive_failures,
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime).split('.')[0],  # Remove microseconds
            "stats": self.stats.copy(),
            "next_check_estimate": (
                (self._last_check_time + timedelta(seconds=self.interval_seconds)).isoformat()
                if self._last_check_time else "Soon"
            )
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the scheduler itself"""
        try:
            is_healthy = (
                self.monitoring_enabled and 
                self._is_running and 
                self._consecutive_failures < self._max_consecutive_failures
            )
            
            return {
                "status": "healthy" if is_healthy else "degraded",
                "enabled": self.monitoring_enabled,
                "running": self._is_running,
                "consecutive_failures": self._consecutive_failures,
                "max_failures": self._max_consecutive_failures,
                "error": None if is_healthy else "Scheduler experiencing issues"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "enabled": self.monitoring_enabled,
                "running": False,
                "error": str(e)
            }

# This will be initialized in main.py with service dependencies