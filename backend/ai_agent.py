"""
AI Portfolio Agent - Enhanced with market context and intelligent routing
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import inspect

from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FunctionCall:
    name: str
    arguments: Dict[str, Any]
    result: Any
    timestamp: str
    
class AIPortfolioAgent:
    def __init__(self, portfolio_manager, market_service, market_context_service):
        self.portfolio_manager = portfolio_manager
        self.market_service = market_service
        self.market_context_service = market_context_service
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("⚠️ OpenAI API key not found. AI features will be disabled.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("✅ OpenAI client initialized with model: gpt-4o")
        
        # Available functions for the AI
        self.available_functions = {
            'get_portfolio_summary': self._get_portfolio_summary,
            'get_stock_price': self._get_stock_price,
            'search_stocks': self._search_stocks,
            'get_market_news': self._get_market_news,
            'get_portfolio_performance': self._get_portfolio_performance,
            'get_stock_analysis': self._get_stock_analysis,
            'get_market_indicators': self._get_market_indicators,
            'buy_stock': self._buy_stock,
            'sell_stock': self._sell_stock,
            'get_cash_balance': self._get_cash_balance,
            'get_holdings': self._get_holdings,
            'get_transaction_history': self._get_transaction_history,
        }
        
        # Function definitions for OpenAI
        self.function_definitions = [
    {
        "name": "get_portfolio_summary",
                "description": "Get a complete overview of the user's portfolio including total value, holdings, and performance",
        "parameters": {
            "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to get portfolio for"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_stock_price",
                "description": "Get current price and details for a specific stock symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                            "description": "Stock symbol (e.g., AAPL, GOOGL)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
                "name": "search_stocks",
                "description": "Search for stocks by company name or symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                            "description": "Search term (company name or stock symbol)"
                }
            },
            "required": ["query"]
        }
    },
    {
                "name": "get_market_news",
                "description": "Get latest market news and analysis",
        "parameters": {
            "type": "object",
            "properties": {
                        "category": {
                    "type": "string",
                            "description": "News category (general, technology, finance, etc.)",
                            "default": "general"
                        }
                    }
                }
            },
            {
                "name": "get_portfolio_performance",
                "description": "Get detailed performance metrics for the user's portfolio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to get performance for"
                        },
                        "period": {
                            "type": "string",
                            "description": "Time period for performance analysis (1d, 7d, 30d, 1y)",
                            "default": "30d"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_stock_analysis",
                "description": "Get detailed analysis and recommendations for a specific stock",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                            "description": "Stock symbol to analyze"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_market_indicators",
                "description": "Get current market indicators and economic data",
        "parameters": {
                    "type": "object",
                    "properties": {
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific indicators to retrieve (optional)"
                        }
                    }
                }
            },
            {
                "name": "buy_stock",
                "description": "Execute a buy order for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID placing the order"
                        },
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol to buy"
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Number of shares to buy"
                        }
                    },
                    "required": ["user_id", "symbol", "quantity"]
                }
            },
            {
                "name": "sell_stock",
                "description": "Execute a sell order for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID placing the order"
                        },
                "symbol": {
                    "type": "string",
                            "description": "Stock symbol to sell"
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Number of shares to sell"
                        }
                    },
                    "required": ["user_id", "symbol", "quantity"]
                }
            },
            {
                "name": "get_cash_balance",
                "description": "Get the user's current cash balance",
        "parameters": {
            "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to get cash balance for"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_holdings",
                "description": "Get all current stock holdings for the user",
        "parameters": {
            "type": "object",
            "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to get holdings for"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_transaction_history",
                "description": "Get transaction history for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to get transactions for"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of transactions to return",
                            "default": 10
                        }
                    },
                    "required": ["user_id"]
                }
            }
        ]

    # Function implementations
    async def _get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """Get portfolio summary for user"""
        try:
            # This would typically get data from the database
            # For now, return a placeholder
            return {
                "user_id": user_id,
                "total_value": 10000.0,
                "cash_balance": 5000.0,
                "holdings_count": 0,
                "message": "Portfolio data would be retrieved from database"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price"""
        try:
            price_data = await self.market_service.get_stock_price(symbol)
            return price_data
        except Exception as e:
            return {"error": str(e)}

    async def _search_stocks(self, query: str) -> Dict[str, Any]:
        """Search for stocks"""
        try:
            results = await self.market_service.search_stocks(query)
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}

    async def _get_market_news(self, category: str = "general") -> Dict[str, Any]:
        """Get market news"""
        try:
            # This would get news from the market context service
            return {
                "category": category,
                "news": [],
                "message": "News data would be retrieved from market context service"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_portfolio_performance(self, user_id: str, period: str = "30d") -> Dict[str, Any]:
        """Get portfolio performance metrics"""
        try:
            return {
                "user_id": user_id,
                "period": period,
                "performance": "Performance data would be calculated",
                "message": "Portfolio performance would be retrieved from database"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_stock_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get stock analysis"""
        try:
            return {
                "symbol": symbol,
                "analysis": "Stock analysis would be performed",
                "message": "Stock analysis data would be retrieved"
            }
        except Exception as e:
            return {"error": str(e)}
        
    async def _get_market_indicators(self, indicators: List[str] = None) -> Dict[str, Any]:
        """Get market indicators"""
        try:
            return {
                "indicators": indicators or [],
                "data": {},
                "message": "Market indicators would be retrieved"
            }
        except Exception as e:
            return {"error": str(e)}
        
    async def _buy_stock(self, user_id: str, symbol: str, quantity: float) -> Dict[str, Any]:
        """Execute buy order"""
        try:
            return {
                "user_id": user_id,
                "symbol": symbol,
                "quantity": quantity,
                "message": "Buy order would be executed",
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def _sell_stock(self, user_id: str, symbol: str, quantity: float) -> Dict[str, Any]:
        """Execute sell order"""
        try:
            return {
                "user_id": user_id,
                "symbol": symbol,
                "quantity": quantity,
                "message": "Sell order would be executed",
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def _get_cash_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user's cash balance"""
        try:
            return {
                "user_id": user_id,
                "cash_balance": 5000.0,
                "message": "Cash balance would be retrieved from database"
            }
        except Exception as e:
            return {"error": str(e)}
        
    async def _get_holdings(self, user_id: str) -> Dict[str, Any]:
        """Get user's holdings"""
        try:
            return {
                "user_id": user_id,
                "holdings": [],
                "message": "Holdings would be retrieved from database"
            }
        except Exception as e:
            return {"error": str(e)}
        
    async def _get_transaction_history(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get transaction history"""
        try:
            return {
                "user_id": user_id,
                "limit": limit,
                "transactions": [],
                "message": "Transaction history would be retrieved from database"
            }
        except Exception as e:
            return {"error": str(e)}
        
    async def _build_market_context(self) -> str:
        """Build market context for AI"""
        try:
            if self.market_context_service:
                context = await self.market_context_service.get_market_context([])
                return f"Market Context: {json.dumps(context, default=str)}"
            return "Market context unavailable"
        except Exception as e:
            return f"Market context error: {str(e)}"

    async def _prepare_conversation_history(self, conversation_history: Optional[List[Dict]], context: str, user_id: str) -> List[Dict]:
        """Prepare conversation history for AI"""
        messages = [
            {
                "role": "system",
                "content": f"""You are a professional AI investment assistant for ProCogia's Portfolio Management platform.
                
User ID: {user_id}
{context}

You help users understand their investment portfolio performance using real-time market data and intelligent analysis.
Be helpful, accurate, and provide actionable insights."""
            }
        ]
        
        if conversation_history:
            # Add recent conversation history
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                    messages.append(msg)
        
        return messages

    async def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Enhanced chat function with intelligent routing and context awareness
        """
        if not self.client:
            return {
                "response": "🤖 I'm sorry, but AI features are currently unavailable. Please configure the OpenAI API key to enable AI assistance.",
                "timestamp": datetime.now().isoformat(),
                "function_called": None,
                "function_response": None,
                "all_function_calls": []
            }
        
        try:
            # Get user ID from portfolio manager
            user_id = self.portfolio_manager.user_id
            
            # Build context for the AI
            context = await self._build_market_context()
            
            # Prepare conversation history
            messages = await self._prepare_conversation_history(conversation_history, context, user_id)
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Make the API call with function calling
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                    messages=messages,
                functions=self.function_definitions,
                function_call="auto",
                temperature=0.7,
                max_tokens=2000
            )
            
            message_content = response.choices[0].message
            function_calls = []
            
            # Handle function calls
            if message_content.function_call:
                function_call = message_content.function_call
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)
                
                # Add user_id to function arguments if not present but required
                if function_name in ['get_portfolio_summary', 'get_portfolio_performance', 'buy_stock', 'sell_stock', 'get_cash_balance', 'get_holdings', 'get_transaction_history']:
                    if 'user_id' not in function_args:
                        function_args['user_id'] = user_id
                
                # Execute the function
                if function_name in self.available_functions:
                    try:
                        if inspect.iscoroutinefunction(self.available_functions[function_name]):
                            function_result = await self.available_functions[function_name](**function_args)
                        else:
                            function_result = self.available_functions[function_name](**function_args)
                        
                        function_call_info = FunctionCall(
                            name=function_name,
                            arguments=function_args,
                            result=function_result,
                            timestamp=datetime.now().isoformat()
                        )
                        function_calls.append(function_call_info)
                        
                        # Continue conversation with function result
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "function_call": {
                            "name": function_name,
                                "arguments": function_call.arguments
                            }
                        })
                        
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": json.dumps(function_result, default=str)
                        })
                        
                        # Get the final response
                        final_response = await self.client.chat.completions.create(
                            model="gpt-4o",
                        messages=messages,
                            temperature=0.7,
                            max_tokens=1500
                        )
                        
                                                final_content = final_response.choices[0].message.content
                    except Exception as e:
                        logger.error(f"Function execution error: {e}")
                        final_content = f"I encountered an error while executing {function_name}. Please try again or rephrase your request."
                        function_result = {"error": str(e)}
                        
                        function_call_info = FunctionCall(
                            name=function_name,
                            arguments=function_args,
                            result=function_result,
                            timestamp=datetime.now().isoformat()
                        )
                        function_calls.append(function_call_info)
                else:
                    final_content = f"I don't have access to the function '{function_name}'. Please try a different request."
                    function_result = {"error": "Function not available"}
                    function_call_info = FunctionCall(
                        name=function_name,
                        arguments=function_args,
                        result=function_result,
                        timestamp=datetime.now().isoformat()
                    )
                    function_calls.append(function_call_info)
            else:
                final_content = message_content.content
            
            # Return the structured response
            return {
                "response": final_content,
                "timestamp": datetime.now().isoformat(),
                "function_called": function_calls[0].name if function_calls else None,
                "function_response": function_calls[0].result if function_calls else None,
                "all_function_calls": [
                    {
                        "name": fc.name,
                        "arguments": fc.arguments,
                        "result": fc.result,
                        "timestamp": fc.timestamp
                    } for fc in function_calls
                ]
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": f"🤖 I apologize, but I encountered an error: {str(e)}. Please try again.",
                "timestamp": datetime.now().isoformat(),
                "function_called": None,
                "function_response": None,
                "all_function_calls": []
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of AI agent"""
        return {
            "status": "healthy" if self.client else "error",
            "error": None if self.client else "OpenAI API key not configured",
            "model": "gpt-4o" if self.client else None
        } 