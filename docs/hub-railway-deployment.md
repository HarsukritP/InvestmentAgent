# Hub Railway Deployment Guide

This guide walks you through deploying the ProCogia AI Agent Hub as microservices on Railway.

## Prerequisites

1. Railway account with access to the existing Portfolio AI Agent project
2. Supabase hub database already set up (see `HUB-DATABASE-SETUP-GUIDE.md`)
3. Railway CLI installed (`npm i -g @railway/cli`)

## Deployment Options

You have two options for deployment:

### Option 1: Using Railway Dashboard (Recommended for First Deployment)

1. **Login to Railway Dashboard**
   - Go to [railway.app](https://railway.app)
   - Login with your account

2. **Create Hub Backend Service**
   - Open your "Portfolio AI Agent" project
   - Click "New Service" → "GitHub Repo"
   - Select your repository
   - Under "Service Settings":
     - Set root directory to `/services/hub/backend`
     - Set build command to `pip install -r requirements.txt`
     - Set start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Click "Deploy"

3. **Create Hub Frontend Service**
   - Click "New Service" → "GitHub Repo" again
   - Select your repository
   - Under "Service Settings":
     - Set root directory to `/services/hub/frontend`
     - Set build command to `npm install && npm run build`
     - Set start command to `npx serve -s build -l $PORT`
   - Click "Deploy"

4. **Configure Environment Variables**
   - Follow instructions in `docs/railway-environment-setup.md`
   - Add all required variables to each service

### Option 2: Using Railway CLI (For Future Deployments)

1. **Login to Railway CLI**
   ```bash
   railway login
   ```

2. **Link to Your Project**
   ```bash
   railway link
   ```
   - Select your "Portfolio AI Agent" project when prompted

3. **Deploy Using the Script**
   ```bash
   ./scripts/deploy-hub.sh
   ```

## Setting Up Domain Routing

For a clean URL structure (e.g., procogia.ai/hub, procogia.ai/portfolio-agent):

1. **Set Up Custom Domain**
   - In Railway dashboard, go to "Settings" → "Domains"
   - Add your domain (e.g., procogia.ai)
   - Verify domain ownership

2. **Configure Path-Based Routing**
   - Create routes for each service:
     - `/hub/*` → Hub Frontend
     - `/api/hub/*` → Hub Backend
     - `/portfolio-agent/*` → Portfolio Frontend
     - `/api/portfolio-agent/*` → Portfolio Backend

3. **Update Environment Variables**
   - Update API URLs to reflect the new routing structure

## Verifying Deployment

1. **Check Hub Backend**
   - Visit `https://[hub-backend-url]/docs`
   - You should see the FastAPI Swagger documentation

2. **Check Hub Frontend**
   - Visit `https://[hub-frontend-url]`
   - You should see the agent selection dashboard

3. **Test Authentication**
   - Try logging in with Google OAuth
   - Verify you can access both hub and portfolio agent

## Troubleshooting

- **Database Connection Issues**
  - Verify Supabase credentials in environment variables
  - Check network access settings in Supabase

- **Cross-Service Communication Problems**
  - Ensure all service URLs are correctly set in environment variables
  - Check CORS settings in backend services

- **Authentication Failures**
  - Verify JWT_SECRET is the same across services
  - Check Google OAuth configuration

## Next Steps

1. Migrate existing users from portfolio database to hub database
2. Test the complete user flow from hub to portfolio agent
3. Monitor logs for any errors or performance issues 