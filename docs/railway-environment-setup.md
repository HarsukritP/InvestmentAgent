# Railway Environment Variables Setup Guide

This guide explains how to set up the environment variables for the ProCogia AI Agent Hub microservices in Railway.

## Hub Backend Service Variables

Navigate to the `hub-backend` service in your Railway project and add these variables:

```
# Hub Database
HUB_SUPABASE_URL=https://[your-hub-project-id].supabase.co
HUB_SUPABASE_ANON_KEY=[your-hub-anon-key]
HUB_SUPABASE_SERVICE_KEY=[your-hub-service-key]

# Portfolio Database (for cross-service communication)
PORTFOLIO_SUPABASE_URL=https://[your-portfolio-project-id].supabase.co
PORTFOLIO_SUPABASE_ANON_KEY=[your-portfolio-anon-key]
PORTFOLIO_SUPABASE_SERVICE_KEY=[your-portfolio-service-key]

# Authentication
JWT_SECRET=[your-existing-jwt-secret]
GOOGLE_CLIENT_ID=[your-existing-google-client-id]
GOOGLE_CLIENT_SECRET=[your-existing-google-client-secret]

# Service Configuration
PORT=8001  # Different from portfolio backend port
```

## Hub Frontend Service Variables

Navigate to the `hub-frontend` service in your Railway project and add these variables:

```
# API URLs
REACT_APP_HUB_API_URL=${{HUB_BACKEND_URL}}/api
REACT_APP_PORTFOLIO_API_URL=${{PORTFOLIO_BACKEND_URL}}/api

# Authentication
REACT_APP_GOOGLE_CLIENT_ID=999018005773-fh94g2r07sr6pa5mfu5hq843ks4itiva.apps.googleusercontent.com
```

## Portfolio Backend Service Variables (Update)

Update your existing portfolio backend service with these additional variables:

```
# Hub Database (for cross-service communication)
HUB_SUPABASE_URL=https://[your-hub-project-id].supabase.co
HUB_SUPABASE_ANON_KEY=[your-hub-anon-key]
HUB_SUPABASE_SERVICE_KEY=[your-hub-service-key]

# Keep existing variables as they are
```

## Portfolio Frontend Service Variables (Update)

Update your existing portfolio frontend service with these additional variables:

```
# Hub API URL
REACT_APP_HUB_API_URL=agenthub-backend.up.railway.app/api

# Keep existing variables as they are
```

## Setting Up Railway Service URLs

After deploying all services, you'll need to connect them:

1. Go to your Railway project
2. Navigate to the "Variables" section
3. Create these shared variables:
   - `HUB_BACKEND_URL`: The URL of your hub backend service
   - `HUB_FRONTEND_URL`: The URL of your hub frontend service
   - `PORTFOLIO_BACKEND_URL`: The URL of your portfolio backend service
   - `PORTFOLIO_FRONTEND_URL`: The URL of your portfolio frontend service

## Testing the Configuration

Once all services are deployed and variables are set:

1. Visit the hub frontend URL
2. You should see the agent selection dashboard
3. Clicking on the Portfolio Agent should redirect to the portfolio frontend
4. Authentication should work across both services 