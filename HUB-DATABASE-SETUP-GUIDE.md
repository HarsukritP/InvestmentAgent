# ProCogia AI Hub - Database Setup Guide

## 🎯 Overview

This guide walks you through setting up the **hub database** for your multi-agent ProCogia AI platform. The hub database will centrally manage users, agent registry, and usage analytics while your portfolio agent keeps its dedicated database.

## 📋 Prerequisites

- [x] Existing ProCogia portfolio agent working
- [x] Current Supabase project for portfolio (keep this!)
- [ ] New Supabase project for hub (we'll create this)
- [ ] Python 3.8+ with pip

## 🚀 Step-by-Step Setup

### Step 1: Create New Supabase Project for Hub

1. **Go to [supabase.com](https://supabase.com) and log in**
2. **Click "New Project"**
3. **Fill in project details:**
   - **Name**: `ProCogia AI Hub`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Same as your portfolio database (for lower latency)
4. **Click "Create new project"**
5. **Wait for project to be ready** (usually 2-3 minutes)

### Step 2: Get Hub Database Credentials

1. **In your new hub project, go to:**
   - `Project Settings` → `API`
2. **Copy these values:**
   ```
   Project URL: https://[your-project-id].supabase.co
   anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Step 3: Set Up Hub Database Schema

1. **In the hub project, go to:**
   - `SQL Editor` → `New query`
2. **Copy and paste the entire contents of** `scripts/create-hub-database.sql`
3. **Click "Run"** to execute the script
4. **Verify success:** You should see success messages in the Results panel

### Step 4: Configure Environment Variables

**Add these to your `.env` file:**

```env
# Hub Database (NEW)
HUB_SUPABASE_URL=https://[your-hub-project-id].supabase.co
HUB_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
HUB_SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Portfolio Database (EXISTING - rename for clarity)
PORTFOLIO_SUPABASE_URL=https://fxgvxdmcfkcfyxvxoqzj.supabase.co
PORTFOLIO_SUPABASE_ANON_KEY=[your-existing-portfolio-key]
PORTFOLIO_SUPABASE_SERVICE_KEY=[your-existing-portfolio-service-key]

# Keep existing for backward compatibility
SUPABASE_URL=https://fxgvxdmcfkcfyxvxoqzj.supabase.co
SUPABASE_ANON_KEY=[your-existing-portfolio-key]
```

### Step 5: Install Migration Dependencies

```bash
pip install supabase python-dotenv
```

### Step 6: Run User Migration

**⚠️ Important:** This migrates your existing users to the hub database.

```bash
python scripts/migrate-users-to-hub.py
```

**The script will:**
- Connect to both databases
- Show you a summary of users to migrate
- Ask for confirmation
- Migrate all users safely
- Create initial usage statistics
- Verify the migration

### Step 7: Verify Hub Database Setup

1. **Check the hub database in Supabase:**
   - Go to `Table Editor`
   - You should see these tables:
     - ✅ `users` (with your migrated users)
     - ✅ `agents` (with portfolio agent registered)
     - ✅ `user_sessions` (empty for now)
     - ✅ `user_agent_stats` (with initial stats)

2. **Verify agent registration:**
   ```sql
   SELECT name, slug, description FROM agents;
   ```
   Should show: `Portfolio Management Agent` with slug `portfolio-agent`

3. **Verify user migration:**
   ```sql
   SELECT COUNT(*) as user_count FROM users;
   ```
   Should match your portfolio database user count (5 users)

## 🔧 Testing the Setup

### Test 1: Hub Service Connection

```bash
cd services/hub/backend
pip install -r requirements.txt
python main.py
```

**Expected:** Server starts on port 8001 with no errors

### Test 2: Hub API Endpoints

With the hub service running, test these endpoints:

```bash
# Health check
curl http://localhost:8001/health

# Hub status
curl http://localhost:8001/api/hub/status

# Available agents
curl http://localhost:8001/api/hub/agents
```

**Expected:** All endpoints return JSON responses without errors

### Test 3: Database Manager

```bash
cd ../../  # Back to project root
python -c "
import sys
sys.path.append('shared')
from database_manager import db_manager
print('Hub configured:', db_manager.is_hub_configured())
print('Portfolio configured:', db_manager.is_portfolio_configured())
print('Test connections:', db_manager.test_connections())
"
```

**Expected:**
```
Hub configured: True
Portfolio configured: True
Test connections: {'hub': 'connected', 'portfolio': 'connected'}
```

## 🎉 Success Verification

If all tests pass, you should have:

- ✅ **Hub database** set up with proper schema
- ✅ **Users migrated** from portfolio to hub database  
- ✅ **Portfolio agent registered** in agent registry
- ✅ **Multi-database manager** working correctly
- ✅ **Hub API service** running and responding

## 🔄 Next Steps

Now that your hub database is set up:

1. **Deploy hub service** to Railway
2. **Update portfolio service** to use hub for authentication
3. **Test end-to-end flow** with existing users
4. **Set up domain routing** for professional URLs

## 🛠️ Troubleshooting

### Issue: "Hub database credentials not found"
**Solution:** Double-check your `.env` file has `HUB_SUPABASE_URL` and `HUB_SUPABASE_ANON_KEY`

### Issue: "Permission denied" during migration
**Solution:** Ensure you're using the service_role key in the migration script for write operations

### Issue: Migration shows "0 users found"
**Solution:** Check your portfolio database credentials in `.env` - they should still work

### Issue: "Portfolio agent not found" during stats creation
**Solution:** Re-run the `create-hub-database.sql` script to ensure the agent was inserted

### Issue: Hub service won't start
**Solutions:**
- Check Python dependencies: `pip install -r services/hub/backend/requirements.txt`
- Verify environment variables are set
- Check for port conflicts (hub uses 8001 by default)

## 📞 Need Help?

If you encounter issues:

1. **Check the logs** - errors usually indicate missing environment variables
2. **Verify database connections** using the test script above
3. **Ensure both databases are accessible** from your network
4. **Check Supabase project status** in the dashboard

Your **portfolio functionality remains completely unchanged** throughout this process! 🛡️ 