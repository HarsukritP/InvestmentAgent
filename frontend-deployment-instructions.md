# Frontend Deployment Instructions

## Environment Variables for Frontend

When deploying the frontend to Railway, you need to set the following environment variables:

```
# API Configuration
REACT_APP_API_URL=https://investmentagent-backend-production.up.railway.app
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id

# Build Configuration
NODE_ENV=production
CI=false
PORT=3000
```

## Steps to Deploy Frontend on Railway

1. Go to [Railway.app](https://railway.app/) and sign in
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select the "InvestmentAgent" repository
5. In the deployment settings:
   - Set the root directory to `/frontend`
   - Build command: `npm run build`
   - Start command: `npx serve -s build -l $PORT`
6. Add all the environment variables listed above
7. Deploy the service

## Important Notes

- Make sure to update the `REACT_APP_API_URL` with your actual backend Railway URL
- The frontend deployment should happen after the backend is deployed and you have the backend URL
- You may need to modify the proxy setting in `package.json` if it's hardcoded to localhost
- Use your actual Google Client ID from your local `.env` file, not the placeholder shown above

## Creating a Railway.json for Frontend

You might need to create a specific railway.json file in the frontend directory. Create a file at `frontend/railway.json` with the following content:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm run build"
  },
  "deploy": {
    "startCommand": "npx serve -s build -l $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
``` 