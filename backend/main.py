"""
AI Portfolio Agent - FastAPI backend with OAuth authentication and database integration
"""
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Cookie, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Import services
from portfolio import PortfolioManager
from market_data import MarketDataService
from ai_agent import AIPortfolioAgent
from auth import AuthenticationService
from market_context import MarketContextService
import database

# Import monitoring services
from email_service import email_service
from monitoring_service import MonitoringService
from scheduler import MonitoringScheduler, ActionScheduler

# Create FastAPI app
app = FastAPI(
    title="AI Portfolio Agent",
    description="ProCogia's AI-powered portfolio management platform with database integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local React app URL
        "https://portfolioagent.procogia.ai",  # Custom domain
        "https://www.portfolioagent.procogia.ai",  # Custom domain with www
        "http://portfolioagent.procogia.ai",  # Custom domain (HTTP)
        "http://www.portfolioagent.procogia.ai",  # Custom domain with www (HTTP)
        "https://portfolioagent-procogia-ai.up.railway.app",  # Railway frontend URL
        "https://portfolioagent-procogia-ai-service.up.railway.app",  # Railway frontend service URL
        "https://portfolioagent-backend-production.up.railway.app",  # Backend URL
        "https://procogia-aihub.up.railway.app",  # AIHub URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

# Initialize services
market_service = MarketDataService()
portfolio_manager = PortfolioManager()
auth_service = AuthenticationService()
db_service = database.db_service
market_context_service = MarketContextService(db_service)
ai_agent = AIPortfolioAgent(portfolio_manager, market_service, market_context_service, db_service)

# Initialize monitoring services
monitoring_service = MonitoringService(
    db_service=db_service,
    market_service=market_service,
    ai_agent=ai_agent,
    auth_service=auth_service,
    market_context_service=market_context_service
)
monitoring_scheduler = MonitoringScheduler(monitoring_service, email_service)
action_scheduler = ActionScheduler(db_service, market_service, portfolio_manager)

# Security
security = HTTPBearer(auto_error=False)

# Startup and shutdown events for monitoring
@app.on_event("startup")
async def startup_event():
    """Initialize monitoring system on startup"""
    logger.info("Starting Investment Agent with monitoring system")
    
    # Start the monitoring scheduler
    monitoring_scheduler.start_monitoring()
    # Start actions evaluator
    action_scheduler.start()
    
    # Log startup information
    scheduler_status = monitoring_scheduler.get_scheduler_status()
    logger.info(f"Monitoring system initialized - Enabled: {scheduler_status['enabled']}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup monitoring system on shutdown"""
    logger.info("Shutting down Investment Agent monitoring system")
    
    # Stop the monitoring scheduler
    monitoring_scheduler.stop_monitoring()
    # Stop actions scheduler
    action_scheduler.stop()
    
    logger.info("Monitoring system shutdown complete")

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    function_called: Optional[str] = None
    function_response: Optional[Dict[str, Any]] = None
    all_function_calls: Optional[List[Dict[str, Any]]] = None

class TradeRequest(BaseModel):
    symbol: str
    shares: float
    action: str  # 'buy' or 'sell'

class TradeResponse(BaseModel):
    success: bool
    message: str
    transaction: Optional[Dict[str, Any]] = None
    new_cash_balance: Optional[float] = None

class ActionCreateRequest(BaseModel):
    action_type: str
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    amount_usd: Optional[float] = None
    trigger_type: str
    trigger_params: Dict[str, Any]
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    max_executions: Optional[int] = 1
    cooldown_seconds: Optional[int] = None
    notes: Optional[str] = None

class ActionUpdateRequest(BaseModel):
    status: Optional[str] = None
    action_type: Optional[str] = None
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    amount_usd: Optional[float] = None
    trigger_type: Optional[str] = None
    trigger_params: Optional[Dict[str, Any]] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    max_executions: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    notes: Optional[str] = None

class BuyStockRequest(BaseModel):
    symbol: str
    quantity: float

class TransactionUpdateRequest(BaseModel):
    notes: Optional[str] = None
    symbol: Optional[str] = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current authenticated user from JWT token"""
    if not credentials:
        return None
    
    token = credentials.credentials
    user = auth_service.get_user_from_token(token)
    return user

async def require_auth(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authentication - raises 401 if not authenticated"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Portfolio Agent API",
        "version": "2.0.0",
        "description": "ProCogia's AI-powered portfolio management platform with database integration",
        "endpoints": {
            "portfolio": "/portfolio",
            "portfolios": "/portfolios",
            "trade": "/trade",
            "transactions": "/transactions",
            "search_stocks": "/search-stocks?query={search_term}",
            "stock_price": "/stock-price/{symbol}",
            "chat": "/chat",
            "health": "/health",
            "auth": {
                "login": "/auth/login",
                "callback": "/auth/callback",
                "logout": "/auth/logout",
                "me": "/auth/me"
            },
            "monitoring": {
                "status": "/monitoring/status",
                "trigger_check": "/monitoring/trigger-check",
                "reset_failures": "/monitoring/reset-failures", 
                "test_email": "/monitoring/test-email",
                "test_email_public": "/monitoring/test-email-public"
            },
            "market": {
                "refresh_status": "/market/refresh-status"
            }
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 errors"""
    return {"message": "No favicon configured"}

# Authentication Endpoints
@app.get("/auth/login")
async def login(request: Request):
    """Initiate OAuth login (Auth0)."""
    # Determine backend base URL
    base_url = "https://portfolioagent-procogia-ai-service.up.railway.app"
    if "localhost" in request.headers.get("origin", ""):
        base_url = "http://localhost:8000"

    redirect_uri = f"{base_url}/auth/callback"

    # Prefer Auth0 if configured, else fall back to Google (for safety during cutover)
    oauth_url = None
    try:
        if auth_service.auth0_domain and auth_service.auth0_client_id:
            oauth_url = auth_service.get_auth0_oauth_url(redirect_uri)
        elif auth_service.google_client_id:
            oauth_url = auth_service.get_google_oauth_url(redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth not configured: {e}")

    if not oauth_url:
        raise HTTPException(status_code=500, detail="OAuth not configured")

    return {"oauth_url": oauth_url}

@app.get("/auth/callback")
async def auth_callback(code: str, state: Optional[str] = None, request: Request = None):
    """Handle OAuth callback (Auth0 preferred, Google fallback)."""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    base_url = "https://portfolioagent-procogia-ai-service.up.railway.app"
    if request and "localhost" in request.headers.get("origin", ""):
        base_url = "http://localhost:8000"
    redirect_uri = f"{base_url}/auth/callback"

    # Try Auth0 first
    token_data = None
    user_info = None
    if auth_service.auth0_domain and auth_service.auth0_client_id:
        token_data = auth_service.exchange_code_for_token_auth0(code, redirect_uri)
        if token_data and token_data.get("id_token"):
            user_info = auth_service.verify_auth0_id_token(token_data.get("id_token"))
    # Fallback to Google during transition
    if not user_info and auth_service.google_client_id:
        token_data = auth_service.exchange_code_for_token(code, redirect_uri)
        if token_data and token_data.get("id_token"):
            user_info = auth_service.verify_google_token(token_data.get("id_token"))

    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid token")
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Create or get user in database - NO FALLBACK
    db_user = await db_service.create_or_get_user(
        google_id=user_info['sub'],
        email=user_info['email'],
        name=user_info['name'],
        picture_url=user_info.get('picture')
    )
    
    # Add database user ID to user info for JWT
    user_info['db_user_id'] = db_user['id']
    
    # Create JWT token
    jwt_token = auth_service.create_jwt_token(user_info)
    
    # Always redirect to the custom domain if available, otherwise fallback to Railway
    frontend_base_url = "https://portfolioagent.procogia.ai"
    
    # Use localhost for local development
    if request and "localhost" in request.headers.get("origin", ""):
        frontend_base_url = "http://localhost:3000"
    
    frontend_url = f"{frontend_base_url}/auth/success?token={jwt_token}"
    return RedirectResponse(url=frontend_url)

@app.post("/auth/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}

@app.get("/auth/me")
async def get_current_user_info(user: Dict[str, Any] = Depends(require_auth)):
    """Get current user information"""
    return {
        "user": user,
        "authenticated": True
    }

# Portfolio endpoints
@app.get("/portfolios")
async def get_user_portfolios(user: Dict[str, Any] = Depends(require_auth)):
    """Get all portfolios for the current user"""
    try:
        user_id = user.get('db_user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User not found in database")
        
        portfolios = await db_service.get_user_portfolios(user_id)
        return {"portfolios": portfolios}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolios: {str(e)}")

@app.get("/portfolio")
async def get_portfolio(portfolio_id: Optional[str] = None, user: Dict[str, Any] = Depends(require_auth)):
    """Get user portfolio with current market data"""
    try:
        user_id = user.get('db_user_id')
        
        if not user_id:
            # Create or get user in database
            db_user = await db_service.create_or_get_user(
                google_id=user.get('sub'),
                email=user.get('email'),
                name=user.get('name'),
                picture_url=user.get('picture')
            )
            user_id = db_user['id']
        
        # Get user's portfolio
        portfolios = await db_service.get_user_portfolios(user_id)
        
        if not portfolios:
            # Create default portfolio
            portfolio = await db_service.create_portfolio(user_id, "My Portfolio")
            holdings = []
        else:
            # Use first portfolio if portfolio_id not specified
            if not portfolio_id:
                portfolio = portfolios[0]
            else:
                portfolio = next((p for p in portfolios if p['id'] == portfolio_id), None)
                
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            # Get portfolio holdings
            holdings = await db_service.get_portfolio_holdings(portfolio['id'])
        
        # Get current market data for holdings
        if holdings:
            symbols = [h['symbol'] for h in holdings]
            
            # Add symbols to auto-refresh watchlist
            market_service.add_to_watchlist(symbols)
            
            # Get current market quotes
            market_quotes = await market_service.get_portfolio_quotes(symbols)
            
            # Calculate total portfolio value
            total_value = 0
            
            # Update holdings with current market data
            for holding in holdings:
                symbol = holding['symbol']
                shares = holding['shares']
                
                # Get current price from market data
                quote = market_quotes.get(symbol.upper(), {})
                current_price = quote.get('price', holding['average_cost'])
                
                # Calculate market value and profit/loss
                market_value = shares * current_price
                cost_basis = shares * holding['average_cost']
                profit_loss = market_value - cost_basis
                profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                # Add to total portfolio value
                total_value += market_value
                
                # Update holding with current market data
                holding.update({
                    'current_price': current_price,
                    'market_value': market_value,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent,
                    'last_updated': datetime.now().isoformat()
                })
        else:
            total_value = 0
        
        # Update portfolio with total value
        portfolio['total_market_value'] = total_value
        portfolio['total_account_value'] = total_value + portfolio['cash_balance']
        
        return {
            "status": "success",
            "portfolio": portfolio,
            "holdings": holdings
        }
    
    except Exception as e:
        print(f"Error getting portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trade", response_model=TradeResponse)
async def execute_trade(
    trade_request: TradeRequest,
    portfolio_id: Optional[str] = None,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Execute a buy or sell trade"""
    try:
        user_id = user.get('db_user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User not found in database")
        
        # Get user's portfolio
        if not portfolio_id:
            portfolios = await db_service.get_user_portfolios(user_id)
            if not portfolios:
                raise HTTPException(status_code=404, detail="No portfolios found")
            portfolio_id = portfolios[0]['id']
        
        # Get current stock price
        try:
            price_data = await market_service.get_stock_quote(trade_request.symbol)
            current_price = price_data.get('price')
            if not current_price:
                raise HTTPException(status_code=400, detail=f"Could not get price for {trade_request.symbol}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error getting stock price: {str(e)}")
        
        # Execute trade
        if trade_request.action.lower() == 'buy':
            result = await db_service.execute_buy_order(
                portfolio_id, user_id, trade_request.symbol, 
                trade_request.shares, current_price
            )
        elif trade_request.action.lower() == 'sell':
            result = await db_service.execute_sell_order(
                portfolio_id, user_id, trade_request.symbol, 
                trade_request.shares, current_price
            )
        else:
            raise HTTPException(status_code=400, detail="Action must be 'buy' or 'sell'")
        
        return TradeResponse(
            success=True,
            message=f"Successfully {trade_request.action}ed {trade_request.shares} shares of {trade_request.symbol}",
            transaction=result['transaction'],
            new_cash_balance=result['new_cash_balance']
        )
        
    except ValueError as e:
        return TradeResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")

@app.get("/transactions")
async def get_transactions(user: Dict[str, Any] = Depends(get_current_user)):
    """Get transactions for a user"""
    try:
        user_id = user.get('db_user_id')
        
        if not user_id:
            # Create or get user in database
            db_user = await db_service.create_or_get_user(
                google_id=user.get('sub'),
                email=user.get('email'),
                name=user.get('name'),
                picture_url=user.get('picture')
            )
            user_id = db_user['id']
        
        # Get user's portfolio
        portfolios = await db_service.get_user_portfolios(user_id)
        
        if not portfolios:
            return {
                "status": "success",
                "data": [],
                "count": 0,
                "message": "No portfolios found"
            }
        
        portfolio = portfolios[0]  # Use first portfolio
        portfolio_id = portfolio['id']
        
        # Get transactions directly from the database
        transactions = db_service.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).execute()
        
        return {
            "status": "success",
            "data": transactions.data,
            "count": len(transactions.data),
            "portfolio_id": portfolio_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Actions Automation Endpoints
@app.get("/actions")
async def list_actions(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    action_type: Optional[str] = None,
    trigger_type: Optional[str] = None,
    user: Dict[str, Any] = Depends(require_auth)
):
    try:
        user_id = user.get('db_user_id')
        if not user_id:
            # Fallback: ensure DB user exists (mirrors other endpoints)
            db_user = await db_service.create_or_get_user(
                google_id=user.get('sub'),
                email=user.get('email'),
                name=user.get('name'),
                picture_url=user.get('picture')
            )
            user_id = db_user['id']
        filters = {k: v for k, v in {
            'status': status,
            'symbol': symbol.upper() if symbol else None,
            'action_type': action_type,
            'trigger_type': trigger_type
        }.items() if v is not None}
        actions = await db_service.get_actions(user_id, filters)
        return {"actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing actions: {str(e)}")

@app.post("/actions")
async def create_action(
    payload: ActionCreateRequest,
    user: Dict[str, Any] = Depends(require_auth)
):
    try:
        user_id = user.get('db_user_id')
        if not user_id:
            # Fallback: ensure DB user exists
            db_user = await db_service.create_or_get_user(
                google_id=user.get('sub'),
                email=user.get('email'),
                name=user.get('name'),
                picture_url=user.get('picture')
            )
            user_id = db_user['id']
        # Basic validation
        action_type_upper = payload.action_type.upper()
        trigger_type = payload.trigger_type

        if action_type_upper in ["BUY", "SELL"] and not (payload.quantity or payload.amount_usd):
            raise HTTPException(status_code=400, detail="BUY/SELL requires quantity or amount (USD)")
        if action_type_upper in ["BUY", "SELL"] and not (payload.symbol and payload.symbol.strip()):
            raise HTTPException(status_code=400, detail="Symbol is required for BUY/SELL actions")
        if payload.trigger_type not in ["price_above", "price_below", "change_pct", "time_of_day"]:
            raise HTTPException(status_code=400, detail="Unsupported trigger_type")

        # Trigger param validation
        if trigger_type in ["price_above", "price_below"]:
            threshold = (payload.trigger_params or {}).get('threshold')
            try:
                threshold = float(threshold)
            except Exception:
                threshold = None
            if threshold is None:
                raise HTTPException(status_code=400, detail="threshold is required for price triggers")
        if trigger_type == "change_pct":
            change = (payload.trigger_params or {}).get('change')
            try:
                change = float(change)
            except Exception:
                change = None
            if change is None:
                raise HTTPException(status_code=400, detail="change is required for change_pct trigger")

        action_data = {
            'user_id': user_id,
            'status': 'active',
            'action_type': action_type_upper,
            'symbol': payload.symbol.upper() if payload.symbol else None,
            'quantity': payload.quantity,
            'amount_usd': payload.amount_usd,
            'trigger_type': payload.trigger_type,
            'trigger_params': payload.trigger_params,
            'valid_from': payload.valid_from,
            'valid_until': payload.valid_until,
            'max_executions': payload.max_executions or 1,
            'cooldown_seconds': payload.cooldown_seconds,
            'notes': payload.notes
        }
        created = await db_service.create_action(action_data)
        # Add to watchlist if symbol
        if created.get('symbol'):
            market_service.add_to_watchlist([created['symbol']])
        return created
    except HTTPException:
        raise
    except Exception as e:
        # Log full traceback and structured error for Supabase APIError
        import traceback
        logger.error("Create action error: %s", e)
        logger.error("Payload caused error: %s", action_data)
        logger.error("Traceback: %s", traceback.format_exc())
        # Try to expose more useful message
        err_msg = getattr(e, 'message', None) or getattr(e, 'detail', None) or str(e) or type(e).__name__
        hint = getattr(e, 'hint', None)
        details = getattr(e, 'details', None)
        composed = err_msg
        if details:
            composed += f" | details: {details}"
        if hint:
            composed += f" | hint: {hint}"
        raise HTTPException(status_code=500, detail=f"Error creating action: {composed}")

@app.get("/actions/{action_id}")
async def get_action(action_id: str, user: Dict[str, Any] = Depends(require_auth)):
    action = await db_service.get_action_by_id(action_id, user.get('db_user_id'))
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action

@app.patch("/actions/{action_id}")
async def update_action(action_id: str, payload: ActionUpdateRequest, user: Dict[str, Any] = Depends(require_auth)):
    updated = await db_service.update_action(action_id, user.get('db_user_id'), payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Action not found or nothing to update")
    return updated

@app.delete("/actions/{action_id}")
async def cancel_action(action_id: str, hard_delete: bool = False, user: Dict[str, Any] = Depends(require_auth)):
    if hard_delete:
        ok = await db_service.delete_action(action_id, user.get('db_user_id'))
    else:
        ok = await db_service.cancel_action(action_id, user.get('db_user_id'))
    if not ok:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"success": True}

@app.get("/search-stocks")
async def search_stocks(query: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Search for stocks to buy"""
    try:
        if not query or len(query.strip()) < 1:
            return {"results": [], "query": query}
        
        # Use market service to search stocks
        results = await market_service.search_stocks(query.strip())
        
        # Pre-cache price data for search results to optimize buy flow
        if results:
            symbols = [result['symbol'] for result in results[:5]]  # Cache top 5 results
            
            try:
                # Fetch and cache prices for search results
                cached_quotes = await market_service.get_portfolio_quotes(symbols)
                
                # Add price data to search results
                for result in results:
                    symbol = result['symbol'].upper()
                    if symbol in cached_quotes:
                        quote_data = cached_quotes[symbol]
                        result['current_price'] = quote_data.get('price')
                        result['change'] = quote_data.get('change')
                        result['change_percent'] = quote_data.get('change_percent')
                        result['cached'] = True
                
            except Exception:
                # Continue without caching - not critical for search functionality
                pass
        
        return {
            "results": results,
            "query": query,
            "count": len(results),
            "cached_prices": len([r for r in results if r.get('cached')]) if results else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching stocks: {str(e)}")

@app.post("/buy-stock")
async def buy_stock(
    request: BuyStockRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Buy stock - add to portfolio"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required for buying stocks")
        
    if not request.symbol or request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid symbol or quantity")
    
    symbol = request.symbol.upper()
    quantity = request.quantity
    
    # Get or create user in database
    user_id = user.get('db_user_id')
    if not user_id:
        db_user = await db_service.create_or_get_user(
            google_id=user.get('sub'),
            email=user.get('email'),
            name=user.get('name'),
            picture_url=user.get('picture')
        )
        user_id = db_user['id']
    
    # Get user's portfolio (create if doesn't exist)
    portfolios = await db_service.get_user_portfolios(user_id)
    if not portfolios:
        portfolio = await db_service.create_portfolio(
            user_id=user_id,
            name="My Portfolio",
            cash_balance=10000.0
        )
    else:
        portfolio = portfolios[0]  # Use first portfolio
    
    # Get current price
    quote_data = await market_service.get_stock_quote(symbol)
    current_price = quote_data.get("price")
    
    if not current_price or current_price <= 0:
        raise HTTPException(status_code=400, detail=f"Unable to get current price for {symbol}")
    
    # Check if user can afford it
    total_cost = current_price * quantity
    if portfolio['cash_balance'] < total_cost:
        shortfall = total_cost - portfolio['cash_balance']
        max_affordable = int(portfolio['cash_balance'] / current_price)
        return {
            "success": False,
            "error": f"Insufficient funds. Need ${total_cost:,.2f}, have ${portfolio['cash_balance']:,.2f}",
            "affordability": {
                "can_afford": False,
                "total_cost": total_cost,
                "available_cash": portfolio['cash_balance'],
                "shortfall": shortfall,
                "max_affordable_shares": max_affordable,
                "current_price": current_price
            }
        }
    
    # Execute the buy using database service
    result = await db_service.execute_buy_order(
        portfolio['id'], user_id, symbol, quantity, current_price
    )
    
    return {
        "success": True,
        "message": f"Successfully bought {quantity} shares of {symbol}",
        "transaction": result['transaction'],
        "remaining_cash": result['new_cash_balance'],
        "holding": {
            "symbol": symbol,
            "quantity": quantity,
            "purchase_price": current_price
        }
    }

@app.post("/sell-stock")
async def sell_stock(
    request: BuyStockRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Sell stock - remove from portfolio"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required for selling stocks")
        
    if not request.symbol or request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid symbol or quantity")
    
    symbol = request.symbol.upper()
    quantity = request.quantity
    
    # Get or create user in database
    user_id = user.get('db_user_id')
    if not user_id:
        db_user = await db_service.create_or_get_user(
            google_id=user.get('sub'),
            email=user.get('email'),
            name=user.get('name'),
            picture_url=user.get('picture')
        )
        user_id = db_user['id']
    
    # Get user's portfolio
    portfolios = await db_service.get_user_portfolios(user_id)
    if not portfolios:
        raise HTTPException(status_code=404, detail="No portfolio found")
    
    portfolio = portfolios[0]  # Use first portfolio
    
    # Check if user has the stock and enough shares
    holdings = await db_service.get_portfolio_holdings(portfolio['id'])
    holding = next((h for h in holdings if h['symbol'].upper() == symbol), None)
    
    if not holding:
        raise HTTPException(status_code=404, detail=f"You don't own any shares of {symbol}")
    
    if holding['shares'] < quantity:
        raise HTTPException(status_code=400, detail=f"You only have {holding['shares']} shares of {symbol}, but you're trying to sell {quantity}")
    
    # Get current price
    quote_data = await market_service.get_stock_quote(symbol)
    current_price = quote_data.get("price")
    
    if not current_price or current_price <= 0:
        raise HTTPException(status_code=400, detail=f"Unable to get current price for {symbol}")
    
    # Execute the sell using database service
    try:
        result = await db_service.execute_sell_order(
            portfolio['id'], user_id, symbol, quantity, current_price
        )
        
        return {
            "success": True,
            "message": f"Successfully sold {quantity} shares of {symbol}",
            "transaction": result['transaction'],
            "remaining_cash": result['new_cash_balance']
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing sell order: {str(e)}")

@app.get("/cash-balance")
async def get_cash_balance(user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's current cash balance"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get or create user in database
    user_id = user.get('db_user_id')
    if not user_id:
        db_user = await db_service.create_or_get_user(
            google_id=user.get('sub'),
            email=user.get('email'),
            name=user.get('name'),
            picture_url=user.get('picture')
        )
        user_id = db_user['id']
    
    # Get user's portfolio
    portfolios = await db_service.get_user_portfolios(user_id)
    if not portfolios:
        # Create default portfolio
        portfolio = await db_service.create_portfolio(
            user_id=user_id,
            name="My Portfolio",
            cash_balance=10000.0
        )
    else:
        portfolio = portfolios[0]
    
    return {
        "cash_balance": portfolio['cash_balance'],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/check-affordability/{symbol}")
async def check_affordability(
    symbol: str,
    quantity: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Check if user can afford to buy specified quantity of stock"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    symbol = symbol.upper()
    
    # Get or create user in database
    user_id = user.get('db_user_id')
    if not user_id:
        db_user = await db_service.create_or_get_user(
            google_id=user.get('sub'),
            email=user.get('email'),
            name=user.get('name'),
            picture_url=user.get('picture')
        )
        user_id = db_user['id']
    
    # Get user's portfolio
    portfolios = await db_service.get_user_portfolios(user_id)
    if not portfolios:
        # Create default portfolio
        portfolio = await db_service.create_portfolio(
            user_id=user_id,
            name="My Portfolio",
            cash_balance=10000.0
        )
    else:
        portfolio = portfolios[0]
    
    # Get current price
    quote_data = await market_service.get_stock_quote(symbol)
    current_price = quote_data.get("price")
    
    if not current_price:
        raise HTTPException(status_code=400, detail=f"Unable to get current price for {symbol}")
    
    total_cost = current_price * quantity
    can_afford = portfolio['cash_balance'] >= total_cost
    max_affordable = int(portfolio['cash_balance'] / current_price) if current_price > 0 else 0
    
    return {
        "symbol": symbol,
        "quantity": quantity,
        "current_price": current_price,
        "total_cost": total_cost,
        "available_cash": portfolio['cash_balance'],
        "can_afford": can_afford,
        "max_affordable_shares": max_affordable,
        "shortfall": max(0, total_cost - portfolio['cash_balance'])
    }

@app.get("/stock-price/{symbol}")
async def get_stock_price(symbol: str, user: Dict[str, Any] = Depends(require_auth)):
    """Get current stock price for a specific symbol"""
    try:
        if not symbol:
            raise HTTPException(status_code=400, detail="Stock symbol is required")
        
        # Get stock price using market service
        price_data = await market_service.get_stock_quote(symbol.upper())
        
        if not price_data or not price_data.get('price'):
            raise HTTPException(status_code=404, detail=f"Price data not available for {symbol}")
        
        return {
            "symbol": symbol.upper(),
            "price": price_data['price'],
            "change": price_data.get('change', 0),
            "change_percent": price_data.get('change_percent', 0),
            "timestamp": price_data.get('timestamp', datetime.now().isoformat()),
            "cached": price_data.get('cached', False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock price: {str(e)}")

# Chart and Historical Data Endpoints
@app.get("/chart/{symbol}")
async def get_chart_data(
    symbol: str,
    period: str = "6months",
    interval: str = "1day",
    user: Dict[str, Any] = Depends(require_auth)
):
    """Get historical chart data for a stock symbol"""
    try:
        symbol = symbol.upper()
        
        # Validate period parameter
        valid_periods = ["1week", "1month", "3months", "6months", "1year", "2years", "5years"]
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}")
        
        # Ensure we have sufficient historical data, backfill if needed
        data_check = await market_service.ensure_historical_data(symbol, period)
        
        # Convert period to days for database query
        period_days = {
            "1week": 7,
            "1month": 30,
            "3months": 90,
            "6months": 180,
            "1year": 365,
            "2years": 730,
            "5years": 1825
        }
        days = period_days.get(period, 180)
        
        # Get historical data from database
        historical_data = await market_service.get_historical_data(symbol, days)
        
        if not historical_data:
            raise HTTPException(status_code=404, detail=f"No historical data available for {symbol}")
        
        # Format data for charting (newest first)
        chart_data = []
        for record in reversed(historical_data):  # Reverse to get newest first
            chart_data.append({
                "date": record["timestamp"][:10],  # Extract date part (YYYY-MM-DD)
                "datetime": record["timestamp"],
                "open": record.get("open_price"),
                "high": record.get("high_price"),
                "low": record.get("low_price"),
                "close": record.get("close_price") or record.get("price"),
                "volume": record.get("volume"),
                "price": record.get("price")  # For simple line charts
            })
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(chart_data),
            "data": chart_data,
            "meta": {
                "data_source": data_check.get("action", "existing"),
                "backfill_info": data_check.get("backfill_result") if data_check.get("action") == "backfilled" else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chart data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")

@app.post("/backfill-historical/{symbol}")
async def backfill_historical_data(
    symbol: str,
    period: str = "1year",
    interval: str = "1day",
    user: Dict[str, Any] = Depends(require_auth)
):
    """Manually trigger historical data backfill for a symbol"""
    try:
        symbol = symbol.upper()
        
        # Validate parameters
        valid_periods = ["1week", "1month", "3months", "6months", "1year", "2years", "5years"]
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}")
        
        # Trigger backfill
        result = await market_service.backfill_historical_data(symbol, period, interval)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "message": f"Successfully backfilled historical data for {symbol}",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error backfilling data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error backfilling historical data: {str(e)}")

@app.get("/portfolio-charts")
async def get_portfolio_charts(user: Dict[str, Any] = Depends(require_auth)):
    """Get chart data for all holdings in user's portfolio"""
    try:
        user_id = user.get('db_user_id')
        
        if not user_id:
            # Create or get user in database
            db_user = await db_service.create_or_get_user(
                google_id=user.get('sub'),
                email=user.get('email'),
                name=user.get('name'),
                picture_url=user.get('picture')
            )
            user_id = db_user['id']
        
        # Get user's portfolio
        portfolios = await db_service.get_user_portfolios(user_id)
        if not portfolios:
            return {"charts": [], "message": "No portfolio found"}
        
        portfolio = portfolios[0]
        holdings = await db_service.get_portfolio_holdings(portfolio['id'])
        
        if not holdings:
            return {"charts": [], "message": "No holdings in portfolio"}
        
        # Get chart data for each holding
        charts = {}
        for holding in holdings:
            symbol = holding['symbol']
            try:
                # Ensure we have historical data
                await market_service.ensure_historical_data(symbol, "3months")
                
                # Get 30 days of data for portfolio overview
                historical_data = await market_service.get_historical_data(symbol, 30)
                
                if historical_data:
                    # Format for simple line chart
                    chart_data = []
                    for record in reversed(historical_data[-30:]):  # Last 30 days, newest first
                        chart_data.append({
                            "date": record["timestamp"][:10],
                            "price": record.get("close_price") or record.get("price"),
                            "change": record.get("change_amount", 0)
                        })
                    
                    charts[symbol] = {
                        "symbol": symbol,
                        "data": chart_data,
                        "data_points": len(chart_data)
                    }
                    
            except Exception as e:
                logger.warning(f"Error getting chart data for {symbol}: {str(e)}")
                continue
        
        return {
            "charts": charts,
            "symbols": list(charts.keys()),
            "total_charts": len(charts)
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio charts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio charts: {str(e)}")

@app.get("/intraday/{symbol}")
async def get_intraday_data(
    symbol: str,
    interval: str = "1h",
    outputsize: int = 24,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Get intraday data for hover charts and real-time updates"""
    try:
        symbol = symbol.upper()
        
        # Validate interval parameter
        valid_intervals = ["1min", "5min", "15min", "30min", "1h", "2h", "4h"]
        if interval not in valid_intervals:
            raise HTTPException(status_code=400, detail=f"Invalid interval. Must be one of: {', '.join(valid_intervals)}")
        
        # Get intraday data from market service
        result = await market_service.get_intraday_data(symbol, interval, outputsize)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting intraday data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching intraday data: {str(e)}")

@app.get("/stock-details/{symbol}")
async def get_stock_details(
    symbol: str,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Get comprehensive stock details for detail page"""
    try:
        symbol = symbol.upper()
        
        # Get current quote
        quote_data = await market_service.get_stock_quote(symbol)
        if not quote_data:
            raise HTTPException(status_code=404, detail=f"Stock data not available for {symbol}")
        
        # Get basic historical data for quick overview
        historical_data = await market_service.get_historical_data(symbol, 30)
        
        # Calculate additional metrics
        prices = [float(record.get("close_price") or record.get("price", 0)) for record in historical_data[-30:]]
        
        # Simple price analytics
        price_analytics = {}
        if len(prices) >= 2:
            current_price = prices[-1]
            prev_price = prices[-2] if len(prices) > 1 else prices[0]
            week_ago_price = prices[-7] if len(prices) >= 7 else prices[0]
            month_ago_price = prices[0] if len(prices) >= 30 else prices[0]
            
            price_analytics = {
                "daily_change": current_price - prev_price,
                "daily_change_percent": ((current_price - prev_price) / prev_price * 100) if prev_price else 0,
                "weekly_change": current_price - week_ago_price,
                "weekly_change_percent": ((current_price - week_ago_price) / week_ago_price * 100) if week_ago_price else 0,
                "monthly_change": current_price - month_ago_price,
                "monthly_change_percent": ((current_price - month_ago_price) / month_ago_price * 100) if month_ago_price else 0,
                "high_52w": max(prices) if prices else current_price,
                "low_52w": min(prices) if prices else current_price,
                "avg_volume": sum([record.get("volume", 0) for record in historical_data[-30:] if record.get("volume")]) / len([r for r in historical_data[-30:] if r.get("volume")]) if historical_data else None
            }
        
        return {
            "symbol": symbol,
            "quote": quote_data,
            "analytics": price_analytics,
            "data_points": len(historical_data),
            "last_updated": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock details for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock details: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatMessage,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Chat with AI agent about portfolio"""
    try:
        user_id = user.get('db_user_id')
        debug_info = {"user_id": user_id}
        
        # Set the user_id in the portfolio manager
        portfolio_manager.set_user_id(user_id)
        
        if user_id:
            # Get user's portfolio from database
            portfolios = await db_service.get_user_portfolios(user_id)
            debug_info["has_portfolios"] = bool(portfolios)
            
            if portfolios:
                portfolio = portfolios[0]  # Use first portfolio
                holdings = await db_service.get_portfolio_holdings(portfolio['id'])
                debug_info["portfolio_id"] = portfolio['id']
                debug_info["has_holdings"] = bool(holdings)
                debug_info["holdings_count"] = len(holdings) if holdings else 0
                
                # Convert to format expected by AI agent
                portfolio_data = {
                    "cash_balance": portfolio['cash_balance'],
                    "holdings": []
                }
                
                if holdings:
                    symbols = [h['symbol'] for h in holdings]
                    market_quotes = await market_service.get_portfolio_quotes(symbols)
                    debug_info["symbols"] = symbols
                    debug_info["has_quotes"] = bool(market_quotes)
                    
                    for holding in holdings:
                        symbol = holding['symbol'].upper()
                        quote_data = market_quotes.get(symbol, {})
                        current_price = quote_data.get('price', holding['average_cost'])
                        
                        portfolio_data["holdings"].append({
                            "symbol": symbol,
                            "quantity": holding['shares'],  # Map shares to quantity
                            "purchase_price": holding['average_cost'],  # Map average_cost to purchase_price
                            "current_price": current_price
                        })
                
                # Update AI agent's portfolio manager with current data
                portfolio_manager.portfolio = portfolio_data
                debug_info["portfolio_manager_updated"] = True
            else:
                # No portfolio found, use empty portfolio
                portfolio_manager.portfolio = {"cash_balance": 10000, "holdings": []}
                debug_info["using_empty_portfolio"] = True
        else:
            # Use legacy portfolio
            debug_info["using_legacy_portfolio"] = True
            pass
        
        # Get conversation history from request if provided
        conversation_history = chat_request.conversation_history if hasattr(chat_request, 'conversation_history') else None
        
        # Get AI response with conversation history
        response = await ai_agent.chat(chat_request.message, conversation_history)
        
        # Add debug info to response
        if "error" in response:
            debug_info["ai_error"] = response["error"]
        
        # Return enhanced response with function call information
        return ChatResponse(
            response=response.get("response", "Sorry, I couldn't process your request."),
            timestamp=datetime.now().isoformat(),
            function_called=response.get("function_called"),
            function_response=response.get("function_response"),
            all_function_calls=response.get("all_function_calls")
        )
        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for API status"""
    # Check database connection
    db_status = "ok"
    db_error = None
    try:
        # Attempt to query the database
        await db_service.test_connection()
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    
    # Check AI service
    ai_status = ai_agent.health_check()
    
    # Check market data service
    market_data_status = market_service.health_check()
    
    # Check market context service
    market_context_status = "ok"
    market_context_error = None
    try:
        # Check if API keys are configured
        if not os.getenv("FRED_API_KEY"):
            market_context_status = "error"
            market_context_error = "FRED_API_KEY not configured"
        elif not os.getenv("NEWS_API_KEY"):
            market_context_status = "error"
            market_context_error = "NEWS_API_KEY not configured"
    except Exception as e:
        market_context_status = "error"
        market_context_error = str(e)
    
    # Overall API status
    overall_status = "healthy"
    if db_status == "error" or ai_status.get("status") == "error" or market_data_status.get("status") != "healthy" or market_context_status == "error":
        overall_status = "degraded"
    
    # Format response to match what frontend expects
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": {
                "status": db_status,
                "error": db_error
            },
            "ai_agent": ai_status,
            "market_data": market_data_status,
            "market_context": {
                "status": market_context_status,
                "error": market_context_error
            },
            "portfolio": {"status": "healthy"},
            "auth": {"status": "healthy" if auth_service.google_client_id else "not_configured"}
        },
        "configuration": {
            "twelvedata_key_configured": bool(os.getenv("TWELVEDATA_API_KEY")),
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "oauth_configured": bool(auth_service.google_client_id and auth_service.google_client_secret),
            "supabase_configured": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY")),
            "fred_api_key_configured": bool(os.getenv("FRED_API_KEY")),
            "news_api_key_configured": bool(os.getenv("NEWS_API_KEY"))
        }
    }

@app.get("/market-news")
async def get_market_news(user: Dict[str, Any] = Depends(require_auth)):
    """Get market news for dashboard"""
    try:
        # Import market context service
        from market_context import MarketContextService
        
        # Initialize market context service
        market_context = MarketContextService()
        
        # Fetch general market news
        news_data = await market_context.get_market_news()
        
        return {
            "general_news": news_data.get("general_news", []),
            "timestamp": news_data.get("_timestamp"),
            "source": news_data.get("_source", "News API")
        }
        
    except Exception as e:
        logger.error(f"Error fetching market news: {str(e)}")
        # Return empty news instead of error to not break dashboard
        return {
            "general_news": [],
            "timestamp": datetime.now().isoformat(),
            "source": "Error",
            "error": str(e)
        }

@app.get("/cache/stats")
async def get_cache_statistics(user: Dict[str, Any] = Depends(require_auth)):
    """Get comprehensive cache statistics including intraday cache"""
    try:
        # Get general cache stats
        general_stats = await market_service.get_cache_stats()
        
        # Get intraday-specific cache stats
        intraday_stats = await market_service.get_intraday_cache_stats()
        
        return {
            "general_cache": general_stats,
            "intraday_cache": intraday_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving cache statistics: {str(e)}")

@app.post("/cache/cleanup")
async def cleanup_old_cache(
    max_age_hours: int = 24,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Clean up old cache entries to free space and improve performance"""
    try:
        if max_age_hours < 1 or max_age_hours > 168:  # 1 hour to 1 week
            raise HTTPException(status_code=400, detail="max_age_hours must be between 1 and 168")
        
        # Clean up old intraday cache entries
        cleanup_result = await market_service.cleanup_old_intraday_cache(max_age_hours)
        
        if "error" in cleanup_result:
            raise HTTPException(status_code=500, detail=cleanup_result["error"])
        
        return {
            "message": "Cache cleanup completed successfully",
            "result": cleanup_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during cache cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during cache cleanup: {str(e)}")

@app.get("/cache/intraday/stats")
async def get_intraday_cache_stats(user: Dict[str, Any] = Depends(require_auth)):
    """Get detailed statistics about intraday data caching"""
    try:
        stats = await market_service.get_intraday_cache_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return {
            "intraday_cache_stats": stats,
            "cache_policy": {
                "cache_duration_1min": "5 minutes",
                "cache_duration_5min": "5 minutes", 
                "cache_duration_15min": "15 minutes",
                "cache_duration_30min": "15 minutes",
                "cache_duration_1h": "30 minutes",
                "cache_duration_2h": "30 minutes",
                "cache_duration_default": "60 minutes"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting intraday cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving intraday cache statistics: {str(e)}")

@app.get("/transaction-stats")
async def get_transaction_stats(user: Dict[str, Any] = Depends(get_current_user)):
    """Get transaction statistics for a user's portfolio"""
    try:
        user_id = user.get('db_user_id')
        
        if not user_id:
            # Create or get user in database
            db_user = await db_service.create_or_get_user(
                google_id=user.get('sub'),
                email=user.get('email'),
                name=user.get('name'),
                picture_url=user.get('picture')
            )
            user_id = db_user['id']
        
        # Get user's portfolio
        portfolios = await db_service.get_user_portfolios(user_id)
        
        if not portfolios:
            return {
                "status": "success",
                "transaction_count": 0,
                "buy_count": 0,
                "sell_count": 0,
                "total_buy_amount": 0,
                "total_sell_amount": 0,
                "most_traded_symbol": "N/A"
            }
        
        portfolio = portfolios[0]  # Use first portfolio
        portfolio_id = portfolio['id']
        
        # Try to use the stored function first
        try:
            stats = db_service.supabase.rpc('get_transaction_stats', {'p_portfolio_id': portfolio_id}).execute()
            
            # If the function worked, return its data
            if stats.data:
                return {
                    "status": "success",
                    "portfolio_id": portfolio_id,
                    "transaction_count": stats.data.get('transaction_count', 0),
                    "buy_count": stats.data.get('buy_count', 0),
                    "sell_count": stats.data.get('sell_count', 0),
                    "total_buy_amount": stats.data.get('total_buy_amount', 0),
                    "total_sell_amount": stats.data.get('total_sell_amount', 0),
                    "most_traded_symbol": stats.data.get('most_traded_symbol', 'N/A')
                }
        except Exception:
            # Continue to fallback method
            pass
        
        # Fallback: Calculate stats manually
        transactions = db_service.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).execute().data
        
        # Calculate stats manually
        buy_transactions = [t for t in transactions if t.get('transaction_type') == 'BUY']
        sell_transactions = [t for t in transactions if t.get('transaction_type') == 'SELL']
        
        total_buy_amount = sum(t.get('total_amount', 0) for t in buy_transactions)
        total_sell_amount = sum(t.get('total_amount', 0) for t in sell_transactions)
        
        # Calculate most traded symbol
        symbol_counts = {}
        for t in transactions:
            symbol = t.get('symbol')
            if symbol:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        most_traded_symbol = 'N/A'
        max_count = 0
        for symbol, count in symbol_counts.items():
            if count > max_count:
                max_count = count
                most_traded_symbol = symbol
        
        return {
            "status": "success",
            "portfolio_id": portfolio_id,
            "transaction_count": len(transactions),
            "buy_count": len(buy_transactions),
            "sell_count": len(sell_transactions),
            "total_buy_amount": total_buy_amount,
            "total_sell_amount": total_sell_amount,
            "most_traded_symbol": most_traded_symbol if symbol_counts else 'N/A'
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Monitoring Management Endpoints
@app.get("/monitoring/status")
async def get_monitoring_status(user: Dict[str, Any] = Depends(require_auth)):
    """Get monitoring system status and statistics"""
    try:
        scheduler_status = monitoring_scheduler.get_scheduler_status()
        monitoring_stats = monitoring_service.get_monitoring_stats()
        email_health = email_service.health_check()
        
        return {
            "monitoring_system": {
                "scheduler": scheduler_status,
                "monitoring_service": monitoring_stats,
                "email_service": email_health
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting monitoring status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving monitoring status: {str(e)}")

@app.post("/monitoring/trigger-check")
async def trigger_immediate_monitoring_check(user: Dict[str, Any] = Depends(require_auth)):
    """Trigger an immediate monitoring check and email report"""
    try:
        result = await monitoring_scheduler.trigger_immediate_check()
        
        if result["success"]:
            return {
                "message": "Immediate monitoring check triggered successfully",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering monitoring check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering monitoring check: {str(e)}")

@app.post("/monitoring/reset-failures")
async def reset_monitoring_failures(
    service_name: Optional[str] = None,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Reset failure tracking for monitoring services"""
    try:
        monitoring_service.reset_failure_tracking(service_name)
        
        return {
            "message": f"Reset failure tracking for {service_name or 'all services'}",
            "service": service_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resetting monitoring failures: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting failures: {str(e)}")

@app.get("/monitoring/test-email")
async def test_monitoring_email(user: Dict[str, Any] = Depends(require_auth)):
    """Test email functionality by sending a test message"""
    try:
        # Get current health data
        health_data = await monitoring_service.perform_comprehensive_health_check()
        
        # Send test email
        success = await email_service.send_status_report(health_data)
        
        if success:
            return {
                "message": "Test email sent successfully",
                "timestamp": datetime.now().isoformat(),
                "recipients": email_service.email_recipients,
                "recipients_count": len(email_service.email_recipients)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending test email: {str(e)}")

@app.get("/market/refresh-status")
async def get_market_refresh_status():
    """Get synchronized market data refresh status for all users"""
    try:
        # Get market service refresh status
        current_time = datetime.now()
        last_refresh = market_service._last_refresh
        is_market_open = market_service.is_market_open()
        refresh_interval_seconds = market_service.get_refresh_interval()
        
        # Calculate time since last refresh
        time_since_refresh = (current_time - last_refresh).total_seconds()
        
        # Calculate next refresh time
        time_until_next_refresh = max(0, refresh_interval_seconds - time_since_refresh)
        next_refresh_time = current_time + timedelta(seconds=time_until_next_refresh)
        
        # Format for frontend
        minutes_until_refresh = int(time_until_next_refresh // 60)
        seconds_until_refresh = int(time_until_next_refresh % 60)
        
        return {
            "market_status": "open" if is_market_open else "closed",
            "last_refresh": last_refresh.isoformat(),
            "next_refresh": next_refresh_time.isoformat(),
            "next_refresh_in_seconds": int(time_until_next_refresh),
            "next_refresh_minutes": minutes_until_refresh,
            "next_refresh_seconds": seconds_until_refresh,
            "refresh_interval_minutes": refresh_interval_seconds // 60,
            "is_refreshing": market_service._is_refreshing,
            "watchlist_size": len(market_service._watchlist_symbols),
            "auto_refresh_active": market_service._auto_refresh_task is not None,
            "server_time": current_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market refresh status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting refresh status: {str(e)}")

@app.get("/monitoring/test-email-public")
async def test_monitoring_email_public():
    """Public test email endpoint for configuration testing (no auth required)"""
    try:
        logger.info("=== Starting public email test ===")
        
        # Check email service configuration first
        email_health = email_service.health_check()
        logger.info(f"Email service health: {email_health}")
        
        if not email_service.monitoring_enabled:
            return {
                "message": "❌ Email monitoring is disabled",
                "timestamp": datetime.now().isoformat(),
                "email_service_status": email_health,
                "error": "Monitoring disabled - check environment variables"
            }
        
        # Get current health data
        health_data = await monitoring_service.perform_comprehensive_health_check()
        
        # Add test notification to the health data
        health_data["test_mode"] = True
        health_data["test_timestamp"] = datetime.now().isoformat()
        
        logger.info("Sending test email via email service...")
        
        # Send test email with direct call for better error handling
        try:
            success = await email_service.send_status_report(health_data)
            
            if success:
                return {
                    "message": "✅ Test email sent successfully!",
                    "timestamp": datetime.now().isoformat(),
                    "recipients": email_service.email_recipients,
                    "recipients_count": len(email_service.email_recipients),
                    "email_service_status": email_health,
                    "smtp_config": {
                        "host": email_service.smtp_host,
                        "port": email_service.smtp_port,
                        "user": email_service.smtp_user,
                        "from": email_service.email_from
                    }
                }
            else:
                return {
                    "message": "❌ Failed to send test email - check Railway logs for detailed SMTP error",
                    "timestamp": datetime.now().isoformat(),
                    "email_service_status": email_health,
                    "error": "Email service returned failure - see backend logs for SMTP details",
                    "troubleshooting": {
                        "check_railway_logs": "Look for SMTP authentication or connection errors",
                        "verify_credentials": "Ensure SMTP_USER and SMTP_PASSWORD are correct",
                        "gmail_app_password": "Make sure using Gmail App Password, not regular password"
                    }
                }
        except Exception as email_error:
            logger.error(f"Direct email send error: {str(email_error)}")
            return {
                "message": "❌ Email sending failed with exception",
                "timestamp": datetime.now().isoformat(),
                "email_service_status": email_health,
                "error": str(email_error),
                "error_type": type(email_error).__name__
            }
            
    except Exception as e:
        logger.error(f"Error in public test email: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {
            "message": "❌ Error in test email endpoint",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "email_service_status": email_service.health_check()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 