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
        "description": "Search for a specific stock by company name or symbol to get current market data. ONLY accepts specific company names or symbols (e.g., 'Apple', 'AAPL', 'Microsoft'). Does NOT accept generic categories like 'tech stocks' or 'healthcare sector'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The specific company name or stock symbol to search for (e.g., 'Apple', 'AAPL', 'Microsoft', 'MSFT'). Do NOT use generic terms like 'tech stocks' or 'healthcare sector'."
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

CRITICAL: BE EXTREMELY PROACTIVE AND DECISIVE. Users expect you to take complete action without requiring multiple interactions.

FUNCTION USAGE GUIDELINES:
1. search_stock: 
   - This function ONLY accepts SPECIFIC stock symbols or company names (e.g., "AAPL", "Apple", "MSFT", "Tesla")
   - It CANNOT search for generic categories like "healthcare stocks" or "renewable energy stocks"
   - If you need stocks from a specific sector, you MUST search for KNOWN companies in that sector
   - Example valid inputs: "AAPL", "Microsoft", "TSLA", "Amazon"
   - Example invalid inputs: "tech stocks", "healthcare sector", "renewable energy companies"

2. buy_stock and sell_stock:
   - These functions require SPECIFIC stock symbols that exist in the market
   - Always verify a stock exists by using search_stock before attempting to buy it
   - The quantity parameter must be a positive number
   - These functions will return detailed error messages if the transaction cannot be completed

When users ask you to perform complex tasks:
1. GATHER ALL NECESSARY INFORMATION UPFRONT - don't ask for information piece by piece
2. Use ALL available functions to collect comprehensive data before making decisions
3. Present COMPLETE solutions, not partial ones that require further user input
4. Make well-reasoned decisions based on the data - don't ask the user to choose between options
5. Only ask for confirmation ONCE after presenting a COMPLETE plan with ALL details

TRANSACTION CONFIRMATION PROTOCOL:
When users request to buy or sell stocks or make portfolio changes:
1. Research and identify the BEST options based on data - don't present multiple options for the user to choose from
2. Create a COMPLETE plan with specific stocks, quantities, and estimated prices
3. Present the FULL transaction details in one clear confirmation request
4. Include the estimated total value and expected outcome
5. Ask explicitly: "Would you like me to proceed with this complete transaction plan?"
6. Only execute the transaction after receiving clear confirmation
7. If the user modifies any details, adapt your plan accordingly

When users ask about the market or economy, you should IMMEDIATELY access real-time economic indicators, 
financial news, and sentiment analysis to provide informed perspectives on market conditions.

When users ask you to buy or sell stocks, you can execute these transactions directly. Make sure to:
1. Confirm the details of the transaction (symbol, quantity, price) before executing
2. Check if the user has sufficient funds (for buys) or shares (for sells)
3. Provide a clear summary of the transaction after it's completed
4. Update the user on their new portfolio balance and holdings

You can buy both stocks that are already in the portfolio AND new stocks that aren't currently held. For new stocks, you'll automatically verify the symbol exists before purchasing.

REMEMBER: Always maintain memory of previous interactions in the conversation. Use this context to provide more relevant and personalized responses.

MULTI-STEP PROCESSES:
For complex requests involving multiple steps:
1. Break down the request into clear steps
2. Execute each step in logical sequence
3. Provide updates after completing each major step
4. Summarize the entire process when complete

For portfolio rebalancing or complex strategies:
1. First analyze the current portfolio composition
2. Evaluate market conditions and relevant economic factors
3. MAKE SPECIFIC DECISIONS about which stocks to buy/sell and at what quantities
4. Present a complete plan with specific actions
5. Request confirmation before executing any trades
6. Execute trades only after receiving explicit approval
7. Provide a comprehensive summary of changes made

SECTOR-BASED RECOMMENDATIONS:
When asked to recommend stocks from specific sectors:
1. Use your knowledge to identify SPECIFIC well-known companies in that sector
2. Search for these specific companies by name or symbol using search_stock
3. If the search fails, try other well-known companies in the sector
4. NEVER search for generic sector terms like "healthcare stocks" or "renewable energy companies"
5. Example: Instead of searching for "renewable energy stock", search for specific companies like "NEE" (NextEra Energy) or "ENPH" (Enphase Energy)"""

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
        """Format portfolio context for the AI prompt"""
        try:
            # Get portfolio data
            portfolio_data = await self.get_portfolio_data()
            
            # Calculate basic portfolio metrics
            total_portfolio_value = 0
            cash_balance = portfolio_data.get("cash_balance", 0)
            holdings = portfolio_data.get("holdings", [])
            
            # Format holdings data
            holdings_text = ""
            symbols = []
            
            if holdings:
                for holding in holdings:
                    symbol = holding.get("symbol", "")
                    quantity = holding.get("quantity", 0)
                    purchase_price = holding.get("purchase_price", 0)
                    current_price = holding.get("current_price", 0)
                    
                    # Calculate metrics
                    position_value = quantity * current_price
                    total_portfolio_value += position_value
                    cost_basis = quantity * purchase_price
                    pnl = position_value - cost_basis
                    pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    # Format holding text
                    holdings_text += f"- {symbol}: {quantity} shares, purchase price: ${purchase_price:.2f}, current price: ${current_price:.2f}, value: ${position_value:.2f}, P&L: ${pnl:.2f} ({pnl_percent:.2f}%)\n"
                    
                    # Add symbol to list for market context
                    symbols.append(symbol)
            
            # Calculate total account value
            total_account_value = total_portfolio_value + cash_balance
            
            # Get portfolio diversification metrics
            diversification = "Not diversified"
            risk_level = "Unknown"
            
            try:
                # Try to get more detailed portfolio metrics if available
                metrics = await self.execute_function("calculate_portfolio_metrics")
                if metrics and not isinstance(metrics, str) and "error" not in metrics:
                    diversification = metrics.get("diversification_score", "Not calculated")
                    risk_level = metrics.get("risk_level", "Not calculated")
                    sector_allocation = metrics.get("sector_allocation", {})
                    
                    # Add sector allocation to the context
                    if sector_allocation:
                        holdings_text += "\nSector Allocation:\n"
                        for sector, percentage in sector_allocation.items():
                            holdings_text += f"- {sector}: {percentage:.1f}%\n"
            except Exception as metrics_error:
                print(f"Error getting portfolio metrics: {metrics_error}")
            
            # Get market context if available
            market_context = ""
            try:
                if self.market_context_service:
                    context_data = await self.market_context_service.get_market_context(symbols)
                    
                    if context_data and "error" not in context_data:
                        # Extract economic indicators
                        indicators = context_data.get("economic_indicators", {})
                        if indicators:
                            market_context += "\nEconomic Indicators:\n"
                            for name, value in indicators.items():
                                market_context += f"- {name}: {value}\n"
                        
                        # Extract market sentiment
                        sentiment = context_data.get("market_sentiment", {})
                        if sentiment:
                            sentiment_score = sentiment.get("sentiment_score", 0)
                            sentiment_label = "Bullish" if sentiment_score > 0 else "Bearish" if sentiment_score < 0 else "Neutral"
                            market_context += f"\nMarket Sentiment: {sentiment_label} (score: {sentiment_score})\n"
                            
                            # Add sentiment factors
                            factors = sentiment.get("factors", [])
                            if factors:
                                market_context += "Sentiment Factors:\n"
                                for factor in factors:
                                    market_context += f"- {factor}\n"
                        
                        # Extract relevant news
                        news = context_data.get("relevant_news", [])
                        if news:
                            market_context += "\nRecent Market News:\n"
                            # Limit to top 5 news items
                            for i, item in enumerate(news[:5]):
                                market_context += f"- {item.get('title', 'No title')}\n"
            except Exception as context_error:
                print(f"Error getting market context: {context_error}")
            
            # Format the complete portfolio context
            portfolio_context = f"""
Current Portfolio Information:
- Cash Balance: ${cash_balance:.2f}
- Portfolio Value: ${total_portfolio_value:.2f}
- Total Account Value: ${total_account_value:.2f}
- Diversification Score: {diversification}
- Risk Level: {risk_level}

Holdings:
{holdings_text}
{market_context}
"""
            
            # Combine user message with portfolio context
            combined_prompt = f"""
User Message: {user_message}

{portfolio_context}
"""
            return combined_prompt
            
        except Exception as e:
            print(f"Error formatting portfolio context: {e}")
            # Return the original message if there's an error
            return f"User Message: {user_message}\n\nNote: Unable to retrieve portfolio context."

    async def execute_function(self, function_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a function with given parameters"""
        params = params or {}
        
        if function_name == "get_portfolio_summary":
            try:
                portfolio_data = await self.get_portfolio_data()
                return portfolio_data
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "get_stock_details":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"error": "Symbol is required"}
            
            try:
                stock_data = await self.get_stock_performance_data(symbol)
                return stock_data
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "search_stock":
            query = params.get("query", "")
            if not query:
                return {"error": "Query is required"}
            
            print(f"Executing function: {function_name} with params: {params}")
            
            # Check if query looks like a generic category rather than a specific stock
            generic_terms = ["stock", "stocks", "sector", "industry", "companies", "etf", "fund", "index"]
            sector_terms = ["tech", "technology", "healthcare", "energy", "renewable", "financial", "consumer", 
                           "retail", "industrial", "materials", "utilities", "telecom", "real estate"]
            
            is_likely_generic = False
            # Check if query contains both sector terms and generic terms
            if any(term in query.lower() for term in generic_terms) and any(term in query.lower() for term in sector_terms):
                is_likely_generic = True
            
            if is_likely_generic:
                # Provide helpful error message with examples
                return {
                    "error": f"'{query}' appears to be a generic category search. The search_stock function only accepts specific company names or symbols.",
                    "help": "Try searching for specific companies instead. For example:",
                    "examples": {
                        "technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
                        "healthcare": ["JNJ", "UNH", "PFE", "ABBV"],
                        "renewable_energy": ["NEE", "ENPH", "SEDG", "RUN"],
                        "financial": ["JPM", "BAC", "GS", "V"]
                    }
                }
            
            try:
                # Search for stock
                search_results = await self.market_service.search_stocks(query)
                
                if not search_results or len(search_results) == 0:
                    return {"error": f"Could not find stock matching '{query}'"}
                
                # Get the first result (most relevant match)
                stock = search_results[0]
                symbol = stock.get("symbol")
                
                # Get current price
                price_data = await self.market_service.get_stock_price(symbol)
                
                if not price_data or "error" in price_data:
                    return {
                        "symbol": symbol,
                        "name": stock.get("instrument_name"),
                        "exchange": stock.get("exchange"),
                        "error": f"Found stock but could not retrieve current price for {symbol}",
                        "price": None,
                        "search_results": search_results[:5]  # Include top 5 results
                    }
                
                # Return stock data with price
                return {
                    "symbol": symbol,
                    "name": stock.get("instrument_name"),
                    "exchange": stock.get("exchange"),
                    "price": price_data.get("price"),
                    "currency": price_data.get("currency", "USD"),
                    "last_updated": price_data.get("last_updated"),
                    "search_results": search_results[:5]  # Include top 5 results
                }
            except Exception as e:
                return {"error": str(e), "query": query}
        
        elif function_name == "buy_stock":
            symbol = params.get("symbol", "").upper()
            quantity = params.get("quantity")
            
            if not symbol:
                return {"error": "Symbol is required"}
            if not quantity:
                return {"error": "Quantity is required"}
            
            try:
                quantity = float(quantity)
            except ValueError:
                return {"error": "Quantity must be a number"}
            
            if quantity <= 0:
                return {"error": "Quantity must be positive"}
            
            try:
                # First, verify the stock exists and get its current price
                price_data = await self.market_service.get_stock_price(symbol)
                
                if not price_data or "error" in price_data:
                    return {"error": f"Could not retrieve current price for {symbol}. Please verify the symbol and try again."}
                
                current_price = price_data.get("price")
                if not current_price:
                    return {"error": f"Could not determine current price for {symbol}"}
                
                # Calculate total cost
                total_cost = current_price * quantity
                
                # Check if user has enough cash
                if self.portfolio_manager.portfolio["cash_balance"] < total_cost:
                    return {
                        "error": "Insufficient funds",
                        "cash_balance": self.portfolio_manager.portfolio["cash_balance"],
                        "required": total_cost,
                        "symbol": symbol,
                        "price": current_price,
                        "quantity": quantity
                    }
                
                # Execute the buy
                result = await self.portfolio_manager.buy_stock(symbol, quantity)
                
                if "error" in result:
                    return result
                
                # Add current price to the result
                result["price"] = current_price
                result["total_cost"] = total_cost
                
                return result
            except Exception as e:
                return {"error": str(e)}
        
        elif function_name == "sell_stock":
            symbol = params.get("symbol", "").upper()
            quantity = params.get("quantity")
            
            if not symbol:
                return {"error": "Symbol is required"}
            if not quantity:
                return {"error": "Quantity is required"}
            
            try:
                quantity = float(quantity)
            except ValueError:
                return {"error": "Quantity must be a number"}
            
            if quantity <= 0:
                return {"error": "Quantity must be positive"}
            
            try:
                # First, verify the stock exists in the portfolio and get its current price
                holdings = self.portfolio_manager.portfolio.get("holdings", [])
                holding = next((h for h in holdings if h["symbol"] == symbol), None)
                
                if not holding:
                    return {"error": f"You don't own any shares of {symbol}"}
                
                if holding["quantity"] < quantity:
                    return {
                        "error": f"Insufficient shares. You own {holding['quantity']} shares of {symbol}, but are trying to sell {quantity}.",
                        "owned_shares": holding["quantity"],
                        "requested_shares": quantity
                    }
                
                # Get current price
                price_data = await self.market_service.get_stock_price(symbol)
                
                if not price_data or "error" in price_data:
                    return {"error": f"Could not retrieve current price for {symbol}. Please try again later."}
                
                current_price = price_data.get("price")
                if not current_price:
                    return {"error": f"Could not determine current price for {symbol}"}
                
                # Execute the sell
                result = await self.portfolio_manager.sell_stock(symbol, quantity)
                
                if "error" in result:
                    return result
                
                # Add current price to the result
                result["price"] = current_price
                result["total_value"] = current_price * quantity
                
                return result
            except Exception as e:
                return {"error": str(e)}
        
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
                
                # Create the initial message with system prompt
                messages = [
                    {"role": "system", "content": self.system_prompt}
                ]
                
                # Add conversation history if provided
                if conversation_history and len(conversation_history) > 0:
                    # Only include the last 15 messages to avoid token limits but ensure context
                    recent_history = conversation_history[-15:] if len(conversation_history) > 15 else conversation_history
                    for msg in recent_history:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        
                        # Only add valid messages
                        if role in ["user", "assistant", "system"] and content:
                            messages.append({"role": role, "content": content})
                
                # Add the current user message with context
                messages.append({"role": "user", "content": context_prompt})
                
                # Make the API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=2048
                )
                
                # Initialize tracking variables
                function_called = None
                function_response = None
                all_function_calls = []
                
                # Process the response in a loop to handle multiple function calls
                # This allows the model to decide when it's done calling functions
                max_function_calls = 8  # Increased limit for complex requests
                function_call_count = 0
                current_response = response
                
                while function_call_count < max_function_calls:
                    response_message = current_response.choices[0].message
                    
                    # Add the assistant's response to the conversation
                    messages.append(response_message)
                    
                    # Check if the model wants to call functions
                    if not response_message.tool_calls or len(response_message.tool_calls) == 0:
                        # No more function calls, we're done
                        break
                    
                    # Process all tool calls in this response
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        function_call_count += 1
                        
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
                        
                        # Track all function calls
                        all_function_calls.append({
                            "name": function_name,
                            "args": function_args,
                            "response": function_response
                        })
                        
                        # Convert function response to string safely
                        try:
                            function_response_str = json.dumps(function_response)
                        except (TypeError, ValueError) as json_error:
                            print(f"Error serializing function response: {str(json_error)}")
                            # Create a safe version of the response
                            safe_response = {"error": "Could not serialize function response"}
                            function_response = safe_response
                            function_response_str = json.dumps(safe_response)
                        
                        # Add function result to the conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": function_response_str
                        })
                    
                    # If we've reached the max number of function calls, break the loop
                    if function_call_count >= max_function_calls:
                        break
                    
                    # Get a new response from the model to see if it wants to call more functions
                    current_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.2,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=2048
                    )
                
                # Get the final response after all function calls
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=2048
                )
                
                # Return the final response with all function calls
                return {
                    "response": final_response.choices[0].message.content,
                    "function_called": function_called,  # Return the last function called for backward compatibility
                    "function_response": function_response,  # Return the last function response for backward compatibility
                    "all_function_calls": all_function_calls,  # Return all function calls
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
                        "all_function_calls": [],
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