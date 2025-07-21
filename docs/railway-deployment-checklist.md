# Railway Deployment Checklist

## Pre-Deployment

- [ ] GitHub repository is set up and accessible
- [ ] All code changes are committed and pushed to the main branch
- [ ] CORS settings in backend include the custom domain (`portfolioagent.procogia.ai`)
- [ ] Railway.json files are properly configured for both backend and frontend
- [ ] All required API keys are available:
  - [ ] AlphaVantage API keys
  - [ ] TwelveData API key
  - [ ] Gemini API key
  - [ ] FRED API key
  - [ ] News API key
- [ ] Google OAuth credentials are set up
  - [ ] Client ID
  - [ ] Client Secret
- [ ] Supabase database is set up with required tables
  - [ ] Users table
  - [ ] Portfolios table
  - [ ] Holdings table
  - [ ] Transactions table
  - [ ] Market context table
- [ ] JWT secret is generated
- [ ] Access to Railway account is confirmed
- [ ] Access to domain registrar for procogia.ai is confirmed

## Deployment Steps

- [ ] Deploy backend service to Railway
- [ ] Set all backend environment variables
- [ ] Test backend API endpoints
- [ ] Deploy frontend service to Railway
- [ ] Set frontend environment variables (including backend URL)
- [ ] Test frontend connection to backend
- [ ] Configure custom domain in Railway
- [ ] Set up DNS records for custom domain
- [ ] Update Google OAuth settings with new domain
- [ ] Test authentication flow with custom domain

## Post-Deployment Verification

- [ ] Custom domain is accessible (https://portfolioagent.procogia.ai)
- [ ] SSL certificate is valid
- [ ] User authentication works
- [ ] Portfolio data loads correctly
- [ ] Stock search works
- [ ] Buy/sell transactions work
- [ ] Chat with AI assistant works
- [ ] Transaction history displays correctly
- [ ] Application is responsive on mobile devices
- [ ] No CORS errors in browser console
- [ ] No 404 or 500 errors in browser console

## Performance and Monitoring

- [ ] Set up monitoring for backend service
- [ ] Set up monitoring for frontend service
- [ ] Configure alerts for service outages
- [ ] Monitor API usage and rate limits
- [ ] Check database performance

## Documentation

- [ ] Update README with deployment information
- [ ] Document any issues encountered during deployment
- [ ] Create user guide for the deployed application 