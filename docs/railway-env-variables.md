# Railway Environment Variables

## Backend Environment Variables

```
# API Keys
ALPHAVANTAGE_API_KEY=your_alphavantage_key_1
ALPHAVANTAGE_API_KEY_2=your_alphavantage_key_2
ALPHAVANTAGE_API_KEY_3=your_alphavantage_key_3
ALPHAVANTAGE_API_KEY_4=your_alphavantage_key_4
TWELVEDATA_API_KEY=your_twelvedata_key
GEMINI_API_KEY=your_gemini_key
FRED_API_KEY=your_fred_key
NEWS_API_KEY=your_news_api_key

# Authentication
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Deployment
PORT=8000
BASE_URL=https://portfolioagent-backend-production.up.railway.app
FRONTEND_URL=https://portfolioagent.procogia.ai
```

## Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=https://portfolioagent-backend-production.up.railway.app
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

## Notes

1. Replace all placeholder values with your actual API keys and secrets
2. The `BASE_URL` should be the URL of your backend service on Railway
3. The `FRONTEND_URL` should be set to your custom domain (portfolioagent.procogia.ai)
4. Make sure the `REACT_APP_API_URL` in the frontend points to your backend service URL
5. Use the same `GOOGLE_CLIENT_ID` for both backend and frontend 