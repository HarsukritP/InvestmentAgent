# Service Isolation Fixes

## Overview
Fixed critical service isolation issues where services were trying to access files outside their deployment directories. Railway (and other deployment platforms) deploy each service from its isolated directory, so cross-directory dependencies break deployment.

## Issues Fixed

### 1. Hub Backend Service (`services/hub/backend/`)
**Problem**: 
- `main.py` was trying to import from `../../../../shared/` directory
- `hub/hub_api.py` was using complex path manipulation to access shared files
- `hub/hub_database.py` was attempting to import from project root

**Solution**:
- Removed external path dependencies
- Created self-contained `database_manager.py` specifically for hub service
- Added proper fallback implementations
- Updated all imports to use local files only

### 2. Portfolio Agent Service (`services/portfolio-agent/backend/`)
**Problem**:
- `main.py` was trying to import from `../../../shared/` directory
- Service would fail during deployment due to missing shared directory

**Solution**:
- Removed external shared directory imports
- Created portfolio-specific `database_manager.py` 
- Added setup script to ensure proper initialization

### 3. Frontend Services
**Status**: ✅ Already properly isolated
- Hub frontend (`services/hub/frontend/`) - No external dependencies
- Portfolio frontend (`services/portfolio-agent/frontend/`) - No external dependencies

## Files Modified

### Hub Backend
- `services/hub/backend/main.py` - Removed shared directory imports
- `services/hub/backend/hub/hub_api.py` - Removed complex path imports
- `services/hub/backend/hub/hub_database.py` - Removed external imports
- `services/hub/backend/database_manager.py` - Created hub-specific implementation
- `services/hub/backend/setup.sh` - Enhanced with proper fallbacks

### Portfolio Agent Backend
- `services/portfolio-agent/backend/main.py` - Removed shared directory imports
- `services/portfolio-agent/backend/database_manager.py` - Created portfolio-specific implementation
- `services/portfolio-agent/backend/setup.sh` - Created new setup script

### Deployment Scripts
- `scripts/deploy-hub-services-individually.sh` - Added setup script execution
- `scripts/deploy-portfolio-services-individually.sh` - Created new deployment script

## Key Principles Applied

### 1. Service Isolation
- Each service directory is completely self-contained
- No imports from parent or sibling directories
- All dependencies either local or from npm/pip packages

### 2. Deployment Safety
- Services can be deployed from their isolated directories
- Setup scripts handle any required file preparation
- Graceful fallbacks for missing dependencies

### 3. Database Management
- Each service has its own database manager implementation
- Hub service: `HubDatabaseManager` focused on hub operations
- Portfolio service: `PortfolioDatabaseManager` focused on portfolio operations
- Both support integration when hub database is available

## Deployment Process

### Hub Services
```bash
# Deploy hub services
./scripts/deploy-hub-services-individually.sh
```

### Portfolio Agent Services  
```bash
# Deploy portfolio agent services
./scripts/deploy-portfolio-services-individually.sh
```

### Setup Script Execution
Each deployment automatically runs setup scripts if present:
- `services/hub/backend/setup.sh`
- `services/portfolio-agent/backend/setup.sh`

## Testing Service Isolation

To verify services are properly isolated, you can test by:

1. **Navigate to service directory**: `cd services/hub/backend`
2. **Run locally**: `python main.py` 
3. **Check imports**: Should not fail due to missing external files
4. **Verify database manager**: Should create local fallback if shared files missing

## Benefits

✅ **Clean Deployments**: Each service deploys independently  
✅ **No Cross-Dependencies**: Services don't break if other services change  
✅ **Railway Compatible**: Works with Railway's directory-based deployment  
✅ **Local Development**: Still works for local development and testing  
✅ **Graceful Degradation**: Services work even without hub integration initially

## Migration Notes

- Existing environment variables still work
- Database connections remain the same
- API endpoints unchanged
- Only internal import structure modified
- No breaking changes to external interfaces 