"""
AI Agent integration with OpenAI GPT-4o for portfolio analysis
"""
import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from portfolio import PortfolioManager
from market_data import MarketDataService
from market_context import MarketContextService

# Define available functions for the AI agent
AI_FUNCTIONS = [
    {
        "name": "get_portfolio_summary",
        "description": "Get a summary of the user's portfolio including holdings, values, and performance metrics",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_stock_details",
        "description": "Get detailed information about a specific stock in the user's portfolio",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock symbol to get details for (e.g., AAPL, GOOGL, MSFT)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "search_stock",
        "description": "Search for a stock by name or symbol to get current market data",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The stock name or symbol to search for"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "buy_stock",
        "description": "Execute a stock purchase for the user's portfolio. Can buy both existing holdings and new stocks not currently in the portfolio.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock symbol to buy (e.g., AAPL, GOOGL, MSFT). For stocks not in the portfolio, the system will verify the symbol exists before purchasing."
                },
                "quantity": {
                    "type": "number",
                    "description": "The number of shares to buy (can be decimal for fractional shares)"
                }
            },
            "required": ["symbol", "quantity"]
        }
    },
    {
        "name": "sell_stock",
        "description": "Execute a stock sale from the user's portfolio",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock symbol to sell (e.g., AAPL, GOOGL, MSFT)"
                },
                "quantity": {
                    "type": "number",
                    "description": "The number of shares to sell (can be decimal for fractional shares)"
                }
            },
            "required": ["symbol", "quantity"]
        }
    },
    {
        "name": "calculate_portfolio_metrics",
        "description": "Calculate advanced portfolio metrics like diversification score, risk level, etc.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_transaction_history",
        "description": "Get the user's transaction history",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of transactions to return (default: 10)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_historical_prices",
        "description": "Get historical price data for a stock from the database",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock symbol to get historical data for (e.g., AAPL, GOOGL, MSFT)"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days of historical data to retrieve (default: 30, max: 90)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_cache_stats",
        "description": "Get statistics about the market data cache",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_market_context",
        "description": "Get current market context including economic indicators, relevant news, and sentiment analysis to inform investment decisions",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional stock symbols to get specific news and sentiment for"
                }
            },
            "required": []
        }
    }
]

class AIPortfolioAgent:
    """AI Portfolio Agent for investment advice and portfolio management"""
    
    def __init__(self, portfolio_manager: PortfolioManager, market_service: MarketDataService, market_context_service=None):
        """Initialize AI Portfolio Agent with portfolio manager and market data service"""
        # Initialize services
        self.portfolio_manager = portfolio_manager
        self.market_service = market_service
        
        # Initialize OpenAI client if API key is available
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
            print(f"✅ OpenAI client initialized with model: {self.model}")
        else:
            self.client = None
            print("⚠️  WARNING: OpenAI API key not found. AI features will be limited.")
        
        # Initialize market context service
        self.market_context_service = market_context_service
        
        # System prompt for the AI assistant
        self.system_prompt = """You are a professional AI investment assistant for ProCogia's Portfolio Management platform.

You help users understand their investment portfolio performance using real-time market data and intelligent analysis.

Your capabilities include:
- Analyzing portfolio performance and risk
- Providing insights on individual stock performance  
- Offering data-driven investment recommendations
- Explaining market trends and their impact on holdings
- Executing buy and sell orders for stocks when requested by the user
- Analyzing current market conditions using economic data and news

When users ask about the market or economy, you can access real-time economic indicators, 
financial news, and sentiment analysis to provide informed perspectives on market conditions.

When users ask you to buy or sell stocks, you can execute these transactions directly. Make sure to:
1. Confirm the details of the transaction (symbol, quantity, price) before executing
2. Check if the user has sufficient funds (for buys) or shares (for sells)
3. Provide a clear summary of the transaction after it's completed
4. Update the user on their new portfolio balance and holdings

You can buy both stocks that are already in the portfolio AND new stocks that aren't currently held. For new stocks, you'll automatically verify the symbol exists before purchasing.

Always be professional, accurate, and helpful. When users ask about portfolio data, I will provide you with the current portfolio information including real-time prices and performance metrics.

When discussing performance, always include:
- Specific numbers (prices, percentages, dollar amounts)
- Context about market conditions
- Clear explanations of calculations
- Professional investment terminology

Remember: This is a simulation environment, so any trading recommendations are for educational purposes only."""

    async def get_portfolio_data(self) -> Dict[str, Any]:
        """Get comprehensive portfolio data for AI context"""
        try:
            holdings = self.portfolio_manager.get_holdings()
            if not holdings:
                return {"error": "No holdings found in portfolio"}
                
            symbols = [holding["symbol"] for holding in holdings]
            market_prices = await self.market_service.get_multiple_quotes(symbols)
            portfolio_data = self.portfolio_manager.calculate_portfolio_value(market_prices)
            
            return {
                "portfolio_summary": {
                    "total_portfolio_value": portfolio_data["portfolio_value"],
                    "total_pnl": portfolio_data["total_pnl"],
                    "total_pnl_percent": portfolio_data["total_pnl_percent"],
                    "cash_balance": portfolio_data["cash_balance"],
                    "total_account_value": portfolio_data["total_account_value"]
                },
                "holdings": portfolio_data["holdings"],
                "market_prices": market_prices,
                "last_updated": portfolio_data["last_updated"]
            }
        except Exception as e:
            print(f"Error fetching portfolio data: {str(e)}")
            return {"error": str(e)}

    async def get_stock_performance_data(self, symbol: str) -> Dict[str, Any]:
        """Get detailed performance data for a specific stock"""
        try:
            symbols = [holding["symbol"] for holding in self.portfolio_manager.get_holdings()]
            market_prices = await self.market_service.get_multiple_quotes(symbols)
            
            holding = self.portfolio_manager.get_holding_by_symbol(symbol)
            if not holding:
                return {"error": f"Stock {symbol} not found in portfolio"}
            
            current_price = market_prices.get(symbol.upper(), holding["purchase_price"])
            quantity = holding["quantity"]
            purchase_price = holding["purchase_price"]
            
            cost_basis = quantity * purchase_price
            current_value = quantity * current_price
            pnl = current_value - cost_basis
            pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            return {
                "symbol": symbol.upper(),
                "shares_owned": quantity,
                "purchase_price": purchase_price,
                "current_price": current_price,
                "total_investment": cost_basis,
                "current_value": current_value,
                "pnl": pnl,
                "pnl_percent": pnl_percent
            }
        except Exception as e:
            return {"error": str(e)}

    async def format_portfolio_context(self, user_message: str) -> str:
        """Create context-aware prompt with portfolio data only when relevant"""
        # Check if the message is related to portfolio or investments
        portfolio_keywords = [
            'portfolio', 'stock', 'invest', 'holding', 'share', 'market', 'price', 
            'value', 'performance', 'balance', 'cash', 'position', 'asset', 'equity',
            'gain', 'loss', 'return', 'profit', 'dividend', 'buy', 'sell', 'trade',
            'pnl', 'p&l', 'allocation', 'diversif', 'risk', 'volatility'
        ]
        
        # Check for stock symbols in common formats
        stock_symbols = ['aapl', 'msft', 'googl', 'goog', 'amzn', 'tsla', 'nvda', 'meta', 'amd']
        
        # Normalize user message for easier matching
        normalized_message = user_message.lower()
        
        # Check if message contains portfolio-related keywords or stock symbols
        is_portfolio_related = any(keyword in normalized_message for keyword in portfolio_keywords) or \
                              any(symbol in normalized_message.split() for symbol in stock_symbols)
        
        context = ""
        
        # Only add portfolio context if the query is related to portfolio/investments
        if is_portfolio_related:
            # Get portfolio data
            portfolio_data = await self.get_portfolio_data()
            
            if "error" in portfolio_data:
                context = "Portfolio data is currently unavailable."
            else:
                # Format portfolio context - keep it concise to reduce token usage
                context = f"""
CURRENT PORTFOLIO DATA:
Total Portfolio Value: ${portfolio_data['portfolio_summary']['total_portfolio_value']:,.2f}
Total P&L: ${portfolio_data['portfolio_summary']['total_pnl']:,.2f} ({portfolio_data['portfolio_summary']['total_pnl_percent']:+.2f}%)
Cash Balance: ${portfolio_data['portfolio_summary']['cash_balance']:,.2f}

HOLDINGS:"""
                for holding in portfolio_data['holdings']:
                    context += f"\n- {holding['symbol']}: {holding['quantity']} shares, ${holding['current_price']:.2f}/share, P&L: ${holding['pnl']:,.2f} ({holding['pnl_percent']:+.2f}%)"
            
                # Only add detailed stock analysis if specifically asked about a stock
                for symbol in ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']:
                    if symbol in user_message.upper() or (symbol == 'AAPL' and 'APPLE' in user_message.upper()) or (symbol == 'GOOGL' and 'GOOGLE' in user_message.upper()) or (symbol == 'MSFT' and 'MICROSOFT' in user_message.upper()):
                        stock_data = await self.get_stock_performance_data(symbol)
                        if "error" not in stock_data:
                            context += f"\n\nDETAILED {symbol} ANALYSIS: {stock_data['shares_owned']} shares, bought at ${stock_data['purchase_price']:.2f}, now ${stock_data['current_price']:.2f}, P&L: ${stock_data['pnl']:,.2f} ({stock_data['pnl_percent']:+.2f}%)"
        
        # Provide a clear instruction for the AI - different based on whether portfolio data was included
        if is_portfolio_related:
            instruction = """
You are a professional investment assistant. Answer the user's question using the portfolio data above.
You have access to the following functions to get additional information:
- get_portfolio_summary() - For overall portfolio information and performance metrics
- get_stock_details(symbol) - For detailed information about a specific stock in the portfolio
- search_stock(query) - To search for any stock and get current market data
- calculate_portfolio_metrics() - For portfolio risk, diversification, and sector allocation metrics
- get_transaction_history(limit) - For the user's recent transactions history
- get_historical_prices(symbol, days) - For historical price data of any stock (default 30 days, max 90)
- get_cache_stats() - For information about the market data cache
- get_market_context(symbols) - For current market context including economic indicators, relevant news, and sentiment analysis

USER QUESTION: {user_message}

Respond with helpful, specific information about their portfolio. Include relevant numbers and insights.
Use the available functions to provide the most accurate and detailed answer possible.
"""
        else:
            instruction = """
You are a professional investment assistant. Answer the user's question thoughtfully.
You have access to the following functions to get information:
- search_stock(query) - To search for any stock and get current market data
- get_historical_prices(symbol, days) - For historical price data of any stock (default 30 days, max 90)
- get_cache_stats() - For information about the market data cache
- get_market_context(symbols) - For current market context including economic indicators, relevant news, and sentiment analysis

USER QUESTION: {user_message}

Respond with helpful information. Since the question is not about their specific portfolio,
focus on providing general advice, information, or answering their question directly.
Use the available functions when appropriate to provide accurate market data.
"""
        
        full_prompt = instruction.format(user_message=user_message)
        if context:
            full_prompt = context + "\n\n" + full_prompt
            
        return full_prompt

    async def execute_function(self, function_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a function based on the AI's request"""
        if params is None:
            params = {}
        
        print(f"Executing function: {function_name} with params: {params}")
        
        if function_name == "get_portfolio_summary":
            try:
                portfolio_data = await self.get_portfolio_data()
                # Ensure we return a valid dictionary
                if isinstance(portfolio_data, dict):
                    return portfolio_data
                else:
                    return {"error": "Invalid portfolio data format"}
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "get_stock_details":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"error": "No stock symbol provided"}
            
            try:
                # Check if stock is in portfolio
                holding = self.portfolio_manager.get_holding_by_symbol(symbol)
                if not holding:
                    return {"error": f"Stock {symbol} not found in portfolio"}
                
                return await self.get_stock_performance_data(symbol)
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "search_stock":
            query = params.get("query", "")
            if not query:
                return {"error": "No search query provided"}
            
            try:
                search_results = await self.market_service.search_stocks(query)
                # Ensure we return a valid dictionary
                return {"results": search_results}
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "buy_stock":
            symbol = params.get("symbol", "").upper()
            quantity = params.get("quantity")
            
            if not symbol:
                return {"error": "No stock symbol provided"}
            
            if not quantity or quantity <= 0:
                return {"error": "Invalid quantity. Please provide a positive number of shares to buy."}
            
            try:
                # Check if the symbol exists by searching for it
                search_results = None
                try:
                    search_results = await self.market_service.search_stocks(symbol)
                    if not search_results or len(search_results) == 0:
                        return {"error": f"Could not find stock with symbol {symbol}"}
                    
                    # Verify the symbol matches exactly what we're looking for
                    exact_match = False
                    for result in search_results:
                        if result.get("symbol", "").upper() == symbol.upper():
                            exact_match = True
                            break
                    
                    if not exact_match:
                        return {
                            "error": f"Could not find exact match for symbol {symbol}. Did you mean one of these?",
                            "suggestions": [r.get("symbol") for r in search_results[:5]]
                        }
                except Exception as search_error:
                    print(f"Warning: Search failed but continuing: {search_error}")
                    # Continue with the buy operation even if search fails
                
                # Get current price of the stock
                quote_data = await self.market_service.get_stock_quote(symbol)
                if not quote_data or "price" not in quote_data:
                    return {"error": f"Could not get current price for {symbol}"}
                
                current_price = quote_data["price"]
                
                # Check if the user can afford the purchase
                portfolio_data = await self.get_portfolio_data()
                cash_balance = portfolio_data["portfolio_summary"]["cash_balance"]
                total_cost = current_price * quantity
                
                if total_cost > cash_balance:
                    max_affordable = int(cash_balance / current_price) if current_price > 0 else 0
                    return {
                        "success": False,
                        "error": f"Insufficient funds. You need ${total_cost:.2f} but have ${cash_balance:.2f}.",
                        "affordability": {
                            "can_afford": False,
                            "cash_balance": cash_balance,
                            "total_cost": total_cost,
                            "shortfall": total_cost - cash_balance,
                            "max_affordable_shares": max_affordable,
                            "current_price": current_price
                        }
                    }
                
                # Execute the buy order
                from database import db_service
                
                # Get the user's portfolio ID
                portfolios = await db_service.get_user_portfolios(self.portfolio_manager.user_id)
                if not portfolios:
                    return {"error": "No portfolio found for this user"}
                
                portfolio_id = portfolios[0]["id"]
                
                # Execute the buy order
                result = await db_service.execute_buy_order(
                    portfolio_id=portfolio_id,
                    user_id=self.portfolio_manager.user_id,
                    symbol=symbol,
                    shares=quantity,
                    price_per_share=current_price
                )
                
                # Update the portfolio manager's data
                updated_portfolio = await db_service.get_portfolio_by_id(portfolio_id, self.portfolio_manager.user_id)
                updated_holdings = await db_service.get_portfolio_holdings(portfolio_id)
                
                self.portfolio_manager.portfolio = {
                    "cash_balance": updated_portfolio["cash_balance"],
                    "holdings": [
                        {
                            "symbol": h["symbol"],
                            "quantity": h["shares"],
                            "purchase_price": h["average_cost"]
                        } for h in updated_holdings
                    ]
                }
                
                # Include stock information in the response if we have it
                stock_info = {}
                if search_results and len(search_results) > 0:
                    for result in search_results:
                        if result.get("symbol", "").upper() == symbol.upper():
                            stock_info = {
                                "name": result.get("name", ""),
                                "exchange": result.get("exchange", ""),
                                "type": result.get("type", "")
                            }
                            break
                
                return {
                    "success": True,
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "total_cost": total_cost,
                    "new_cash_balance": result["new_cash_balance"],
                    "transaction_id": result["transaction"]["id"],
                    "message": f"Successfully purchased {quantity} shares of {symbol} at ${current_price:.2f} per share.",
                    "stock_info": stock_info
                }
                
            except Exception as e:
                return {"error": f"Error executing buy order: {str(e)}"}
        
        elif function_name == "sell_stock":
            symbol = params.get("symbol", "").upper()
            quantity = params.get("quantity")
            
            if not symbol:
                return {"error": "No stock symbol provided"}
            
            if not quantity or quantity <= 0:
                return {"error": "Invalid quantity. Please provide a positive number of shares to sell."}
            
            try:
                # Check if the user owns the stock and has enough shares
                holding = self.portfolio_manager.get_holding_by_symbol(symbol)
                if not holding:
                    return {"error": f"You don't own any shares of {symbol}"}
                
                if holding["quantity"] < quantity:
                    return {
                        "success": False,
                        "error": f"Insufficient shares. You own {holding['quantity']} shares of {symbol} but are trying to sell {quantity}.",
                        "available_shares": holding["quantity"]
                    }
                
                # Get current price of the stock
                quote_data = await self.market_service.get_stock_quote(symbol)
                if not quote_data or "price" not in quote_data:
                    return {"error": f"Could not get current price for {symbol}"}
                
                current_price = quote_data["price"]
                total_proceeds = current_price * quantity
                
                # Execute the sell order
                from database import db_service
                
                # Get the user's portfolio ID
                portfolios = await db_service.get_user_portfolios(self.portfolio_manager.user_id)
                if not portfolios:
                    return {"error": "No portfolio found for this user"}
                
                portfolio_id = portfolios[0]["id"]
                
                # Execute the sell order
                result = await db_service.execute_sell_order(
                    portfolio_id=portfolio_id,
                    user_id=self.portfolio_manager.user_id,
                    symbol=symbol,
                    shares=quantity,
                    price_per_share=current_price
                )
                
                # Update the portfolio manager's data
                updated_portfolio = await db_service.get_portfolio_by_id(portfolio_id, self.portfolio_manager.user_id)
                updated_holdings = await db_service.get_portfolio_holdings(portfolio_id)
                
                self.portfolio_manager.portfolio = {
                    "cash_balance": updated_portfolio["cash_balance"],
                    "holdings": [
                        {
                            "symbol": h["symbol"],
                            "quantity": h["shares"],
                            "purchase_price": h["average_cost"]
                        } for h in updated_holdings
                    ]
                }
                
                return {
                    "success": True,
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "total_proceeds": total_proceeds,
                    "new_cash_balance": result["new_cash_balance"],
                    "transaction_id": result["transaction"]["id"],
                    "message": f"Successfully sold {quantity} shares of {symbol} at ${current_price:.2f} per share."
                }
                
            except Exception as e:
                return {"error": f"Error executing sell order: {str(e)}"}
        
        elif function_name == "calculate_portfolio_metrics":
            try:
                holdings = self.portfolio_manager.get_holdings()
                if not holdings:
                    return {"error": "No holdings found in portfolio"}
                
                # Get current market prices
                symbols = [h["symbol"] for h in holdings]
                market_prices = await self.market_service.get_multiple_quotes(symbols)
                
                # Calculate diversification score (simplified)
                total_value = sum(h["quantity"] * market_prices.get(h["symbol"], h["purchase_price"]) for h in holdings)
                if total_value == 0:
                    return {"error": "Portfolio has no value"}
                
                # Calculate diversification based on number of holdings and sector distribution
                base_score = min(100, len(holdings) * 20)  # More holdings = better diversification
                
                # Sector-based diversification (simplified)
                sector_distribution = {}
                
                # Map symbols to sectors (simplified)
                sectors = {
                    "AAPL": "Technology",
                    "MSFT": "Technology",
                    "GOOGL": "Technology",
                    "AMZN": "Consumer Cyclical",
                    "META": "Technology",
                    "TSLA": "Automotive",
                    "NVDA": "Technology",
                    "JPM": "Financial Services",
                    "V": "Financial Services",
                    "JNJ": "Healthcare",
                    "PG": "Consumer Defensive",
                    "UNH": "Healthcare",
                    "HD": "Consumer Cyclical",
                    "BAC": "Financial Services",
                    "XOM": "Energy",
                    "DIS": "Communication Services",
                    "VZ": "Communication Services",
                    "NFLX": "Communication Services",
                    "ADBE": "Technology",
                    "CRM": "Technology",
                    "AMD": "Technology"
                }
                
                # Calculate concentration by sector
                for holding in holdings:
                    symbol = holding["symbol"]
                    value = holding["quantity"] * market_prices.get(symbol, holding["purchase_price"])
                    sector = sectors.get(symbol, "Other")
                    
                    if sector in sector_distribution:
                        sector_distribution[sector] += value
                    else:
                        sector_distribution[sector] = value
                
                # Adjust score based on sector concentration
                sector_count = len(sector_distribution)
                concentration_penalty = max(0, 5 - sector_count) * 10  # Penalty for fewer sectors
                
                # Calculate final diversification score
                diversification_score = max(0, min(100, base_score - concentration_penalty))
                
                # Format sector distribution as dictionary
                formatted_sectors = {}
                for sector, value in sector_distribution.items():
                    formatted_sectors[sector] = {
                        "value": float(value),
                        "percentage": float((value / total_value) * 100) if total_value > 0 else 0
                    }
                
                return {
                    "diversification_score": diversification_score,
                    "risk_level": "High" if diversification_score < 40 else "Medium" if diversification_score < 70 else "Low",
                    "sector_distribution": formatted_sectors,
                    "concentration_risk": "High" if len(holdings) < 3 else "Medium" if len(holdings) < 5 else "Low"
                }
            
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "get_transaction_history":
            try:
                limit = params.get("limit", 10)
                transactions = self.portfolio_manager.get_transactions()
                # Ensure we return a dictionary with a list
                return {"transactions": transactions[:limit] if transactions else []}
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "get_historical_prices":
            try:
                symbol = params.get("symbol", "")
                days = params.get("days", 30)
                if not symbol:
                    return {"error": "No stock symbol provided"}
                
                historical_data = await self.market_service.get_historical_data(symbol, days)
                # Ensure we return a dictionary
                return {"data": historical_data, "symbol": symbol, "days": days}
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "get_cache_stats":
            try:
                stats = await self.market_service.get_cache_stats()
                # Ensure we return a dictionary
                if isinstance(stats, dict):
                    return stats
                else:
                    return {"stats": stats}
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "get_market_context":
            try:
                symbols = params.get("symbols", [])
                # Convert to list if it's a single string
                if isinstance(symbols, str):
                    symbols = [symbols]
                    
                market_context = await self.market_context_service.get_market_context(symbols)
                return market_context
            except Exception as e:
                return {"error": str(e)}
        
        else:
            return {"error": f"Unknown function: {function_name}"}

    async def chat(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Process user message and return AI response with function calling"""
        if not self.client or not self.model:
            return {
                "response": "I'm sorry, but the AI service is not configured. Please set up your OpenAI API key to use the AI assistant.",
                "error": "Missing OpenAI API key"
            }
        
        try:
            # Create context-aware prompt
            context_prompt = await self.format_portfolio_context(user_message)
            
            # Generate response using OpenAI with function calling
            try:
                # Format the tools for OpenAI function calling
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": func["name"],
                            "description": func["description"],
                            "parameters": func["parameters"]
                        }
                    } for func in AI_FUNCTIONS
                ]
                
                # Create the initial message
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context_prompt}
                ]
                
                # Make the API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=2048
                )
                
                # Check if the model wants to call a function
                function_called = None
                function_response = None
                
                response_message = response.choices[0].message
                
                # Process function calls if present
                if response_message.tool_calls:
                    # Get the function call
                    tool_call = response_message.tool_calls[0]
                    function_name = tool_call.function.name
                    
                    try:
                        # Parse function arguments safely
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        # Handle invalid JSON in arguments
                        print(f"Error: Invalid JSON in function arguments: {tool_call.function.arguments}")
                        function_args = {}
                    
                    print(f"Function called: {function_name} with args: {function_args}")
                    
                    # Execute the function
                    function_called = function_name
                    try:
                        function_response = await self.execute_function(function_name, function_args)
                        
                        # Ensure function_response is a valid dictionary
                        if not isinstance(function_response, dict):
                            print(f"Warning: Function {function_name} returned non-dict response: {function_response}")
                            function_response = {"result": str(function_response)}
                    except Exception as func_error:
                        print(f"Error executing function {function_name}: {str(func_error)}")
                        function_response = {"error": str(func_error)}
                    
                    # Add the assistant's response and function result to the conversation
                    messages.append(response_message)
                    
                    # Convert function response to string safely
                    try:
                        function_response_str = json.dumps(function_response)
                    except (TypeError, ValueError) as json_error:
                        print(f"Error serializing function response: {str(json_error)}")
                        # Create a safe version of the response
                        safe_response = {"error": "Could not serialize function response"}
                        function_response = safe_response
                        function_response_str = json.dumps(safe_response)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response_str
                    })
                    
                    # Get a new response from the model
                    second_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.2,
                        max_tokens=2048
                    )
                    
                    # Return the final response
                    return {
                        "response": second_response.choices[0].message.content,
                        "function_called": function_called,
                        "function_response": function_response,
                        "success": True
                    }
                else:
                    # No function was called, return the direct response
                    return {
                        "response": response_message.content,
                        "function_called": None,
                        "function_response": None,
                        "success": True
                    }
                    
            except Exception as e:
                print(f"Function calling approach failed: {e}")
                
                # Try standard response without function calling as a fallback
                try:
                    # Make a simpler API call without function calling
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": context_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=2048
                    )
                    
                    # If the response is successful, return it
                    return {
                        "response": response.choices[0].message.content,
                        "function_called": None,
                        "function_response": None,
                        "success": True
                    }
                except Exception as fallback_error:
                    print(f"Standard response generation also failed: {fallback_error}")
                    # Ultimate fallback if everything fails
                    return {
                        "response": "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                        "error": f"Error in function calling: {str(e)}",
                        "success": False
                    }
            
        except Exception as e:
            print(f"Error in AI chat: {e}")
            return {
                "response": f"I'm sorry, I encountered an error while processing your request: {str(e)}",
                "error": str(e),
                "success": False
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if AI service is working"""
        try:
            if not os.getenv("OPENAI_API_KEY"):
                return {
                    "status": "error",
                    "api_key_configured": False,
                    "error": "OpenAI API key not configured"
                }
            
            if not self.client:
                return {
                    "status": "error", 
                    "api_key_configured": True,
                    "error": "OpenAI client not initialized"
                }
            
            # Simple health check without async call
            return {
                "status": "healthy",
                "api_key_configured": True,
                "model": "gpt-4o",
                "functions_available": len(AI_FUNCTIONS),
                "ready": True
            }
        except Exception as e:
            return {
                "status": "error",
                "api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
                "error": str(e)
            } 