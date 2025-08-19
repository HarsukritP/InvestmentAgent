# Greenhouse + Merge API Integration Guide

## Overview

This guide walks you through integrating Greenhouse (Applicant Tracking System) with your application via Merge API. Merge provides a unified API to access multiple ATS platforms, making integration simpler and more standardized.

## Prerequisites

1. **Greenhouse Account** with API access
2. **Merge Account** (sign up at [merge.dev](https://merge.dev))
3. **Azure Key Vault** for secure API key storage (for production)

## Step-by-Step Setup

### 1. Get Your Greenhouse API Key

1. **Log into your Greenhouse account**
2. **Navigate to API Management**: Go to Configure → Dev Center → API Credential Management
3. **Create a new API key**:
   - Click "Create New API Key"
   - Set permissions based on your needs:
     - **Read access**: Jobs, Candidates, Applications, Users
     - **Write access**: (optional) for creating candidates/applications
   - Give it a descriptive name like "Merge Integration"
4. **Copy the API key** - you'll need this for Merge configuration

### 2. Set Up Merge Account

1. **Sign up at [merge.dev](https://merge.dev)**
2. **Create a new integration**:
   - Choose "ATS" category
   - Select "Greenhouse" as the provider
3. **Get your Merge API key**:
   - Go to your Merge dashboard
   - Navigate to API Keys section
   - Copy your production API key

### 3. Configure Merge for Greenhouse

1. **In your Merge dashboard**:
   - Go to "Linked Accounts"
   - Click "Add Linked Account"
   - Select "Greenhouse"
2. **Enter your Greenhouse credentials**:
   - API Key: (the one you got from step 1)
   - Greenhouse URL: `https://[your-company].greenhouse.io`
3. **Test the connection** to ensure it's working

### 4. Environment Variables Setup

Add these environment variables to your deployment:

#### For Railway/Production:
```bash
# Merge API Configuration
MERGE_API_KEY=your_merge_production_api_key_here
GREENHOUSE_API_KEY=your_greenhouse_linked_account_token_here
```

#### For Local Development (.env file):
```bash
# Add to your .env file
MERGE_API_KEY=your_merge_api_key
GREENHOUSE_API_KEY=your_greenhouse_account_token
```

### 5. Azure Key Vault Setup (Production Only)

For production deployments using Azure:

1. **Create Key Vault secrets**:
   ```bash
   # In Azure CLI
   az keyvault secret set --vault-name your-keyvault --name "merge-api-key" --value "your_merge_api_key"
   az keyvault secret set --vault-name your-keyvault --name "greenhouse-api-key" --value "your_greenhouse_token"
   ```

2. **Configure your app to read from Key Vault**:
   - Use Azure SDK to retrieve secrets
   - Set environment variables from Key Vault values

### 6. Testing the Integration

Once deployed, test the endpoints:

#### Get Candidates:
```bash
curl -X GET "https://your-api-url/greenhouse/candidates" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Get Jobs:
```bash
curl -X GET "https://your-api-url/greenhouse/jobs" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Get Metrics:
```bash
curl -X GET "https://your-api-url/greenhouse/metrics" \
  -H "Authorization: Bearer your_jwt_token"
```

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/greenhouse/candidates` | GET | Get list of candidates |
| `/greenhouse/jobs` | GET | Get list of job postings |
| `/greenhouse/candidates/{id}` | GET | Get candidate details |
| `/greenhouse/applications` | GET | Get applications |
| `/greenhouse/metrics` | GET | Get recruiting analytics |
| `/greenhouse/search` | GET | Search candidates |

## API Response Examples

### Candidates Response:
```json
{
  "success": true,
  "candidates": [
    {
      "id": "candidate-uuid",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "current_stage": {
        "name": "Phone Screen"
      },
      "applications": [...],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 25,
  "total": 150
}
```

### Jobs Response:
```json
{
  "success": true,
  "jobs": [
    {
      "id": "job-uuid",
      "name": "Senior Software Engineer",
      "status": "open",
      "departments": ["Engineering"],
      "offices": ["San Francisco"],
      "created_at": "2024-01-10T09:00:00Z"
    }
  ],
  "count": 10
}
```

## Security Best Practices

1. **Unique API Keys**: Use separate API keys for different environments
2. **Access Control**: Limit API key permissions to minimum required
3. **Secure Storage**: Use Azure Key Vault or similar for production
4. **Regular Rotation**: Rotate API keys periodically
5. **Monitoring**: Monitor API usage and set up alerts

## Troubleshooting

### Common Issues:

1. **"Greenhouse integration not configured"**:
   - Check that both `MERGE_API_KEY` and `GREENHOUSE_API_KEY` are set
   - Verify the keys are correct and active

2. **"Authentication failed"**:
   - Verify your Greenhouse API key has the correct permissions
   - Check that the linked account in Merge is active

3. **"Rate limit exceeded"**:
   - Merge and Greenhouse have rate limits
   - Implement caching to reduce API calls
   - Contact support to increase limits if needed

### Debug Mode:

Set environment variable for detailed logging:
```bash
LOGGING_LEVEL=DEBUG
```

This will show detailed API requests and responses in the logs.

## Next Steps

1. **Deploy with environment variables** set
2. **Test all endpoints** with real data
3. **Set up monitoring** for API health
4. **Implement caching** for frequently accessed data
5. **Add frontend integration** if needed

## Support

- **Merge Documentation**: [docs.merge.dev](https://docs.merge.dev)
- **Greenhouse API Docs**: [developers.greenhouse.io](https://developers.greenhouse.io)
- **Azure Key Vault**: [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)

## Security Compliance

This integration follows security best practices:
- ✅ API keys stored securely
- ✅ Authentication required for all endpoints
- ✅ No sensitive data logged
- ✅ Rate limiting respected
- ✅ HTTPS only communication
