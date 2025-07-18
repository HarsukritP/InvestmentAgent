# Hub Frontend Railway Setup

## Required Environment Variables

Set these variables in the Railway dashboard for the `hub-frontend` service:

### Portfolio Agent
```
PORTFOLIO_FRONTEND_URL=https://procogia-investment-aiagent.up.railway.app
```

### Other Agents (when available)
```
MANUFACTURING_FRONTEND_URL=https://your-manufacturing-agent.up.railway.app
DOCUMENT_REVIEW_FRONTEND_URL=https://your-document-review-agent.up.railway.app
CUSTOMER_SUPPORT_FRONTEND_URL=https://your-customer-support-agent.up.railway.app
```

### Hub Backend (when available)
```
HUB_BACKEND_URL=https://your-hub-backend.up.railway.app
```

### Environment
```
NODE_ENV=production
```

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