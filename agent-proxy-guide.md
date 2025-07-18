# ProCogia AI Hub - Agent Proxy Integration Guide

This guide provides comprehensive instructions for integrating new AI agents into the ProCogia AI Hub using the proxy architecture. Follow these steps exactly to ensure seamless integration without the issues encountered during the portfolio agent integration.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Hub Frontend Configuration](#hub-frontend-configuration)
3. [Agent Frontend Configuration](#agent-frontend-configuration)
4. [API Proxy Configuration](#api-proxy-configuration)
5. [URL Handling and Routing](#url-handling-and-routing)
6. [Environment Variables](#environment-variables)
7. [Deployment Process](#deployment-process)
8. [Common Issues and Solutions](#common-issues-and-solutions)
9. [Testing Checklist](#testing-checklist)

## Architecture Overview

The ProCogia AI Hub acts as a central router/proxy for multiple AI agents, each deployed as separate services. The architecture consists of:

- **Hub Frontend**: React app that serves as the main entry point and router
- **Hub Backend**: FastAPI service for hub-specific functionality
- **Agent Frontends**: Independent React apps for each agent (portfolio, manufacturing, etc.)
- **Agent Backends**: Independent FastAPI services for each agent

The proxy architecture allows:
1. Users to access agents through a unified URL structure (`procogia.ai/agent-name`)
2. Independent deployment and scaling of each agent
3. Shared authentication and user management
4. Centralized routing and navigation

![Architecture Diagram](https://mermaid.ink/img/pako:eNqNkk1vwjAMhv9KlBMgbYfddpsmDRAnJE47RD5M4kGEJlGSMKmq_vfFKR-CVsfthPPaj99YzmGrNUEGe0cN3yvHrUOVa-MoONS5RV8o5ZwXTlVWO-_NXjlCjxY3aBpjUXm3xrXRDdZGlWjRo8m1Qe-VFVc0ypFHXbmDMtpjrVQJNVrljlRhZVWFRrljyFXlXAXGFOhJuUPQWDtXGrTu4CmKZBgPw3g0jKOHMJLRKBzEURxHYTgYDYbRY_wQDR5HYTyIB6MwHEfxOBwkYRSNpHLHwHmNxYnzP-QvuZDzOZdzOZdzOZf_y7lrLLqzWzfWWdxYrXCtbYGbxqKxBWpfoG0KJYcLdKbEjfIFOm0tFXRmvVVlTnDZnXNnKcAMCpRdB9KUQEZQoiVIYU-QwUdXBxnspCvgTFCBNJDBJ6EjyOjKTOEkbQYfhAZOhDm8Sj-FN-FnkAn_CbLu-xtZLZtK)

## Hub Frontend Configuration

### 1. Server.js Configuration

The hub frontend uses Express.js with http-proxy-middleware to route requests to the appropriate agent services. Here's the complete configuration for adding a new agent:

```javascript
// Add this in services/hub/frontend/server.js

// Define the agent proxy (replace AGENT_NAME with your agent name, e.g., manufacturing-agent)
const agentNameProxy = createProxyMiddleware({
  target: process.env.AGENT_NAME_FRONTEND_URL || 'https://procogia-agentname.up.railway.app',
  changeOrigin: true,
  secure: true,
  pathRewrite: {
    '^/agent-name': '', // Remove /agent-name prefix when forwarding
  },
  onError: (err, req, res) => {
    console.error('🚨 Agent proxy error:', err.message);
    res.status(502).json({ 
      error: 'Agent temporarily unavailable', 
      details: err.message,
      timestamp: new Date().toISOString()
    });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`✅ Proxying agent request: ${req.method} ${req.url} -> ${proxyReq.path}`);
    proxyReq.setHeader('X-Forwarded-Host', req.headers.host);
    proxyReq.setHeader('X-Forwarded-Proto', 'http');
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`📥 Agent proxy response: ${proxyRes.statusCode} for ${req.url}`);
  },
  timeout: 30000,
  logLevel: 'debug'
});

// Agent backend API proxy - for OAuth and API requests
const agentNameApiProxy = createProxyMiddleware({
  target: process.env.AGENT_NAME_BACKEND_URL || 'https://procogia-agentname-service.up.railway.app',
  changeOrigin: true,
  secure: true,
  pathRewrite: {
    '^/agent-name/api': '', // Remove /agent-name/api prefix when forwarding
  },
  onError: (err, req, res) => {
    console.error('🚨 Agent API proxy error:', err.message);
    res.status(502).json({ error: 'Agent API temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`🔌 Proxying agent API: ${req.method} ${req.url} -> ${proxyReq.path}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`📡 Agent API response: ${proxyRes.statusCode} for ${req.url}`);
    
    // Add CORS headers for OAuth
    proxyRes.headers['Access-Control-Allow-Origin'] = '*';
    proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS';
    proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization';
    proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
  }
});

// IMPORTANT: Order of middleware matters!
// 1. First, handle the root route
app.get('/', (req, res) => {
  console.log('🏠 Serving root route - will redirect to ProCogia services');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// 2. Then apply agent frontend proxy
app.use('/agent-name', agentNameProxy);

// 3. Then apply agent API proxy
app.use('/agent-name/api', agentNameApiProxy);

// 4. Apply other agent proxies...
app.use('/portfolio-agent', portfolioProxy);
app.use('/portfolio-agent/api', portfolioApiProxy);
// ... other agents
```

### 2. Health Check and Debug Endpoints

Add the new agent to the health check endpoint for monitoring:

```javascript
// Update the health check endpoint in services/hub/frontend/server.js
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    proxies: {
      portfolio: process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-portfolioagent.up.railway.app',
      agentName: process.env.AGENT_NAME_FRONTEND_URL || 'https://procogia-agentname.up.railway.app',
      // other agents...
      hubApi: process.env.HUB_BACKEND_URL || 'http://hub-backend.railway.internal'
    },
    environment: {
      PORT: process.env.PORT,
      NODE_ENV: process.env.NODE_ENV
    }
  });
});
```

### 3. Update Available Routes in Catch-all Handler

```javascript
// Update the catch-all handler in services/hub/frontend/server.js
app.get('*', (req, res) => {
  console.log(`❌ Route not found: ${req.url}`);
  res.status(404).json({ 
    error: 'Route not found', 
    message: 'This route is not available through the ProCogia AI Hub',
    availableRoutes: [
      '/ - ProCogia Hub (redirects to procogia.com/services)',
      '/portfolio-agent - Portfolio Management Agent',
      '/agent-name - Your New Agent Name',
      // other agents...
      '/api/* - Hub API endpoints',
      '/health - Health check'
    ],
    requestedRoute: req.url,
    timestamp: new Date().toISOString()
  });
});
```

## Agent Frontend Configuration

### 1. Update config.js for Relative API URLs

The agent frontend must be configured to use relative API URLs when accessed through the hub proxy:

```javascript
// In services/agent-name/frontend/src/config.js

// Detect if being accessed through proxy
const isProxied = window.location.pathname.startsWith('/agent-name');

// Use relative API URL when proxied
export const API_URL = isProxied 
  ? '/agent-name/api' // When accessed via proxy, use relative path
  : (process.env.REACT_APP_API_URL || 'https://procogia-agentname-service.up.railway.app');

// Log for debugging
console.log('🔗 Using API URL:', API_URL);
console.log('📍 Current pathname:', window.location.pathname);
console.log('🔄 Is proxied:', isProxied);
```

### 2. Configure React Router with Correct Basename

To prevent URL rewriting issues, configure React Router with the correct basename:

```javascript
// In services/agent-name/frontend/src/App.js

// Determine if we're being accessed through the hub proxy
const isProxied = window.location.pathname.startsWith('/agent-name');
const routerBasename = isProxied ? '/agent-name' : '/';

// Log routing information for debugging
console.log('📍 Current pathname:', window.location.pathname);
console.log('🔄 Is proxied through hub:', isProxied);
console.log('🌐 Using router basename:', routerBasename);

// Use the basename in your Router
return (
  <Router basename={routerBasename}>
    {/* Your routes here */}
  </Router>
);
```

## API Proxy Configuration

### 1. Backend CORS Configuration

The agent backend must be configured to accept requests from the hub:

```python
# In services/agent-name/backend/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local React app URL
        "https://procogia-agentname.up.railway.app",  # Frontend Railway URL
        "https://procogia-agentname-service.up.railway.app",  # Backend Railway URL
        "https://agent-name-frontend.railway.internal",  # Internal frontend
        "https://agent-name-backend.railway.internal",  # Internal backend
        "https://procogia-aihub.up.railway.app",  # Hub frontend
        "https://procogia-ai.up.railway.app",  # Alternative hub URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. OAuth Configuration

For authentication endpoints, add explicit CORS headers:

```python
# In services/agent-name/backend/main.py

@app.get("/auth/login")
async def login(response: Response):
    """Initiate OAuth login with Google"""
    # Add explicit CORS headers
    response.headers["Access-Control-Allow-Origin"] = "https://procogia-aihub.up.railway.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    # Rest of login logic...

@app.options("/auth/login")
async def login_options(response: Response):
    """Handle CORS preflight for auth/login"""
    response.headers["Access-Control-Allow-Origin"] = "https://procogia-aihub.up.railway.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {}
```

### 3. OAuth Callback Configuration

Make sure the OAuth callback uses the correct frontend URL for redirects:

```python
# In services/agent-name/backend/main.py

@app.get("/auth/callback")
async def auth_callback(code: str, state: Optional[str] = None):
    try:
        # Process OAuth callback...
        
        # Redirect to frontend with token
        # IMPORTANT: Use environment variable for frontend URL
        frontend_base_url = os.environ.get("FRONTEND_URL", "https://procogia-agentname.up.railway.app")
        frontend_url = f"{frontend_base_url}/auth/success?token={jwt_token}"
        
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        # Error handling...
        frontend_base_url = os.environ.get("FRONTEND_URL", "https://procogia-agentname.up.railway.app")
        error_url = f"{frontend_base_url}/?error=auth_failed&message={str(e)}"
        return RedirectResponse(url=error_url)
```

## URL Handling and Routing

### 1. Middleware Order

The order of middleware in `server.js` is critical:

1. Root route handler (`/`)
2. Agent frontend proxies (`/agent-name`)
3. Agent API proxies (`/agent-name/api`)
4. Static file serving
5. Catch-all handler

### 2. Static Assets Handling

Static assets should be handled by the agent frontend itself through the main proxy. If you encounter issues with static assets, ensure your proxy configuration is correct.

## Environment Variables

### 1. Hub Frontend Environment Variables

```
PORT=8080
NODE_ENV=production
PORTFOLIO_FRONTEND_URL=https://procogia-portfolioagent.up.railway.app
PORTFOLIO_BACKEND_URL=https://investmentaiagentservice.up.railway.app
AGENT_NAME_FRONTEND_URL=https://procogia-agentname.up.railway.app
AGENT_NAME_BACKEND_URL=https://procogia-agentname-service.up.railway.app
HUB_BACKEND_URL=https://procogia-aihub-service.up.railway.app
```

### 2. Agent Frontend Environment Variables

```
REACT_APP_API_URL=https://procogia-agentname-service.up.railway.app
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

### 3. Agent Backend Environment Variables

```
FRONTEND_URL=https://procogia-agentname.up.railway.app
BASE_URL=https://procogia-agentname-service.up.railway.app
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET=your-jwt-secret
```

## Deployment Process

### 1. Railway Configuration

Each service should have its own `railway.toml` file:

```toml
# services/hub/frontend/railway.toml
[build]
builder = "nixpacks"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "node server.js"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10

[service]
name = "hub-frontend"
```

```toml
# services/agent-name/frontend/railway.toml
[build]
builder = "nixpacks"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "node server.js"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10

[service]
name = "agent-name-frontend"
```

```toml
# services/agent-name/backend/railway.toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10

[service]
name = "agent-name-backend"
```

### 2. Deployment Scripts

Create deployment scripts for your new agent:

```bash
#!/bin/bash
# scripts/deploy-agent-name.sh

echo "🚀 Deploying Agent Name services..."

# Deploy backend
echo "📡 Deploying Agent Name backend..."
cd services/agent-name/backend
railway up --detach
cd ../../..

# Deploy frontend
echo "🖥️ Deploying Agent Name frontend..."
cd services/agent-name/frontend
railway up --detach
cd ../../..

echo "✅ Agent Name deployment complete!"
```

### 3. Deployment Order

Always deploy in this order:
1. Agent backend
2. Agent frontend
3. Hub backend
4. Hub frontend

## Common Issues and Solutions

### 1. URL Rewriting Issues

**Problem**: When accessing the agent through the proxy, the URL changes from `/agent-name` to `/`

**Solution**: Configure React Router with the correct basename as shown in the [Agent Frontend Configuration](#agent-frontend-configuration) section.

### 2. CORS Issues

**Problem**: API requests fail with CORS errors

**Solution**: 
- Add the hub URL to the allowed origins in the agent backend
- Add explicit CORS headers to authentication endpoints
- Ensure the API proxy is correctly configured with CORS headers

### 3. OAuth Redirect Issues

**Problem**: After OAuth login, the user is redirected to the wrong URL

**Solution**: Make sure the `FRONTEND_URL` environment variable is correctly set in the agent backend.

### 4. Static Assets Not Loading

**Problem**: CSS, JS, or images fail to load when accessed through the proxy

**Solution**: Ensure the proxy configuration correctly handles static assets and the pathRewrite rules are correct.

### 5. API Requests Failing

**Problem**: API requests fail when accessed through the proxy

**Solution**: Check that the API proxy is correctly configured and the agent frontend is using the correct relative API URL.

## Testing Checklist

Before considering the integration complete, test the following:

- [ ] Root route (`/`) redirects to ProCogia services
- [ ] Agent route (`/agent-name`) loads the agent frontend
- [ ] Agent URL stays as `/agent-name` (no rewriting to `/`)
- [ ] Static assets (CSS, JS, images) load correctly
- [ ] Sign-in button works and OAuth flow completes successfully
- [ ] API requests work correctly through the proxy
- [ ] Internal navigation within the agent maintains the `/agent-name` prefix
- [ ] Health check endpoint shows the agent status
- [ ] Error handling works correctly for unavailable services

## Conclusion

Following this guide should result in a seamless integration of a new agent into the ProCogia AI Hub. If you encounter any issues not covered here, please refer to the commit history of the portfolio agent integration for additional context and solutions.

Remember that the order of middleware in Express is critical, and proper configuration of React Router's basename is essential for preventing URL rewriting issues.

Good luck with your integration! 