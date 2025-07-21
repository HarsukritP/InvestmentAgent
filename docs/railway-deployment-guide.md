# Railway Deployment Guide for Portfolio Agent

This guide outlines the steps to deploy the Portfolio Agent application to Railway and set up a custom domain (portfolioagent.procogia.ai).

## Step 1: Connect to GitHub Repository

1. Fork or clone the repository to your GitHub account:
   ```
   https://github.com/HarsukritP/InvestmentAgent.git
   ```

2. Make sure you have the latest changes:
   ```bash
   git pull origin main
   ```

## Step 2: Deploy Backend Service

1. Log in to [Railway](https://railway.app/)
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select your forked/cloned repository
5. Configure the deployment:
   - Service name: `portfolioagent-backend`
   - Root directory: `/backend`
   - Environment variables: Add all backend variables from `railway-env-variables.md`

6. Deploy the service and wait for the build to complete
7. Once deployed, note the service URL (e.g., `https://portfolioagent-backend-production.up.railway.app`)

## Step 3: Deploy Frontend Service

1. In your Railway project, click "New Service"
2. Select "Deploy from GitHub repo" (same repository)
3. Configure the deployment:
   - Service name: `portfolioagent-frontend`
   - Root directory: `/frontend`
   - Environment variables: Add all frontend variables from `railway-env-variables.md`
   - Make sure to set `REACT_APP_API_URL` to the backend service URL from Step 2

4. Deploy the service and wait for the build to complete
5. Once deployed, note the service URL (e.g., `https://portfolioagent-frontend-production.up.railway.app`)

## Step 4: Set Up Custom Domain

1. In your Railway project, go to the frontend service settings
2. Click on the "Domains" tab
3. Click "Add Domain"
4. Enter your custom domain: `portfolioagent.procogia.ai`
5. Follow the DNS configuration instructions provided by Railway:
   - Add a CNAME record pointing to the Railway domain
   - Example: `portfolioagent.procogia.ai CNAME portfolioagent-frontend-production.up.railway.app`

6. Wait for DNS propagation (can take up to 24-48 hours, but usually much faster)
7. Railway will automatically provision an SSL certificate for your domain

## Step 5: Update Google OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add the following to "Authorized JavaScript origins":
   - `https://portfolioagent.procogia.ai`
   - `https://portfolioagent-frontend-production.up.railway.app`
   - `https://portfolioagent-backend-production.up.railway.app`

5. Add the following to "Authorized redirect URIs":
   - `https://portfolioagent-backend-production.up.railway.app/auth/callback`

6. Save changes

## Step 6: Verify Deployment

1. Visit your custom domain: `https://portfolioagent.procogia.ai`
2. Test the following functionality:
   - User authentication (Google login)
   - Portfolio view
   - Stock search and buying
   - Chat with AI assistant
   - Transaction history

## Troubleshooting

### CORS Issues
- Verify that your backend CORS settings include the custom domain
- Check the browser console for CORS errors

### Authentication Problems
- Ensure Google OAuth settings are correctly configured
- Verify that environment variables are set correctly

### Database Connection Issues
- Check Supabase connection settings
- Verify that all required tables exist

### API Key Issues
- Ensure all API keys are valid and not expired
- Check for rate limiting issues with external APIs

## Monitoring and Maintenance

1. Use Railway's built-in monitoring tools to track:
   - CPU and memory usage
   - Request volume and response times
   - Error rates

2. Set up alerts for critical service metrics
3. Regularly check logs for any errors or warnings
4. Keep API keys and credentials up to date 