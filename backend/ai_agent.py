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
    def __init__(self, portfolio_manager, market_service, market_context_service, db_service=None):
        self.portfolio_manager = portfolio_manager
        self.market_service = market_service
        self.market_context_service = market_context_service
        self.db_service = db_service
        
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
            'create_action': self._create_action,
            'list_actions': self._list_actions,
            'update_action': self._update_action,
            'cancel_action': self._cancel_action,
            'comprehensive_analysis': self._comprehensive_analysis,
            'get_financial_statements': self._get_financial_statements,
            'analyze_company_fundamentals': self._analyze_company_fundamentals,
            'compare_financial_metrics': self._compare_financial_metrics,
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
            },
            {
                "name": "create_action",
                "description": "Create a background action (rule) to monitor market events and execute trades/notifications",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "action_type": {"type": "string", "description": "BUY | SELL | NOTIFY"},
                        "symbol": {"type": "string"},
                        "quantity": {"type": "number"},
                        "amount_usd": {"type": "number"},
                        "trigger_type": {"type": "string", "description": "price_above | price_below | change_pct | time_of_day"},
                        "trigger_params": {"type": "object"},
                        "valid_until": {"type": "string"},
                        "cooldown_seconds": {"type": "number"},
                        "max_executions": {"type": "number"},
                        "notes": {"type": "string"}
                    },
                    "required": ["user_id", "action_type", "trigger_type", "trigger_params"]
                }
            },
            {
                "name": "list_actions",
                "description": "List existing actions for the user with optional filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "status": {"type": "string"},
                        "symbol": {"type": "string"},
                        "action_type": {"type": "string"},
                        "trigger_type": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "update_action",
                "description": "Update an existing action (pause/resume/edit)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "action_id": {"type": "string"},
                        "patch": {"type": "object"}
                    },
                    "required": ["user_id", "action_id", "patch"]
                }
            },
            {
                "name": "cancel_action",
                "description": "Cancel an action (soft delete)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "action_id": {"type": "string"}
                    },
                    "required": ["user_id", "action_id"]
                }
            },
            {
                "name": "comprehensive_analysis",
                "description": "Get a comprehensive portfolio and market analysis by calling multiple functions automatically",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID for portfolio analysis"},
                        "include_market_news": {"type": "boolean", "default": True, "description": "Include market news in analysis"},
                        "include_suggestions": {"type": "boolean", "default": True, "description": "Include investment suggestions"}
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_financial_statements",
                "description": "Get comprehensive financial statements (income statement, balance sheet, cash flow) for a company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL, GOOGL)"},
                        "statement_type": {"type": "string", "enum": ["income", "balance", "cash_flow", "all"], "default": "all", "description": "Type of financial statement"},
                        "period": {"type": "string", "enum": ["annual", "quarterly"], "default": "annual", "description": "Reporting period"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "analyze_company_fundamentals",
                "description": "Get AI-powered analysis of a company's financial health and investment potential using latest financial data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock symbol to analyze"},
                        "analysis_type": {"type": "string", "enum": ["comprehensive", "profitability", "liquidity", "solvency"], "default": "comprehensive", "description": "Type of analysis"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "compare_financial_metrics",
                "description": "Compare key financial metrics between multiple companies",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbols": {"type": "array", "items": {"type": "string"}, "description": "List of stock symbols to compare"},
                        "metrics": {"type": "array", "items": {"type": "string"}, "description": "Specific metrics to compare (optional)"}
                    },
                    "required": ["symbols"]
                }
            }
        ]

    # Function implementations
    async def _get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """Get real portfolio summary for user from DB + market service"""
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            portfolios = await self.db_service.get_user_portfolios(user_id)
            if not portfolios:
                return {"error": "No portfolio found for this user"}
            portfolio = portfolios[0]
            holdings = await self.db_service.get_portfolio_holdings(portfolio['id'])
            symbols = [h['symbol'] for h in holdings] if holdings else []
            market_quotes = await self.market_service.get_portfolio_quotes(symbols) if symbols else {}

            total_value = 0.0
            total_cost = 0.0
            holdings_out = []
            for h in holdings:
                symbol = h['symbol'].upper()
                shares = float(h['shares'])
                avg_cost = float(h['average_cost'])
                current_price = float(market_quotes.get(symbol, {}).get('price', avg_cost))
                market_value = shares * current_price
                cost_basis = shares * avg_cost
                total_value += market_value
                total_cost += cost_basis
                pnl = market_value - cost_basis
                pnl_percent = (pnl / cost_basis * 100) if cost_basis > 0 else 0
                holdings_out.append({
                    "symbol": symbol,
                    "shares": shares,
                    "average_cost": avg_cost,
                    "current_price": current_price,
                    "market_value": market_value,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent
                })

            total_pnl = total_value - total_cost
            total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
            total_account_value = total_value + float(portfolio['cash_balance'])

            return {
                "portfolio_summary": {
                    "total_portfolio_value": total_value,
                    "total_pnl": total_pnl,
                    "total_pnl_percent": total_pnl_percent,
                    "cash_balance": float(portfolio['cash_balance']),
                    "total_account_value": total_account_value,
                    "holdings_count": len(holdings_out)
                },
                "holdings": holdings_out
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price"""
        try:
            price_data = await self.market_service.get_stock_quote(symbol.upper())
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
            if not self.market_context_service:
                return {"error": "Market context service unavailable"}
            news = await self.market_context_service.get_market_news()
            return news
        except Exception as e:
            return {"error": str(e)}

    async def _get_portfolio_performance(self, user_id: str, period: str = "30d") -> Dict[str, Any]:
        """Simplified performance using current vs cost basis"""
        try:
            summary = await self._get_portfolio_summary(user_id)
            if "error" in summary:
                return summary
            return {"performance": summary.get("portfolio_summary"), "holdings": summary.get("holdings")}
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
        """Execute a real buy order via database and market services"""
        try:
            if not self.db_service:
                return {"error": "Database not available", "success": False}
            # Resolve portfolio
            portfolios = await self.db_service.get_user_portfolios(user_id)
            if not portfolios:
                return {"error": "No portfolio found for this user", "success": False}
            portfolio_id = portfolios[0]["id"]

            # Fetch current price
            quote = await self.market_service.get_stock_quote(symbol.upper())
            current_price = float(quote.get("price", 0))
            if not current_price or current_price <= 0:
                return {"error": f"Could not get price for {symbol}", "success": False}

            # Execute buy
            result = await self.db_service.execute_buy_order(portfolio_id, user_id, symbol.upper(), float(quantity), current_price)

            return {
                "success": True,
                "action": "BUY",
                "symbol": symbol.upper(),
                "quantity": float(quantity),
                "price": current_price,
                "new_cash_balance": result.get("new_cash_balance"),
                "transaction": result.get("transaction"),
                "holding": result.get("holding"),
                "message": f"Bought {quantity} shares of {symbol.upper()} at ${current_price:.2f}"
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def _sell_stock(self, user_id: str, symbol: str, quantity: float) -> Dict[str, Any]:
        """Execute a real sell order via database"""
        try:
            if not self.db_service:
                return {"error": "Database not available", "success": False}
            portfolios = await self.db_service.get_user_portfolios(user_id)
            if not portfolios:
                return {"error": "No portfolio found for this user", "success": False}
            portfolio_id = portfolios[0]["id"]

            # Fetch current price
            quote = await self.market_service.get_stock_quote(symbol.upper())
            current_price = float(quote.get("price", 0))
            if not current_price or current_price <= 0:
                return {"error": f"Could not get price for {symbol}", "success": False}

            result = await self.db_service.execute_sell_order(portfolio_id, user_id, symbol.upper(), float(quantity), current_price)

            return {
                "success": True,
                "action": "SELL",
                "symbol": symbol.upper(),
                "quantity": float(quantity),
                "price": current_price,
                "new_cash_balance": result.get("new_cash_balance"),
                "transaction": result.get("transaction"),
                "message": f"Sold {quantity} shares of {symbol.upper()} at ${current_price:.2f}"
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def _get_cash_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user's cash balance from DB"""
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            portfolios = await self.db_service.get_user_portfolios(user_id)
            if not portfolios:
                return {"error": "No portfolio found"}
            return {"cash_balance": float(portfolios[0]['cash_balance'])}
        except Exception as e:
            return {"error": str(e)}
        
    async def _get_holdings(self, user_id: str) -> Dict[str, Any]:
        """Get user's holdings from DB with current prices"""
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            portfolios = await self.db_service.get_user_portfolios(user_id)
            if not portfolios:
                return {"error": "No portfolio found"}
            portfolio_id = portfolios[0]['id']
            holdings = await self.db_service.get_portfolio_holdings(portfolio_id)
            symbols = [h['symbol'] for h in holdings] if holdings else []
            quotes = await self.market_service.get_portfolio_quotes(symbols) if symbols else {}
            enriched = []
            for h in holdings:
                sym = h['symbol'].upper()
                price = float(quotes.get(sym, {}).get('price', h['average_cost']))
                enriched.append({
                    "symbol": sym,
                    "shares": float(h['shares']),
                    "average_cost": float(h['average_cost']),
                    "current_price": price
                })
            return {"holdings": enriched}
        except Exception as e:
            return {"error": str(e)}
        
    async def _get_transaction_history(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get transaction history from DB"""
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            portfolios = await self.db_service.get_user_portfolios(user_id)
            if not portfolios:
                return {"error": "No portfolio found"}
            portfolio_id = portfolios[0]['id']
            txs = await self.db_service.get_portfolio_transactions(portfolio_id, limit=limit)
            return {"transactions": txs}
        except Exception as e:
            return {"error": str(e)}

    # Actions automation handlers
    async def _create_action(self, user_id: str, action_type: str, trigger_type: str, trigger_params: Dict[str, Any], symbol: Optional[str] = None, quantity: Optional[float] = None, amount_usd: Optional[float] = None, valid_until: Optional[str] = None, cooldown_seconds: Optional[int] = None, max_executions: Optional[int] = 1, notes: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            if action_type.upper() in ["BUY", "SELL"] and not (quantity or amount_usd):
                return {"error": "BUY/SELL requires quantity or amount_usd"}
            action = {
                'user_id': user_id,
                'status': 'active',
                'action_type': action_type.upper(),
                'symbol': symbol.upper() if symbol else None,
                'quantity': quantity,
                'amount_usd': amount_usd,
                'trigger_type': trigger_type,
                'trigger_params': trigger_params,
                'valid_until': valid_until,
                'max_executions': max_executions or 1,
                'cooldown_seconds': cooldown_seconds,
                'notes': notes
            }
            created = await self.db_service.create_action(action)
            # Add to watchlist
            if created.get('symbol'):
                self.market_service.add_to_watchlist([created['symbol']])
            return {"success": True, "action": created}
        except Exception as e:
            return {"error": str(e)}

    async def _list_actions(self, user_id: str, status: Optional[str] = None, symbol: Optional[str] = None, action_type: Optional[str] = None, trigger_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            filters = {k: v for k, v in {
                'status': status,
                'symbol': symbol.upper() if symbol else None,
                'action_type': action_type,
                'trigger_type': trigger_type
            }.items() if v is not None}
            actions = await self.db_service.get_actions(user_id, filters)
            return {"actions": actions}
        except Exception as e:
            return {"error": str(e)}

    async def _update_action(self, user_id: str, action_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            updated = await self.db_service.update_action(action_id, user_id, patch)
            if not updated:
                return {"error": "Action not found or nothing to update"}
            return {"success": True, "action": updated}
        except Exception as e:
            return {"error": str(e)}

    async def _cancel_action(self, user_id: str, action_id: str) -> Dict[str, Any]:
        try:
            if not self.db_service:
                return {"error": "Database not available"}
            ok = await self.db_service.cancel_action(action_id, user_id)
            if not ok:
                return {"error": "Action not found"}
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    async def _comprehensive_analysis(self, user_id: str, include_market_news: bool = True, include_suggestions: bool = True) -> Dict[str, Any]:
        """Comprehensive analysis that demonstrates multiple function calls"""
        try:
            analysis_results = {}
            
            # Get portfolio summary
            portfolio_summary = await self._get_portfolio_summary(user_id)
            analysis_results["portfolio_summary"] = portfolio_summary
            
            # Get recent transactions
            transaction_history = await self._get_transaction_history(user_id, limit=5)
            analysis_results["recent_transactions"] = transaction_history
            
            # Get market news if requested
            if include_market_news:
                market_news = await self._get_market_news()
                analysis_results["market_news"] = market_news
            
            # Get market indicators
            market_indicators = await self._get_market_indicators()
            analysis_results["market_indicators"] = market_indicators
            
            # Compile analysis summary
            analysis_summary = {
                "analysis_type": "comprehensive_portfolio_analysis",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "functions_called": ["get_portfolio_summary", "get_transaction_history"],
                "data": analysis_results
            }
            
            if include_market_news:
                analysis_summary["functions_called"].append("get_market_news")
            
            analysis_summary["functions_called"].append("get_market_indicators")
            
            return analysis_summary
            
        except Exception as e:
            return {"error": str(e)}

    async def _get_financial_statements(self, symbol: str, statement_type: str = "all", period: str = "annual") -> Dict[str, Any]:
        """Get financial statements for a company"""
        try:
            symbol = symbol.upper()
            results = {
                "symbol": symbol,
                "period": period,
                "timestamp": datetime.now().isoformat(),
                "statements": {}
            }
            
            if statement_type in ["income", "all"]:
                income_data = await self.market_service.get_income_statement(symbol, period)
                results["statements"]["income_statement"] = income_data
            
            if statement_type in ["balance", "all"]:
                balance_data = await self.market_service.get_balance_sheet(symbol, period)
                results["statements"]["balance_sheet"] = balance_data
            
            if statement_type in ["cash_flow", "all"]:
                cash_flow_data = await self.market_service.get_cash_flow(symbol, period)
                results["statements"]["cash_flow"] = cash_flow_data
            
            return results
            
        except Exception as e:
            return {"error": str(e)}

    async def _analyze_company_fundamentals(self, symbol: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """AI-powered analysis of company financial health"""
        try:
            symbol = symbol.upper()
            
            # Get financial statements
            financial_data = await self._get_financial_statements(symbol, "all", "annual")
            
            if "error" in financial_data:
                return financial_data
            
            # Get current stock price for context
            price_data = await self.market_service.get_stock_quote(symbol)
            
            # Extract key metrics for analysis
            analysis_results = {
                "symbol": symbol,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "current_price": price_data.get("price") if price_data else None,
                "financial_health": {},
                "key_metrics": {},
                "ai_insights": {},
                "raw_data": financial_data
            }
            
            # Extract and calculate key financial ratios
            statements = financial_data.get("statements", {})
            
            # Income statement metrics
            if "income_statement" in statements and statements["income_statement"] and not statements["income_statement"].get("error"):
                income_data = statements["income_statement"]
                if "income_statement" in income_data and income_data["income_statement"]:
                    latest_income = income_data["income_statement"][0] if isinstance(income_data["income_statement"], list) else income_data["income_statement"]
                    
                    analysis_results["key_metrics"]["revenue"] = latest_income.get("revenue")
                    analysis_results["key_metrics"]["net_income"] = latest_income.get("net_income")
                    analysis_results["key_metrics"]["gross_profit"] = latest_income.get("gross_profit")
                    analysis_results["key_metrics"]["operating_income"] = latest_income.get("operating_income")
                    
                    # Calculate profit margins
                    revenue = float(latest_income.get("revenue", 0)) if latest_income.get("revenue") else 0
                    if revenue > 0:
                        net_income = float(latest_income.get("net_income", 0)) if latest_income.get("net_income") else 0
                        gross_profit = float(latest_income.get("gross_profit", 0)) if latest_income.get("gross_profit") else 0
                        
                        analysis_results["key_metrics"]["net_profit_margin"] = round((net_income / revenue) * 100, 2)
                        analysis_results["key_metrics"]["gross_profit_margin"] = round((gross_profit / revenue) * 100, 2)
            
            # Balance sheet metrics
            if "balance_sheet" in statements and statements["balance_sheet"] and not statements["balance_sheet"].get("error"):
                balance_data = statements["balance_sheet"]
                if "balance_sheet" in balance_data and balance_data["balance_sheet"]:
                    latest_balance = balance_data["balance_sheet"][0] if isinstance(balance_data["balance_sheet"], list) else balance_data["balance_sheet"]
                    
                    total_assets = latest_balance.get("assets", {}).get("total_assets")
                    total_liabilities = latest_balance.get("liabilities", {}).get("total_liabilities")
                    shareholders_equity = latest_balance.get("shareholders_equity", {}).get("total_shareholders_equity")
                    
                    analysis_results["key_metrics"]["total_assets"] = total_assets
                    analysis_results["key_metrics"]["total_liabilities"] = total_liabilities
                    analysis_results["key_metrics"]["shareholders_equity"] = shareholders_equity
                    
                    # Calculate key ratios
                    if total_assets and total_liabilities and shareholders_equity:
                        debt_to_equity = float(total_liabilities) / float(shareholders_equity) if float(shareholders_equity) != 0 else None
                        if debt_to_equity:
                            analysis_results["key_metrics"]["debt_to_equity_ratio"] = round(debt_to_equity, 2)
            
            # Generate AI insights based on analysis type
            if analysis_type == "comprehensive":
                analysis_results["ai_insights"]["summary"] = f"Comprehensive financial analysis for {symbol}"
                analysis_results["ai_insights"]["strengths"] = []
                analysis_results["ai_insights"]["concerns"] = []
                analysis_results["ai_insights"]["recommendation"] = "NEUTRAL"  # Will be enhanced with LLM analysis
                
                # Basic ratio analysis
                net_margin = analysis_results["key_metrics"].get("net_profit_margin")
                debt_ratio = analysis_results["key_metrics"].get("debt_to_equity_ratio")
                
                if net_margin and net_margin > 10:
                    analysis_results["ai_insights"]["strengths"].append("Strong profit margins")
                elif net_margin and net_margin < 5:
                    analysis_results["ai_insights"]["concerns"].append("Low profit margins")
                
                if debt_ratio and debt_ratio < 0.5:
                    analysis_results["ai_insights"]["strengths"].append("Conservative debt levels")
                elif debt_ratio and debt_ratio > 2.0:
                    analysis_results["ai_insights"]["concerns"].append("High debt levels")
            
            return analysis_results
            
        except Exception as e:
            return {"error": str(e)}

    async def _compare_financial_metrics(self, symbols: List[str], metrics: List[str] = None) -> Dict[str, Any]:
        """Compare financial metrics across multiple companies"""
        try:
            if not symbols or len(symbols) < 2:
                return {"error": "At least 2 symbols required for comparison"}
            
            comparison_results = {
                "symbols": [s.upper() for s in symbols],
                "timestamp": datetime.now().isoformat(),
                "comparison_data": {},
                "rankings": {},
                "summary": {}
            }
            
            # Get financial data for each symbol
            for symbol in symbols:
                symbol = symbol.upper()
                try:
                    financial_data = await self._analyze_company_fundamentals(symbol, "comprehensive")
                    comparison_results["comparison_data"][symbol] = financial_data
                except Exception as e:
                    comparison_results["comparison_data"][symbol] = {"error": str(e)}
            
            # Extract key metrics for comparison
            metrics_to_compare = metrics or ["revenue", "net_income", "net_profit_margin", "debt_to_equity_ratio", "total_assets"]
            
            for metric in metrics_to_compare:
                metric_values = {}
                for symbol in symbols:
                    symbol = symbol.upper()
                    company_data = comparison_results["comparison_data"].get(symbol, {})
                    if "key_metrics" in company_data:
                        metric_value = company_data["key_metrics"].get(metric)
                        if metric_value is not None:
                            metric_values[symbol] = metric_value
                
                if metric_values:
                    # Rank companies by this metric
                    sorted_companies = sorted(metric_values.items(), key=lambda x: x[1], reverse=True)
                    comparison_results["rankings"][metric] = sorted_companies
            
            # Generate comparison summary
            comparison_results["summary"]["total_companies"] = len(symbols)
            comparison_results["summary"]["successful_analyses"] = len([c for c in comparison_results["comparison_data"].values() if "error" not in c])
            comparison_results["summary"]["metrics_compared"] = len(comparison_results["rankings"])
            
            return comparison_results
            
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
 Be helpful, accurate, and provide actionable insights.
  CRITICAL STYLE RULES:
  - Keep responses concise (aim for 2-6 short sentences). Prefer brevity, but do not omit valuable details or cut off mid-thought. If additional content is essential (e.g., key numbers or steps), include it.
 - Prefer short bullet points over paragraphs when listing items.
 - When providing numbers, round reasonably and avoid excessive verbosity.
 - If a function was called, summarize the key results succinctly.

 TOOL USE POLICY (IMPORTANT):
 - Whenever the user asks for portfolio values, holdings, transactions, stock prices, market news/context, or FINANCIAL ANALYSIS, CALL THE RELEVANT FUNCTION(s) provided instead of guessing.
 - Use functions even if you believe you already know the answer. Prioritize fresh data via tools.
 - You can call MULTIPLE FUNCTIONS in a single response to complete complex tasks efficiently.
 - For multi-step requests (e.g., "find health stocks and buy with $500"), use multiple functions: search_stocks, get_cash_balance, buy_stock, get_portfolio_summary.
 - For financial analysis requests, use: get_financial_statements, analyze_company_fundamentals, compare_financial_metrics.
 - FINANCIAL CAPABILITIES: You can analyze income statements, balance sheets, cash flows, calculate ratios, and provide investment insights.
 - After function results are available, give a concise summary of the outcome.
 CONTENT SCOPE:
 - For portfolio summaries, include totals and at most 3 notable holdings (e.g., largest position or top movers). Do not list every holding unless asked.
 - Prefer one-sentence headlines followed by 2-4 bullet points.
 """
            }
        ]
        
        if conversation_history:
            # Add recent conversation history
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                    messages.append(msg)
        
        return messages

    async def chat(self, message: str, conversation_history: Optional[List[Dict]] = None, attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
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
            
            # Prepare user message content
            user_content = message
            
            # Handle file attachments for GPT-4V
            if attachments and len(attachments) > 0:
                content_parts = [{"type": "text", "text": message}]
                
                for attachment in attachments:
                    if attachment['content_type'].startswith('image/'):
                        # Handle image files for vision analysis
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{attachment['content_type']};base64,{attachment['content']}"
                            }
                        })
                    else:
                        # Handle document files (PDFs, DOCX, etc.)
                        content_parts[0]["text"] += f"\n\n[Attached file: {attachment['filename']} ({attachment['content_type']})]"
                
                user_content = content_parts
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_content
            })
            
            # Make the API call with function calling using modern tools API
            tools = [{"type": "function", "function": func_def} for func_def in self.function_definitions]
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=700
            )
            
            message_content = response.choices[0].message
            function_calls = []
            
            # Handle multiple tool calls (modern OpenAI API)
            if getattr(message_content, 'tool_calls', None):
                # Process each tool call
                for tool_call in message_content.tool_calls:
                    if tool_call.type == "function":
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Add user_id to function arguments if not present but required
                        if function_name in ['get_portfolio_summary', 'get_portfolio_performance', 'buy_stock', 'sell_stock', 'get_cash_balance', 'get_holdings', 'get_transaction_history', 'create_action', 'list_actions', 'update_action', 'cancel_action']:
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
                                
                            except Exception as e:
                                logger.error(f"Function execution error for {function_name}: {e}")
                                function_result = {"error": str(e)}
                                
                                function_call_info = FunctionCall(
                                    name=function_name,
                                    arguments=function_args,
                                    result=function_result,
                                    timestamp=datetime.now().isoformat()
                                )
                                function_calls.append(function_call_info)
                        else:
                            function_result = {"error": "Function not available"}
                            function_call_info = FunctionCall(
                                name=function_name,
                                arguments=function_args,
                                result=function_result,
                                timestamp=datetime.now().isoformat()
                            )
                            function_calls.append(function_call_info)
                
                # If we have function calls, continue conversation with results
                if function_calls:
                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in message_content.tool_calls]
                    })
                    
                    # Add function results as tool messages
                    for i, function_call in enumerate(function_calls):
                        messages.append({
                            "role": "tool",
                            "tool_call_id": message_content.tool_calls[i].id,
                            "content": json.dumps(function_call.result, default=str)
                        })
                    
                    # Get the final response with function results
                    final_response = await self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=600
                    )
                    
                    final_content = final_response.choices[0].message.content
                else:
                    final_content = "I encountered an issue processing your request. Please try again."
            else:
                final_content = message_content.content
            
            # Return the structured response
            return {
                "response": final_content,
                "timestamp": datetime.now().isoformat(),
                "function_called": function_calls[0].name if function_calls else None,
                "function_response": function_calls[0].result if function_calls else None,
                "attachments_processed": len(attachments) if attachments else 0,
                "attachment_info": [{"filename": att["filename"], "type": att["content_type"]} for att in attachments] if attachments else [],
                "all_function_calls": [
                    {
                        "name": fc.name,
                        "arguments": fc.arguments,
                        "result": fc.result,
                        "response": fc.result,  # alias for frontend compatibility
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