"""
AI Portfolio Agent - FastAPI backend with OAuth authentication and database integration
"""
import os
import uuid
from datetime import datetime
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

# Import services
from portfolio import PortfolioManager
from market_data import MarketDataService
from ai_agent import AIPortfolioAgent
from auth import AuthenticationService
from market_context import MarketContextService
import database

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
ai_agent = AIPortfolioAgent(portfolio_manager, market_service, market_context_service)

# Security
security = HTTPBearer(auto_error=False)

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

class BuyStockRequest(BaseModel):
    symbol: str
    quantity: int

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
            }
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 errors"""
    return {"message": "No favicon configured"}

# Authentication Endpoints
@app.get("/auth/login")
async def login():
    """Initiate OAuth login with Google"""
    if not auth_service.google_client_id:
        raise HTTPException(status_code=500, detail="OAuth not configured")
    
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    redirect_uri = f"{base_url}/auth/callback"
    oauth_url = auth_service.get_google_oauth_url(redirect_uri)
    
    return {"oauth_url": oauth_url}

@app.get("/auth/callback")
async def auth_callback(code: str, state: Optional[str] = None):
    """Handle OAuth callback from Google"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    redirect_uri = f"{base_url}/auth/callback"
    
    # Exchange code for tokens
    token_data = auth_service.exchange_code_for_token(code, redirect_uri)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    # Verify the ID token and get user info
    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No ID token received")
    
    user_info = auth_service.verify_google_token(id_token)
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
    
    # Redirect to frontend with token
    frontend_base_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 