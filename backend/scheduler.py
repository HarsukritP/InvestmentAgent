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


class ActionScheduler:
    """
    Background evaluator for user-defined Actions (automation rules).
    Periodically evaluates active actions and executes when triggers match.
    """
    def __init__(self, db_service, market_service, portfolio_manager):
        self.db_service = db_service
        self.market_service = market_service
        self.portfolio_manager = portfolio_manager

        self.enabled = os.getenv("ACTIONS_SCHEDULER_ENABLED", "true").lower() == "true"
        self._task = None
        self._running = False
        self._last_eval = None
        self._stats = {
            "cycles": 0,
            "evaluated": 0,
            "triggered": 0,
            "executed": 0,
            "errors": 0,
        }

    def start(self) -> None:
        if not self.enabled:
            logger.info("Actions scheduler disabled via env")
            return
        if self._task and not self._task.done():
            logger.warning("Actions scheduler already running")
            return
        self._task = asyncio.create_task(self._loop())
        self._running = True
        logger.info("Started Actions scheduler")

    def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            logger.info("Stopped Actions scheduler")

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "running": self._running,
            "last_evaluated": self._last_eval.isoformat() if self._last_eval else None,
            "stats": self._stats.copy(),
        }

    async def _loop(self) -> None:
        await asyncio.sleep(5)
        while self._running:
            try:
                await self._cycle()
                # Dynamic interval based on market hours
                interval = 10 if self.market_service.is_market_open() else 30
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Actions scheduler loop: {e}")
                self._stats["errors"] += 1
                await asyncio.sleep(30)

    async def _cycle(self) -> None:
        self._stats["cycles"] += 1
        self._last_eval = datetime.now()

        # Fetch active actions for evaluation
        try:
            # For MVP, fetch all active actions for all users
            actions = self.db_service.supabase.table('actions').select('*').eq('status', 'active').execute().data
        except Exception as e:
            logger.error(f"Failed to load actions: {e}")
            self._stats["errors"] += 1
            return

        if not actions:
            return

        # Collect symbols to batch fetch prices
        symbols = sorted({a.get('symbol', '').upper() for a in actions if a.get('symbol')})
        quotes = {}
        if symbols:
            try:
                # Ensure watchlist contains these symbols for background freshness
                self.market_service.add_to_watchlist(symbols)
                quotes = await self.market_service.get_portfolio_quotes(symbols)
            except Exception as e:
                logger.error(f"Failed fetching quotes for actions: {e}")
                self._stats["errors"] += 1

        for action in actions:
            try:
                await self._evaluate_action(action, quotes)
            except Exception as e:
                logger.error(f"Action evaluation error ({action.get('id')}): {e}")
                self._stats["errors"] += 1

    async def _evaluate_action(self, action: Dict[str, Any], quotes: Dict[str, Any]) -> None:
        self._stats["evaluated"] += 1

        # Respect validity window
        now = datetime.utcnow()
        valid_from = action.get('valid_from')
        valid_until = action.get('valid_until')
        if valid_from:
            try:
                from datetime import datetime as dt
                if dt.fromisoformat(valid_from.replace('Z', '+00:00')) > now:
                    return
            except Exception:
                pass
        if valid_until:
            try:
                from datetime import datetime as dt
                if dt.fromisoformat(valid_until.replace('Z', '+00:00')) < now:
                    return
            except Exception:
                pass

        # Cooldown check
        cooldown = action.get('cooldown_seconds')
        last_trig = action.get('last_triggered_at')
        if cooldown and last_trig:
            try:
                from datetime import datetime as dt
                last_dt = dt.fromisoformat(last_trig.replace('Z', '+00:00'))
                if (now - last_dt).total_seconds() < int(cooldown):
                    return
            except Exception:
                pass

        # Max executions
        max_exec = action.get('max_executions') or 1
        exec_count = action.get('executions_count') or 0
        if exec_count >= max_exec:
            # Mark completed
            await self.db_service.update_action(action['id'], action['user_id'], {"status": "completed"})
            return

        trig_type = (action.get('trigger_type') or '').lower()
        params = action.get('trigger_params') or {}
        symbol = (action.get('symbol') or '').upper()

        # Evaluate trigger
        triggered = False
        current_price = None
        if symbol and symbol in quotes:
            current_price = quotes[symbol].get('price')

        if trig_type in ("price_above", "price_below"):
            threshold = float(params.get('threshold')) if params.get('threshold') is not None else None
            if threshold is None or current_price is None:
                return
            if trig_type == "price_above" and current_price >= threshold:
                triggered = True
            if trig_type == "price_below" and current_price <= threshold:
                triggered = True
        elif trig_type == "change_pct":
            # Simple daily change based on cached change_percent
            change_pct = quotes.get(symbol, {}).get('change_percent') if symbol else None
            target = float(params.get('change')) if params.get('change') is not None else None
            direction = (params.get('direction') or 'up').lower()
            if change_pct is None or target is None:
                return
            if direction == 'up' and change_pct >= target:
                triggered = True
            if direction == 'down' and change_pct <= -abs(target):
                triggered = True
        elif trig_type == "time_of_day":
            # Basic window check (HH:MM in UTC for MVP)
            start = params.get('start')  # "HH:MM"
            end = params.get('end')
            if start and end:
                try:
                    sh, sm = [int(x) for x in start.split(':')]
                    eh, em = [int(x) for x in end.split(':')]
                    now_h, now_m = now.hour, now.minute
                    if (now_h, now_m) >= (sh, sm) and (now_h, now_m) <= (eh, em):
                        triggered = True
                except Exception:
                    return
        else:
            # Unsupported trigger yet
            return

        if not triggered:
            return

        self._stats["triggered"] += 1

        # Execute action
        exec_result = await self._execute_action(action, current_price)
        details = {
            "symbol": symbol,
            "price": current_price,
            "quotes_used": bool(quotes),
        }
        if exec_result.get('success'):
            self._stats["executed"] += 1
            await self.db_service.record_action_execution(action['id'], 'success', details, exec_result.get('transaction', {}).get('id'))
            # Increment executions_count and set last_triggered_at
            await self.db_service.update_action(action['id'], action['user_id'], {
                'executions_count': exec_count + 1,
                'last_triggered_at': datetime.utcnow().isoformat()
            })
        else:
            details['error'] = exec_result.get('message') or exec_result.get('error')
            await self.db_service.record_action_execution(action['id'], 'failed', details)

    async def _execute_action(self, action: Dict[str, Any], current_price: Optional[float]) -> Dict[str, Any]:
        action_type = (action.get('action_type') or '').upper()
        symbol = (action.get('symbol') or '').upper()
        quantity = action.get('quantity')
        amount_usd = action.get('amount_usd')

        # Resolve portfolio for user
        user_id = action.get('user_id')
        portfolios = await self.db_service.get_user_portfolios(user_id)
        if not portfolios:
            return {"success": False, "message": "No portfolio found"}
        portfolio_id = portfolios[0]['id']

        # For BUY with amount_usd, convert to shares using current price
        shares = None
        if action_type == 'BUY':
            if quantity:
                shares = float(quantity)
            elif amount_usd and current_price:
                shares = float(amount_usd) / float(current_price)
        elif action_type == 'SELL':
            if quantity:
                shares = float(quantity)

        # Execute via database service
        try:
            if action_type == 'BUY' and shares and shares > 0:
                return await self.db_service.execute_buy_order(portfolio_id, user_id, symbol, shares, float(current_price))
            if action_type == 'SELL' and shares and shares > 0:
                return await self.db_service.execute_sell_order(portfolio_id, user_id, symbol, shares, float(current_price))
            if action_type == 'NOTIFY':
                # For MVP, we only record a success without side effects
                return {"success": True, "message": "Notify action recorded"}
            return {"success": False, "message": "Unsupported or invalid action"}
        except Exception as e:
            return {"success": False, "error": str(e)}
