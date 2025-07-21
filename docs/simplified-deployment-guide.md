# Simplified Railway Deployment Guide

This guide provides streamlined instructions for deploying the Portfolio Agent to Railway with the custom domain `portfolioagent.procogia.ai`.

## Step 1: Deploy Backend Service

1. Log in to [Railway](https://railway.app/)
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Connect to GitHub repository: `https://github.com/HarsukritP/InvestmentAgent.git`
5. Configure the backend service:
   - Service name: `portfolioagent-backend`
   - Root directory: `/backend`
   - Environment variables: Add all backend variables from the provided list
   - Set `BASE_URL` to `https://portfolioagent-backend-production.up.railway.app`
   - Set `FRONTEND_URL` to `https://portfolioagent.procogia.ai`

6. Deploy the service and wait for the build to complete
7. Note the generated service URL (will be something like `https://portfolioagent-backend-production.up.railway.app`)

## Step 2: Deploy Frontend Service

1. In your Railway project, click "New Service"
2. Select "Deploy from GitHub repo" (same repository)
3. Configure the frontend service:
   - Service name: `portfolioagent-frontend`
   - Root directory: `/frontend`
   - Environment variables: Add all frontend variables from the provided list
   - Set `REACT_APP_API_URL` to your backend service URL from Step 1
   - Set `BASE_URL` to your backend service URL from Step 1

4. Deploy the service and wait for the build to complete
5. Note the generated service URL (will be something like `https://portfolioagent-procogia-ai.up.railway.app`)

## Step 3: Set Up Custom Domain

1. In your Railway project, go to the frontend service settings
2. Click on the "Domains" tab
3. Click "Add Domain"
4. Enter your custom domain: `portfolioagent.procogia.ai`
5. Follow the DNS configuration instructions provided by Railway:
   - Add a CNAME record pointing to the Railway domain
   - Example: `portfolioagent.procogia.ai CNAME portfolioagent-procogia-ai.up.railway.app`

6. Wait for DNS propagation (can take up to 24-48 hours, but usually much faster)
7. Railway will automatically provision an SSL certificate for your domain

## Step 4: Update Google OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add the following to "Authorized JavaScript origins":
   - `https://portfolioagent.procogia.ai`
   - `https://portfolioagent-procogia-ai.up.railway.app`

5. Add the following to "Authorized redirect URIs":
   - `https://portfolioagent-backend-production.up.railway.app/auth/callback`

6. Save changes

## Step 5: Verify Deployment

1. Visit your custom domain: `https://portfolioagent.procogia.ai`
2. Test the following functionality:
   - User authentication (Google login)
   - Portfolio view
   - Stock search and buying
   - Chat with AI assistant
   - Transaction history

## Troubleshooting

If you encounter any issues:

1. Check Railway logs for both services
2. Verify all environment variables are correctly set
3. Ensure the database is properly initialized (the init_database.py script should run automatically)
4. Check browser console for any CORS or API errors 