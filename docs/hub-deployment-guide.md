# Hub Services Deployment Guide

This guide explains how to deploy the ProCogia AI Hub services to Railway.

## Prerequisites

1. **Railway CLI installed**: `npm install -g @railway/cli`
2. **Railway account**: Sign up at [railway.app](https://railway.app)
3. **Project created**: Create a new Railway project for the hub services

## Service Architecture

The hub consists of two separate services:

### 1. Hub Backend (`services/hub/backend/`)
- **Technology**: Python 3.10 + FastAPI + Uvicorn
- **Port**: 8001
- **Database**: Supabase (hub database)
- **Deployment**: Docker container

### 2. Hub Frontend (`services/hub/frontend/`)
- **Technology**: React 18 + Node.js 18
- **Port**: 3000 (or $PORT from Railway)
- **Build**: Static files served with `serve`
- **Deployment**: Docker container

## Deployment Steps

### Step 1: Deploy Backend Service

```bash
# From project root
./scripts/deploy-hub-backend.sh
```

This will:
1. Navigate to `services/hub/backend/`
2. Verify all required files exist (Dockerfile, requirements.txt, main.py)
3. Deploy using Railway CLI with service name `hub-backend`

### Step 2: Deploy Frontend Service

```bash
# From project root
./scripts/deploy-frontend.sh
```

This will:
1. Navigate to `services/hub/frontend/`
2. Verify all required files exist (Dockerfile, package.json)
3. Deploy using Railway CLI with service name `hub-frontend`

### Step 3: Deploy Both Services

```bash
# Deploy both services at once
./scripts/deploy-hub.sh
```

## Environment Variables

### Hub Backend Environment Variables

Set these in Railway dashboard for the `hub-backend` service:

```bash
# Hub Database
HUB_SUPABASE_URL=https://[your-hub-project-id].supabase.co
HUB_SUPABASE_ANON_KEY=[your-hub-anon-key]
HUB_SUPABASE_SERVICE_KEY=[your-hub-service-key]

# Portfolio Database (for cross-service communication)
PORTFOLIO_SUPABASE_URL=https://[your-portfolio-project-id].supabase.co
PORTFOLIO_SUPABASE_ANON_KEY=[your-portfolio-anon-key]
PORTFOLIO_SUPABASE_SERVICE_KEY=[your-portfolio-service-key]

# Authentication
JWT_SECRET=[your-jwt-secret]
GOOGLE_CLIENT_ID=[your-google-client-id]
GOOGLE_CLIENT_SECRET=[your-google-client-secret]

# Service Configuration
PORT=8001
ENVIRONMENT=production
```

### Hub Frontend Environment Variables

Set these in Railway dashboard for the `hub-frontend` service:

```bash
# API URLs (use Railway service URLs)
REACT_APP_HUB_API_URL=${{HUB_BACKEND_URL}}/api
REACT_APP_PORTFOLIO_API_URL=${{PORTFOLIO_BACKEND_URL}}/api

# Authentication
REACT_APP_GOOGLE_CLIENT_ID=[your-google-client-id]
```

## Service Configuration Files

### Backend Configuration (`services/hub/backend/`)

- **`Dockerfile`**: Multi-stage Docker build with Python 3.10
- **`railway.json`**: Railway deployment configuration
- **`railway.toml`**: Service-specific Railway settings
- **`requirements.txt`**: Python dependencies
- **`main.py`**: FastAPI application entry point

### Frontend Configuration (`services/hub/frontend/`)

- **`Dockerfile`**: Multi-stage Docker build with Node.js 18
- **`railway.json`**: Railway deployment configuration  
- **`railway.toml`**: Service-specific Railway settings
- **`package.json`**: Node.js dependencies and build scripts

## Troubleshooting

### Common Issues

1. **"Dockerfile not found"**
   - Ensure you're running deployment scripts from project root
   - Verify Dockerfile exists in the service directory
   - Check Railway is looking in the correct directory

2. **"npm: command not found" in backend**
   - This indicates Railway is using wrong configuration
   - Remove any root-level `railway.json` or `nixpacks.toml` files
   - Ensure each service has its own configuration

3. **"uvicorn: command not found"**
   - Use `python -m uvicorn` instead of just `uvicorn`
   - Ensure virtual environment is properly activated
   - Check Python dependencies are installed

4. **Port binding issues**
   - Backend should use port 8001
   - Frontend should use $PORT environment variable
   - Ensure EXPOSE statements in Dockerfiles match

### Verification

After deployment, verify services are working:

1. **Backend Health Check**:
   ```bash
   curl https://your-hub-backend.railway.app/health
   ```

2. **Frontend Access**:
   ```bash
   curl https://your-hub-frontend.railway.app/
   ```

3. **API Integration**:
   ```bash
   curl https://your-hub-backend.railway.app/api/hub/status
   ```

## Next Steps

1. Set up custom domains in Railway
2. Configure environment variables
3. Set up database connections
4. Test cross-service communication
5. Configure CORS for production domains 