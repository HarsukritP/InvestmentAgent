# User Migration Guide

This guide walks you through migrating existing users from your portfolio database to the new hub database.

## Prerequisites

1. Both Supabase projects set up (portfolio and hub)
2. Environment variables configured with both database credentials
3. Python environment with required packages:
   - `supabase`
   - `python-dotenv`

## Migration Steps

### 1. Prepare Your Environment

Ensure your `.env` file contains both portfolio and hub database credentials:

```
# Portfolio Database
SUPABASE_URL=https://[your-portfolio-project-id].supabase.co
SUPABASE_ANON_KEY=[your-portfolio-anon-key]
SUPABASE_SERVICE_KEY=[your-portfolio-service-key]

# Hub Database
HUB_SUPABASE_URL=https://[your-hub-project-id].supabase.co
HUB_SUPABASE_ANON_KEY=[your-hub-anon-key]
HUB_SUPABASE_SERVICE_KEY=[your-hub-service-key]
```

### 2. Run the Migration Script

```bash
python scripts/migrate-users-to-hub.py
```

### 3. Verify Migration Success

The script will output:
- Number of users found in portfolio database
- Number of users successfully migrated
- Any errors encountered

### 4. Check Hub Database

1. Go to your Hub Supabase project
2. Navigate to "Table Editor" → "users"
3. Verify that all users are present with correct information
4. Check "user_agent_stats" table for initial portfolio agent usage stats

### 5. Test Authentication

1. Try logging in with an existing user account
2. Verify the user can access both hub and portfolio agent
3. Check that user data (portfolios, transactions, etc.) is accessible

## Troubleshooting

### Common Issues

- **Connection Errors**
  - Verify Supabase credentials in environment variables
  - Check network access settings in Supabase

- **Missing Users**
  - Check for errors in migration script output
  - Verify user table structure in both databases

- **Authentication Failures**
  - Ensure JWT_SECRET is the same across services
  - Verify Google OAuth configuration is correct

### Manual Migration

If the script fails, you can manually migrate users:

1. Export users from portfolio database:
   ```sql
   SELECT * FROM users;
   ```

2. Import users to hub database:
   ```sql
   INSERT INTO users (id, email, name, avatar_url, google_id, created_at, updated_at)
   VALUES (...);
   ```

3. Create initial user_agent_stats entries:
   ```sql
   INSERT INTO user_agent_stats (user_id, agent_id, first_used_at, last_used_at)
   SELECT 
     u.id, 
     (SELECT id FROM agents WHERE slug = 'portfolio-agent'),
     u.created_at,
     u.updated_at
   FROM users u;
   ```

## Next Steps

After successful migration:

1. Monitor user logins to ensure smooth transition
2. Consider adding a notification to users about the new hub interface
3. Collect feedback on the new hub experience 