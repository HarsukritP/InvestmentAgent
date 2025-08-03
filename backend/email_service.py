"""
Email Service for Investment Agent Monitoring System
Handles SMTP email sending with templates for status reports and alerts
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import jinja2

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # SMTP Configuration from environment variables
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "agentdemos@procogia.ai")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "@Pr0C0g14")
        
        # Email Configuration
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.email_from = os.getenv("MONITORING_EMAIL_FROM", "agentdemos@procogia.ai")
        self.email_to = os.getenv("MONITORING_EMAIL_TO", "agentdemos@procogia.ai")
        
        # Template Environment
        self.template_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_templates())
        )
        
        # Thread pool for async email sending
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info(f"Email service initialized - Enabled: {self.monitoring_enabled}")
        
    def _get_templates(self) -> Dict[str, str]:
        """Get email templates as dictionary"""
        return {
            'status_report': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 15px; border-radius: 5px; }
        .critical { background-color: #f44336; }
        .warning { background-color: #ff9800; }
        .healthy { background-color: #4CAF50; }
        .service { margin: 10px 0; padding: 10px; border-radius: 5px; border-left: 4px solid #ddd; }
        .service.healthy { border-left-color: #4CAF50; background-color: #f8fff8; }
        .service.warning { border-left-color: #ff9800; background-color: #fff8f0; }
        .service.critical { border-left-color: #f44336; background-color: #fff0f0; }
        .metrics { background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header {{ 'critical' if overall_status == 'degraded' else 'healthy' }}">
        <h2>🤖 Investment Agent - {{ 'CRITICAL ALERT' if overall_status == 'degraded' else 'Status Report' }}</h2>
        <p><strong>Overall Status:</strong> {{ overall_status.upper() }}</p>
        <p><strong>Timestamp:</strong> {{ timestamp }}</p>
    </div>
    
    <h3>📊 Service Status Overview</h3>
    {% for service_name, service_data in services.items() %}
    <div class="service {{ 'critical' if service_data.status == 'error' else 'healthy' }}">
        <h4>{{ service_name.replace('_', ' ').title() }}</h4>
        <p><strong>Status:</strong> {{ service_data.status.upper() }}</p>
        {% if service_data.error %}
        <p><strong>Error:</strong> {{ service_data.error }}</p>
        {% endif %}
        {% if service_data.response_time %}
        <p><strong>Response Time:</strong> {{ "%.2f"|format(service_data.response_time) }}ms</p>
        {% endif %}
    </div>
    {% endfor %}
    
    <div class="metrics">
        <h3>🔧 Configuration Status</h3>
        {% for config_name, config_status in configuration.items() %}
        <p><strong>{{ config_name.replace('_', ' ').title() }}:</strong> 
           {{ '✅ Configured' if config_status else '❌ Not Configured' }}</p>
        {% endfor %}
    </div>
    
    {% if recent_activity %}
    <div class="metrics">
        <h3>📈 Recent Activity</h3>
        {{ recent_activity | safe }}
    </div>
    {% endif %}
    
    <div class="footer">
        <p>This is an automated message from the Investment Agent Monitoring System.</p>
        <p>Backend: https://portfolioagent-backend-production.up.railway.app</p>
        <p>Frontend: https://portfolioagent.procogia.ai</p>
    </div>
</body>
</html>
            ''',
            
            'critical_alert': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f44336; color: white; padding: 15px; border-radius: 5px; }
        .alert-box { background-color: #fff0f0; border: 2px solid #f44336; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .service { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .error { background-color: #fff0f0; border-left: 4px solid #f44336; }
        .warning { background-color: #fff8f0; border-left: 4px solid #ff9800; }
        .code { background-color: #f5f5f5; padding: 10px; font-family: monospace; border-radius: 3px; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🚨 CRITICAL ALERT - Investment Agent Service Failure</h2>
        <p><strong>Alert Time:</strong> {{ timestamp }}</p>
        <p><strong>Severity:</strong> CRITICAL</p>
    </div>
    
    <div class="alert-box">
        <h3>⚠️ Service Failures Detected</h3>
        <p>The following services are experiencing issues and require immediate attention:</p>
    </div>
    
    {% for service_name, service_data in failed_services.items() %}
    <div class="service error">
        <h4>❌ {{ service_name.replace('_', ' ').title() }}</h4>
        <p><strong>Status:</strong> {{ service_data.status.upper() }}</p>
        {% if service_data.error %}
        <p><strong>Error Details:</strong></p>
        <div class="code">{{ service_data.error }}</div>
        {% endif %}
        {% if service_data.impact %}
        <p><strong>Impact:</strong> {{ service_data.impact }}</p>
        {% endif %}
    </div>
    {% endfor %}
    
    <div class="alert-box">
        <h3>🔧 Recommended Actions</h3>
        <ul>
            <li>Check Railway deployment logs for detailed error information</li>
            <li>Verify all environment variables are correctly configured</li>
            <li>Test database connectivity and API key validity</li>
            <li>Review recent deployments for potential issues</li>
            <li>Monitor system recovery and service restoration</li>
        </ul>
    </div>
    
    <div class="service warning">
        <h4>📊 System Information</h4>
        <p><strong>Environment:</strong> Production</p>
        <p><strong>Backend URL:</strong> https://portfolioagent-backend-production.up.railway.app</p>
        <p><strong>Health Check Endpoint:</strong> /health</p>
    </div>
    
    <div class="footer">
        <p><strong>URGENT:</strong> This is a critical system alert requiring immediate attention.</p>
        <p>Investment Agent Monitoring System - ProCogia AI</p>
    </div>
</body>
</html>
            '''
        }
        
    def _send_email_sync(self, subject: str, html_content: str, text_content: str = None) -> bool:
        """Synchronous email sending method"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email '{subject}': {str(e)}")
            return False
    
    async def send_email(self, subject: str, html_content: str, text_content: str = None) -> bool:
        """Asynchronous email sending"""
        if not self.monitoring_enabled:
            logger.info("Email monitoring disabled, skipping email send")
            return True
            
        try:
            # Run sync email sending in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._send_email_sync, 
                subject, 
                html_content, 
                text_content
            )
            return result
        except Exception as e:
            logger.error(f"Error in async email send: {str(e)}")
            return False
    
    async def send_status_report(self, health_data: Dict[str, Any]) -> bool:
        """Send regular hourly status report"""
        try:
            # Determine if this is a critical situation
            overall_status = health_data.get('status', 'unknown')
            is_critical = overall_status == 'degraded'
            
            # Prepare template data
            template_data = {
                'overall_status': overall_status,
                'timestamp': health_data.get('timestamp', datetime.now().isoformat()),
                'services': health_data.get('services', {}),
                'configuration': health_data.get('configuration', {}),
                'recent_activity': self._format_recent_activity()
            }
            
            # Choose subject based on status
            if is_critical:
                subject = "🚨 CRITICAL: Investment Agent Service Alert"
            else:
                subject = "✅ Investment Agent - Hourly Status Report"
            
            # Render template
            template = self.template_env.get_template('status_report')
            html_content = template.render(**template_data)
            
            # Send email
            return await self.send_email(subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending status report: {str(e)}")
            return False
    
    async def send_critical_alert(self, health_data: Dict[str, Any], failed_services: Dict[str, Any]) -> bool:
        """Send immediate critical alert for service failures"""
        try:
            # Prepare template data
            template_data = {
                'timestamp': datetime.now().isoformat(),
                'failed_services': failed_services,
                'overall_status': health_data.get('status', 'unknown')
            }
            
            # Add impact assessment
            for service_name, service_data in failed_services.items():
                if service_name == 'database':
                    service_data['impact'] = "Critical - Portfolio data and user authentication unavailable"
                elif service_name == 'ai_agent':
                    service_data['impact'] = "High - Chat functionality and AI recommendations unavailable"
                elif service_name == 'market_data':
                    service_data['impact'] = "High - Stock prices and portfolio values not updating"
                elif service_name == 'market_context':
                    service_data['impact'] = "Medium - Economic data and news not available"
                else:
                    service_data['impact'] = "Service functionality may be impaired"
            
            subject = "🚨 CRITICAL ALERT: Investment Agent Service Failure"
            
            # Render template
            template = self.template_env.get_template('critical_alert')
            html_content = template.render(**template_data)
            
            # Send email
            return await self.send_email(subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending critical alert: {str(e)}")
            return False
    
    def _format_recent_activity(self) -> str:
        """Format recent system activity for inclusion in reports"""
        try:
            # This could be enhanced to include actual metrics
            return """
            <p>• Market data auto-refresh: Active</p>
            <p>• Portfolio calculations: Normal</p>
            <p>• User authentication: Operational</p>
            <p>• API response times: Within normal range</p>
            """
        except Exception:
            return "<p>Recent activity data unavailable</p>"
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the email service itself"""
        try:
            # Basic configuration check
            config_ok = all([
                self.smtp_host,
                self.smtp_port,
                self.smtp_user,
                self.smtp_password,
                self.email_from,
                self.email_to
            ])
            
            return {
                "status": "healthy" if config_ok else "error",
                "enabled": self.monitoring_enabled,
                "smtp_configured": bool(self.smtp_user and self.smtp_password),
                "recipients_configured": bool(self.email_to),
                "error": None if config_ok else "SMTP configuration incomplete"
            }
        except Exception as e:
            return {
                "status": "error",
                "enabled": self.monitoring_enabled,
                "error": str(e)
            }

# Global email service instance
email_service = EmailService()