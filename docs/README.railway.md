# Deploying AI Portfolio Agent on Railway

This guide explains how to deploy the AI Portfolio Agent application on Railway.

## Prerequisites

1. A [Railway](https://railway.app/) account
2. [Git](https://git-scm.com/) installed on your local machine
3. [GitHub](https://github.com/) account (for repository hosting)

## Setting Up GitHub Repository

1. Create a new GitHub repository:
   - Go to [GitHub](https://github.com/) and click "New repository"
   - Name it `portfolio-agent` or another name of your choice
   - Choose public or private visibility
   - Click "Create repository"

2. Initialize the local repository and push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/portfolio-agent.git
   git push -u origin main
   ```

## Deploying to Railway

1. Log in to [Railway](https://railway.app/)

2. Create a new project:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select the repository you created

3. Configure environment variables:
   - In your Railway project, go to the "Variables" tab
   - Add the following variables:
     - `PORT`: `8000`
     - `BASE_URL`: Your Railway app URL (e.g., `https://portfolio-agent-production.up.railway.app`)
     - `ALPHAVANTAGE_API_KEY`: Your AlphaVantage API key
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `JWT_SECRET`: A secure random string for JWT encoding
     - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
     - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

4. Deploy the application:
   - Railway will automatically build and deploy your application
   - You can monitor the deployment in the "Deployments" tab

## Setting Up Google OAuth for Production

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Edit your OAuth 2.0 Client ID or create a new one
4. Add your Railway app URL to the authorized JavaScript origins
5. Add `{YOUR_RAILWAY_URL}/auth/callback` to the authorized redirect URIs
6. Save changes

## Connecting Frontend to Backend

For a full deployment, you'll need to deploy the frontend separately and configure it to connect to your Railway backend. You can:

1. Deploy the frontend on a service like Vercel, Netlify, or Railway
2. Set the `REACT_APP_API_URL` environment variable to your Railway backend URL
3. Update the proxy in `package.json` to point to your Railway backend URL

## Monitoring and Logs

- Railway provides logs for your application in the "Logs" tab
- You can monitor your application's performance in the "Metrics" tab
- Set up alerts in the "Alerts" tab to be notified of any issues

## Troubleshooting

If you encounter any issues with your deployment:

1. Check the logs in the Railway dashboard
2. Verify that all environment variables are set correctly
3. Ensure that your Google OAuth configuration is correct for the production URL
4. Check that the CORS settings in `main.py` include your frontend domain

## Next Steps

- Set up a custom domain for your application
- Configure a database for persistent storage
- Set up CI/CD for automated deployments 