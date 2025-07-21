# Railway Environment Variables

## Backend Environment Variables

```
# API Keys
TWELVEDATA_API_KEY=<your_twelvedata_api_key>
FRED_API_KEY=<your_fred_api_key>
NEWS_API_KEY=<your_news_api_key>
OPENAI_API_KEY=<your_openai_api_key>

# Authentication
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
JWT_SECRET=<your_jwt_secret>

# Supabase Configuration
SUPABASE_URL=<your_supabase_url>
SUPABASE_ANON_KEY=<your_supabase_anon_key>
SUPABASE_SERVICE_KEY=<your_supabase_service_key>

# Deployment URLs
PORT=8000
BASE_URL=https://portfolioagent-backend-production.up.railway.app
FRONTEND_URL=https://portfolioagent.procogia.ai
```

## Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=https://portfolioagent-backend-production.up.railway.app
REACT_APP_GOOGLE_CLIENT_ID=<your_google_client_id>

# Deployment Configuration
PORT=3000
NODE_ENV=production
CI=false
BASE_URL=https://portfolioagent-backend-production.up.railway.app
```

## Notes

1. The `BASE_URL` and `FRONTEND_URL` values have been updated to reflect the new domain (portfolioagent.procogia.ai)
2. When you deploy to Railway, the actual URLs will be:
   - Frontend: https://portfolioagent.procogia.ai (custom domain)
   - Frontend Railway URL: https://portfolioagent-procogia-ai.up.railway.app
   - Backend URL: https://portfolioagent-backend-production.up.railway.app
3. Replace all placeholders with your actual API keys and secrets when setting up in Railway
4. For security reasons, actual API keys and secrets are not stored in the repository 