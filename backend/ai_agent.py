"""
AI Agent integration with Google Gemini for portfolio analysis
"""
import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from portfolio import PortfolioManager
from market_data import MarketDataService

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
    }
]

class AIPortfolioAgent:
    def __init__(self, portfolio_manager: PortfolioManager, market_service: MarketDataService):
        self.portfolio_manager = portfolio_manager
        self.market_service = market_service
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use gemini-1.5-pro for function calling support
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            self.model = None
        
        # System prompt for the AI assistant
        self.system_prompt = """You are a professional AI investment assistant for ProCogia's Portfolio Management platform.

You help users understand their investment portfolio performance using real-time market data and intelligent analysis.

Your capabilities include:
- Analyzing portfolio performance and risk
- Providing insights on individual stock performance  
- Offering data-driven investment recommendations
- Explaining market trends and their impact on holdings

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
        
        # Base prompt starts with system prompt
        prompt_parts = [self.system_prompt]
        
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
                
                prompt_parts.append(context)
        
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

USER QUESTION: {user_message}

Respond with helpful information. Since the question is not about their specific portfolio,
focus on providing general advice, information, or answering their question directly.
Use the available functions when appropriate to provide accurate market data.
"""
        
        prompt_parts.append(instruction.format(user_message=user_message))
        full_prompt = "\n\n".join(prompt_parts)
        return full_prompt

    async def execute_function(self, function_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a function requested by the AI"""
        params = params or {}
        
        if function_name == "get_portfolio_summary":
            return await self.get_portfolio_data()
        
        elif function_name == "get_stock_details":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"error": "No stock symbol provided"}
            return await self.get_stock_performance_data(symbol)
        
        elif function_name == "search_stock":
            query = params.get("query", "")
            if not query:
                return {"error": "No search query provided"}
            try:
                results = await self.market_service.search_stocks(query)
                if results and len(results) > 0:
                    # Get price for the top result
                    top_symbol = results[0]["symbol"]
                    price_data = await self.market_service.get_stock_quote(top_symbol)
                    results[0]["current_price"] = price_data.get("price", "N/A")
                return {"results": results[:5]}  # Return top 5 results
            except Exception as e:
                return {"error": f"Error searching for stock: {str(e)}"}
        
        elif function_name == "calculate_portfolio_metrics":
            portfolio_data = await self.get_portfolio_data()
            if "error" in portfolio_data:
                return portfolio_data
            
            # Calculate additional metrics
            holdings = portfolio_data.get("holdings", [])
            total_value = portfolio_data["portfolio_summary"]["total_portfolio_value"]
            
            # Calculate diversification score (0-100)
            diversification_score = min(len(holdings) * 20, 100) if holdings else 0
            
            # Calculate sector distribution (simplified)
            sectors = {
                "AAPL": "Technology",
                "GOOGL": "Technology",
                "MSFT": "Technology",
                # Add more mappings as needed
            }
            
            sector_distribution = {}
            for holding in holdings:
                symbol = holding["symbol"]
                sector = sectors.get(symbol, "Other")
                value = holding["current_value"]
                if sector in sector_distribution:
                    sector_distribution[sector] += value
                else:
                    sector_distribution[sector] = value
            
            # Calculate percentages
            for sector, value in sector_distribution.items():
                sector_distribution[sector] = {
                    "value": value,
                    "percentage": (value / total_value * 100) if total_value > 0 else 0
                }
            
            return {
                "diversification_score": diversification_score,
                "risk_level": "High" if diversification_score < 40 else "Medium" if diversification_score < 70 else "Low",
                "sector_distribution": sector_distribution,
                "concentration_risk": "High" if len(holdings) < 3 else "Medium" if len(holdings) < 5 else "Low"
            }
        
        elif function_name == "get_transaction_history":
            limit = params.get("limit", 10)
            transactions = self.portfolio_manager.get_transactions()
            return {"transactions": transactions[:limit]}
        
        elif function_name == "get_historical_prices":
            symbol = params.get("symbol", "")
            days = params.get("days", 30)
            if not symbol:
                return {"error": "No stock symbol provided"}
            return await self.market_service.get_historical_data(symbol, days)
        
        elif function_name == "get_cache_stats":
            return await self.market_service.get_cache_stats()
        
        else:
            return {"error": f"Unknown function: {function_name}"}

    async def chat(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Process user message and return AI response with function calling"""
        if not self.model:
            return {
                "response": "I'm sorry, but the AI service is not configured. Please set up your Gemini API key to use the AI assistant.",
                "error": "Missing Gemini API key"
            }
        
        try:
            # Create context-aware prompt
            full_prompt = await self.format_portfolio_context(user_message)
            
            # Generate response using Gemini with function calling
            try:
                # Create a GenerationConfig object
                generation_config = genai.types.GenerationConfig(
                    temperature=0.2,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
                
                # Create safety settings
                safety_settings = [
                    {
                        "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                    },
                    {
                        "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                    },
                    {
                        "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                    },
                    {
                        "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                    }
                ]
                
                # Create a Tool object with function declarations
                tools = [genai.types.Tool(function_declarations=AI_FUNCTIONS)]
                
                # Generate content with function calling
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                    tools=tools
                )
                
                # Check if the model wants to call a function
                function_called = None
                function_response = None
                
                # Process function calls if present
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'function_call'):
                                function_call = part.function_call
                                function_name = function_call.name
                                function_args = {}
                                
                                if hasattr(function_call, 'args'):
                                    function_args = function_call.args
                                
                                print(f"Function called: {function_name} with args: {function_args}")
                                
                                # Execute the function
                                function_called = function_name
                                function_response = await self.execute_function(function_name, function_args)
                                
                                # Generate a new response with the function result
                                function_result_prompt = f"""
{full_prompt}

FUNCTION CALL RESULT:
Function: {function_name}
Result: {json.dumps(function_response, indent=2)}

Based on this information, please provide a helpful response to the user's question. Do not mention that you called a function - just use the data to give a natural, informative answer.
"""
                                response = self.model.generate_content(function_result_prompt)
            
            return {
                "response": response.text,
                    "function_called": function_called,
                    "function_response": function_response,
                    "success": True
                }
            except Exception as e:
                print(f"Function calling approach failed: {e}")
                
                # Try standard response without function calling as a fallback
                try:
                    # Configure generation parameters
                    generation_config = {
                        "temperature": 0.2,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                    
                    safety_settings = [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                    
                    response = self.model.generate_content(
                        full_prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    
                    # If the response is successful, return it
                    return {
                        "response": response.text,
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
            if not os.getenv("GEMINI_API_KEY"):
                return {
                    "status": "error",
                    "api_key_configured": False,
                    "error": "Gemini API key not configured"
                }
            
            if not self.model:
                return {
                    "status": "error", 
                    "api_key_configured": True,
                    "error": "Gemini model not initialized"
                }
            
            # Simple health check without async call
            return {
                "status": "healthy",
                "api_key_configured": True,
                "model": "gemini-1.5-pro",
                "functions_available": len(AI_FUNCTIONS),
                "ready": True
            }
        except Exception as e:
            return {
                "status": "error",
                "api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
                "error": str(e)
            } 