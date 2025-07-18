# Hub Frontend Railway Setup

## Your Current Configuration (CORRECT)

Your existing Railway variables are perfect as configured:

### Portfolio Agent
```
PORTFOLIO_FRONTEND_URL=http://portfolio-frontend.railway.internal
```

### Other Agents (when available)
```
MANUFACTURING_FRONTEND_URL=http://manufacturing-frontend.railway.internal
DOCUMENT_REVIEW_FRONTEND_URL=http://document-review-frontend.railway.internal
CUSTOMER_SUPPORT_FRONTEND_URL=http://customer-support-frontend.railway.internal
```

### Hub Backend (when available)
```
HUB_BACKEND_URL=http://hub-backend.railway.internal
```

### Environment
```
NODE_ENV=production
```

## Your Configuration is Working

The proxy server now uses exactly the URLs you have configured in Railway. No changes needed on your end - your internal Railway URLs are correctly set up.

## How to Set Variables in Railway

1. Go to your Railway project
2. Click on the `hub-frontend` service
3. Go to "Variables" tab
4. Add each variable with its value
5. Redeploy the service

## Testing the Setup

After setting variables and redeploying:

1. **Health Check**: Visit `https://your-hub-frontend.up.railway.app/health`
2. **Debug Info**: Visit `https://your-hub-frontend.up.railway.app/debug/portfolio-test`
3. **Proxy Test**: Visit `https://your-hub-frontend.up.railway.app/portfolio-agent`

## Important Notes

- Only set variables for agents that are actually deployed
- Use the actual Railway URLs for each service
- The proxy will show "NOT_CONFIGURED" for any missing URLs
- All variables are optional - the service will work with partial configuration 