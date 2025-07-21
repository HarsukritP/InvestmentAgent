# Backend Deployment Instructions

## Environment Variables for Backend

When deploying the backend to Railway, you need to set the following environment variables:

```
# API Keys
ALPHAVANTAGE_API_KEY=your_alphavantage_key_1
ALPHAVANTAGE_API_KEY_2=your_alphavantage_key_2
ALPHAVANTAGE_API_KEY_3=your_alphavantage_key_3
ALPHAVANTAGE_API_KEY_4=your_alphavantage_key_4
TWELVEDATA_API_KEY=your_twelvedata_key
GEMINI_API_KEY=your_gemini_key

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
BASE_URL=https://investmentagent-backend-production.up.railway.app
FRONTEND_URL=https://investmentagent-frontend-production.up.railway.app
```

## Steps to Deploy Backend on Railway

1. Go to [Railway.app](https://railway.app/) and sign in
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select the "InvestmentAgent" repository
5. In the deployment settings:
   - Set the root directory to `/backend`
   - Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add all the environment variables from your local `.env` file
7. Deploy the service

## Important Notes

- Make sure to update the `BASE_URL` and `FRONTEND_URL` with your actual Railway URLs after deployment
- The backend service needs to be deployed before the frontend so you can get the correct backend URL
- Copy the actual values from your local `.env` file - do not use the placeholder values shown above 