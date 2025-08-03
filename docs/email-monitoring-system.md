# Email Monitoring System Setup Guide

## Overview

This document outlines the implementation of an automated email monitoring system for the Investment Agent platform. The system provides hourly health status reports and immediate critical alerts for all backend services.

## Architecture

### Components to Monitor

1. **Database Service** - Supabase/PostgreSQL connection
2. **AI Agent** - OpenAI integration and chat functionality
3. **Market Data Service** - TwelveData API integration
4. **Market Context Service** - FRED API + News API integration
5. **Portfolio Manager** - Portfolio operations and calculations
6. **Auth Service** - Google OAuth authentication

### Email Types

- **Regular Hourly Reports** - Comprehensive status when all services are healthy
- **Critical Alerts** - Immediate notifications for service failures or degraded performance

## Implementation Components

### 1. Email Service (`backend/email_service.py`)

**Purpose**: Handle SMTP email sending with templates

**Key Features**:
- Gmail SMTP integration
- HTML and plain text email templates
- Email queuing and retry logic
- Template rendering for different alert types

**Dependencies**:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import jinja2
```

### 2. Monitoring Service (`backend/monitoring_service.py`)

**Purpose**: Aggregate health data and determine alert conditions

**Key Features**:
- Extend existing `/health` endpoint logic
- Service status aggregation
- Performance metrics collection
- Alert threshold management
- Report generation

**Integration Points**:
- Leverage existing health check methods
- Use current service instances (market_service, ai_agent, etc.)
- Access database connection status

### 3. Background Scheduler (`backend/scheduler.py`)

**Purpose**: Manage automated email sending schedule

**Key Features**:
- Hourly health check execution
- Immediate alert triggering
- Background task management using asyncio
- Error handling and retry logic

**Pattern**: Similar to existing `market_data.py` auto-refresh system

## Dependencies Required

Add to `backend/requirements.txt`:
```
schedule==1.2.0
jinja2==3.1.2
```

## Configuration

### Environment Variables

Add to Railway/local environment:
```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=agentdemos@procogia.ai
SMTP_PASSWORD=@Pr0C0g14
MONITORING_EMAIL_FROM=agentdemos@procogia.ai
MONITORING_EMAIL_TO=agentdemos@procogia.ai

# Multiple Recipients (Optional - for testing or additional notifications)
# Comma-separated list of additional email addresses
MONITORING_EMAIL_ADDITIONAL=your.email@example.com,another@example.com

# Monitoring Settings
MONITORING_ENABLED=true
MONITORING_INTERVAL_HOURS=1
ALERT_THRESHOLD_CRITICAL=3  # Max failures before critical alert
ALERT_THRESHOLD_WARNING=1   # Max failures before warning
```

### Multiple Email Recipients

The system supports sending emails to multiple recipients for testing or team notifications:

- **`MONITORING_EMAIL_TO`** - Primary recipient (required)
- **`MONITORING_EMAIL_ADDITIONAL`** - Additional recipients (optional, comma-separated)

**Examples:**
```bash
# Single recipient (default)
MONITORING_EMAIL_TO=agentdemos@procogia.ai

# Multiple recipients via MONITORING_EMAIL_TO
MONITORING_EMAIL_TO=agentdemos@procogia.ai,team@company.com

# Primary + additional recipients
MONITORING_EMAIL_TO=agentdemos@procogia.ai
MONITORING_EMAIL_ADDITIONAL=developer@company.com,manager@company.com

# For testing purposes
MONITORING_EMAIL_ADDITIONAL=your.personal.email@gmail.com
```

The system automatically:
- Combines all recipients into a single email list
- Removes duplicates
- Logs the number of recipients on startup
- Shows recipient count in monitoring status

## Implementation Steps

### Phase 1: Core Email Service

1. **Create `backend/email_service.py`**
   - Implement SMTP client
   - Create email templates (HTML/text)
   - Add retry logic and error handling

2. **Create email templates**
   - Regular status report template
   - Critical alert template
   - Service-specific error templates

### Phase 2: Monitoring Logic

1. **Create `backend/monitoring_service.py`**
   - Extend existing health check logic
   - Implement status aggregation
   - Add performance metrics collection
   - Create report generation methods

2. **Enhance health checks**
   - Add response time measurement
   - Include service-specific metrics
   - Implement alert thresholds

### Phase 3: Background Scheduler

1. **Create `backend/scheduler.py`**
   - Implement hourly monitoring loop
   - Add immediate alert triggering
   - Include error handling and logging

2. **Integrate with main application**
   - Add startup event in `main.py`
   - Initialize monitoring service
   - Start background tasks

### Phase 4: Integration and Testing

1. **Update `main.py`**
   - Import monitoring services
   - Add startup event handlers
   - Configure service dependencies

2. **Testing and validation**
   - Test email delivery
   - Validate alert thresholds
   - Verify background task operation

## File Structure

```
backend/
├── email_service.py         # SMTP email handling
├── monitoring_service.py    # Health monitoring logic
├── scheduler.py            # Background task management
├── templates/
│   ├── email_status_report.html
│   ├── email_critical_alert.html
│   └── email_base.html
└── main.py                 # Updated with monitoring integration
```

## Email Templates

### Regular Status Report

**Subject**: `✅ Investment Agent - Hourly Status Report`

**Content**:
- Overall system health summary
- Individual service statuses
- Performance metrics
- Uptime statistics
- Recent activity summary

### Critical Alert

**Subject**: `🚨 CRITICAL: Investment Agent Service Alert`

**Content**:
- Failed service details
- Error messages and stack traces
- Impact assessment
- Recommended actions
- Service recovery instructions

## Integration with Existing Code

### Leveraging Current Health Checks

The system will extend the existing `/health` endpoint (lines 1085-1150 in `main.py`):

```python
# Existing health check logic
health_data = await health_check()

# New monitoring service usage
monitoring_result = await monitoring_service.evaluate_health(health_data)
if monitoring_result.requires_alert:
    await email_service.send_critical_alert(monitoring_result)
```

### Background Task Pattern

Follow the existing pattern from `market_data.py`:

```python
# Similar to market data auto-refresh
async def start_monitoring_loop():
    while True:
        try:
            await perform_health_check_and_email()
            await asyncio.sleep(3600)  # 1 hour
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            await asyncio.sleep(60)  # Retry in 1 minute
```

## Deployment Considerations

### Railway Platform

- **No Cron Jobs Required** - Uses internal asyncio background tasks
- **Process Management** - Runs within main application process
- **Environment Variables** - Configure via Railway dashboard
- **Logging** - Integrates with existing Railway logging

### Error Handling

- **Email Delivery Failures** - Retry logic with exponential backoff
- **Service Check Failures** - Continue monitoring other services
- **Network Issues** - Graceful degradation and recovery

### Performance Impact

- **Minimal Overhead** - Health checks reuse existing service methods
- **Asynchronous Operation** - Non-blocking background execution
- **Resource Usage** - Low memory and CPU footprint

## Security Considerations

- **SMTP Credentials** - Store in environment variables only
- **Email Content** - Avoid sensitive data in email bodies
- **Access Control** - Restrict email recipient configuration
- **Logging** - Avoid logging email credentials

## Testing Strategy

### Local Testing

1. **Email Delivery** - Test SMTP connection and delivery
2. **Health Checks** - Validate service monitoring accuracy
3. **Alert Thresholds** - Test alert triggering conditions
4. **Background Tasks** - Verify continuous operation

### Production Testing

1. **Service Failures** - Intentionally trigger service issues
2. **Network Issues** - Test behavior during connectivity problems
3. **Recovery** - Validate system recovery after issues resolved
4. **Performance** - Monitor impact on application performance

## Maintenance

### Regular Tasks

- **Email Template Updates** - Enhance reporting format
- **Threshold Tuning** - Adjust alert sensitivity
- **Log Review** - Monitor system operation
- **Performance Optimization** - Improve efficiency

### Monitoring the Monitor

- **Self-Health Checks** - Monitor the monitoring system itself
- **Fallback Alerts** - Alternative notification methods
- **System Metrics** - Track monitoring system performance

## Troubleshooting

### Common Issues

1. **Email Not Sending**
   - Check SMTP credentials
   - Verify network connectivity
   - Review Gmail security settings

2. **False Alerts**
   - Adjust threshold values
   - Review health check logic
   - Check for network timeouts

3. **Missing Alerts**
   - Verify background task operation
   - Check error logs
   - Validate email delivery

### Debug Information

The system includes comprehensive logging for troubleshooting:
- Service health check results
- Email delivery status
- Background task operation
- Error conditions and recovery

## Future Enhancements

### Potential Improvements

- **Dashboard Integration** - Web UI for monitoring status
- **Multiple Recipients** - Configurable email distribution lists
- **SMS Alerts** - Text message notifications for critical issues
- **Metrics Storage** - Historical health data tracking
- **Custom Thresholds** - Per-service alert configuration
- **Integration APIs** - Webhook notifications for external systems

### Scalability Considerations

- **Service Discovery** - Automatic detection of new services
- **Distributed Monitoring** - Multi-instance coordination
- **Load Balancing** - Monitoring across multiple backend instances
- **Geographic Distribution** - Multi-region monitoring support