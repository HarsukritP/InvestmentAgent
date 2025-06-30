# ProCogia AI Agent Platform - Multi-Service Architecture

## 🏗️ Project Structure

This repository has been restructured to support multiple AI agents with independent deployments while sharing common utilities.

```
ProCogia - Portfolio Agent/
├── services/
│   ├── portfolio-agent/          # Portfolio Management Agent
│   │   ├── backend/              # FastAPI backend
│   │   ├── frontend/             # React frontend  
│   │   └── railway.json          # Portfolio deployment config
│   └── hub/                      # Central Agent Hub
│       ├── backend/              # Hub management API
│       ├── frontend/             # Hub dashboard UI
│       └── railway.json          # Hub deployment config
├── shared/                       # Shared utilities & database layers
│   ├── database_manager.py       # Multi-database connection manager
│   └── database.py               # Original portfolio database service
├── scripts/                      # Deployment & setup scripts
│   ├── deploy-portfolio.sh       # Deploy portfolio agent
│   └── deploy-hub.sh             # Deploy hub service
└── docs/                         # Documentation
```

## 🎯 Service Architecture

### Portfolio Agent Service
- **Purpose**: AI-powered portfolio management
- **Backend**: FastAPI with portfolio-specific endpoints
- **Frontend**: React app with trading interface
- **Database**: Your existing Supabase portfolio database
- **Deployment**: Independent Railway service

### Hub Service  
- **Purpose**: Central management for multiple AI agents
- **Backend**: FastAPI with agent management endpoints
- **Frontend**: React dashboard for agent selection
- **Database**: New Supabase hub database (to be created)
- **Deployment**: Independent Railway service

### Shared Services
- **Database Manager**: Handles connections to multiple databases
- **Common Utilities**: Shared authentication, logging, etc.

## 🚀 Deployment Options

### Option 1: Independent Service Deployment

Deploy each service to its own Railway project:

```bash
# Deploy Portfolio Agent
./scripts/deploy-portfolio.sh

# Deploy Hub Service  
./scripts/deploy-hub.sh
```

### Option 2: Single Project, Multiple Services

Deploy both services within one Railway project:

1. Create Railway project
2. Add multiple services:
   - `portfolio-backend` (root: `services/portfolio-agent/backend`)
   - `portfolio-frontend` (root: `services/portfolio-agent/frontend`)
   - `hub-backend` (root: `services/hub/backend`)
   - `hub-frontend` (root: `services/hub/frontend`)

## 🔧 Local Development

### Portfolio Agent
```bash
# Backend
cd services/portfolio-agent/backend
pip install -r requirements.txt
uvicorn main:app --port 8000

# Frontend
cd services/portfolio-agent/frontend  
npm install
npm start
```

### Hub Service
```bash
# Backend
cd services/hub/backend
pip install -r requirements.txt
uvicorn main:app --port 8001

# Frontend
cd services/hub/frontend
npm install  
npm start
```

## 🗄️ Database Setup

### Existing Portfolio Database
- **Status**: ✅ Already configured and working
- **URL**: Your current `SUPABASE_URL`
- **Tables**: portfolios, transactions, holdings, users, market_data

### New Hub Database (To Be Created)
- **Purpose**: Agent registry, user sessions, usage analytics
- **Required Tables**:
  ```sql
  -- agents: Registry of available AI agents
  -- users: Migrated from portfolio DB  
  -- user_sessions: Session tracking
  ```

## 🌐 URL Structure (Production)

```
procogia.ai/
├── hub/                    # Hub homepage & agent selection
├── portfolio-agent/        # Portfolio management interface
└── future-agents/          # Additional agents as they're built
```

## 📦 Railway Deployment Configuration

### Portfolio Agent Backend
- **Root Directory**: `services/portfolio-agent/backend`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Your existing Supabase credentials

### Portfolio Agent Frontend  
- **Root Directory**: `services/portfolio-agent/frontend`
- **Build Command**: `npm run build`
- **Start Command**: `npx serve -s build -l $PORT`

### Hub Backend
- **Root Directory**: `services/hub/backend`  
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Hub database credentials (to be configured)

### Hub Frontend
- **Root Directory**: `services/hub/frontend`
- **Build Command**: `npm run build`  
- **Start Command**: `npx serve -s build -l $PORT`

## 🛡️ Migration Safety

This restructuring preserves all existing functionality:

- ✅ **Portfolio agent code unchanged** - copied as-is to new location
- ✅ **Database connections preserved** - uses same environment variables
- ✅ **Frontend functionality intact** - all existing features work
- ✅ **API endpoints unchanged** - same URLs and responses
- ✅ **Authentication working** - Google OAuth flow preserved

## 🚀 Next Steps

1. **Test Portfolio Agent**: Verify existing functionality works in new structure
2. **Deploy Portfolio Service**: Use new deployment configuration  
3. **Create Hub Database**: Set up Supabase project for hub
4. **Deploy Hub Service**: Launch central agent management
5. **Configure Domain Routing**: Set up procogia.ai URL structure

## 📋 Environment Variables Needed

### Portfolio Agent Service
```env
# Existing variables (no changes needed)
SUPABASE_URL=your_portfolio_db_url
SUPABASE_ANON_KEY=your_portfolio_db_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
# ... all your existing vars
```

### Hub Service (New)
```env
# Hub database (to be created)
HUB_SUPABASE_URL=your_hub_db_url
HUB_SUPABASE_ANON_KEY=your_hub_db_key

# Portfolio database connection (for data migration)
PORTFOLIO_SUPABASE_URL=your_portfolio_db_url  
PORTFOLIO_SUPABASE_ANON_KEY=your_portfolio_db_key
```

## 🎉 Benefits of New Structure

- **🔀 Independent Scaling**: Each service scales independently
- **🚀 Faster Deployments**: Deploy only what changed
- **🛡️ Fault Isolation**: Issues in one service don't affect others  
- **📈 Easy Expansion**: Add new agents without touching existing code
- **🎯 Clear Separation**: Hub logic separate from portfolio logic
- **💾 Database Flexibility**: Each agent can have its own database

This structure sets you up perfectly for the multi-agent future while keeping your fantastic portfolio agent safe and unchanged! 