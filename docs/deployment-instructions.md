# Deployment Instructions for Railway

## Required Environment Variables

### Backend Environment Variables

The backend service requires the following environment variables:

```
# Supabase Configuration
SUPABASE_URL=<your_supabase_url>
SUPABASE_ANON_KEY=<your_supabase_anon_key>
SUPABASE_SERVICE_KEY=<your_supabase_service_key>

# API Keys
TWELVEDATA_API_KEY=<your_twelvedata_api_key>
FRED_API_KEY=<your_fred_api_key>
NEWS_API_KEY=<your_news_api_key>
OPENAI_API_KEY=<your_openai_api_key>

# Authentication
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
JWT_SECRET=<your_jwt_secret>

# Deployment URLs
PORT=8000
BASE_URL=https://portfolioagent-backend-production.up.railway.app
FRONTEND_URL=https://portfolioagent.procogia.ai
```

### Frontend Environment Variables

The frontend service requires the following environment variables:

```
# API Configuration
REACT_APP_API_URL=https://portfolioagent-backend-production.up.railway.app
REACT_APP_GOOGLE_CLIENT_ID=<your_google_client_id>

# Deployment Configuration
PORT=3000
NODE_ENV=production
CI=false
```

## Deployment Steps

1. **Deploy Backend Service**
   - Create a new service in Railway
   - Connect to GitHub repository: `https://github.com/HarsukritP/InvestmentAgent.git`
   - Set root directory to `/backend`
   - Add all backend environment variables
   - Deploy

2. **Deploy Frontend Service**
   - Create another service in Railway
   - Connect to the same GitHub repository
   - Set root directory to `/frontend`
   - Add all frontend environment variables
   - Make sure `REACT_APP_API_URL` points to your backend service URL
   - Deploy

3. **Set Up Custom Domain**
   - In the frontend service settings, go to the "Domains" tab
   - Add your custom domain: `portfolioagent.procogia.ai`
   - Configure DNS settings as instructed by Railway

## Troubleshooting

- **Backend fails to start**: Check that all Supabase environment variables are correctly set
- **Frontend build fails**: The `CI=false` setting should prevent ESLint warnings from failing the build
- **Authentication issues**: Verify Google OAuth configuration and make sure the redirect URIs are correct 