"""
Portfolio management logic for AI Portfolio Agent MVP
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Hardcoded portfolio data as defined in MVP
HARDCODED_PORTFOLIO = {
    "holdings": [
        {"symbol": "AAPL", "quantity": 10, "purchase_price": 150.00},
        {"symbol": "GOOGL", "quantity": 5, "purchase_price": 2500.00},
        {"symbol": "MSFT", "quantity": 8, "purchase_price": 300.00}
    ],
    "cash_balance": 5000.00,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": datetime.now().isoformat(),
    "transactions": []  # Track all buy/sell transactions
}

class PortfolioManager:
    def __init__(self, user_id=None):
        self.portfolio = HARDCODED_PORTFOLIO.copy()
        self.user_id = user_id
    
    def set_user_id(self, user_id):
        """Set the user ID for the portfolio manager"""
        self.user_id = user_id
        return self.user_id
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Get the current portfolio data"""
        return self.portfolio
    
    def get_holdings(self) -> List[Dict[str, Any]]:
        """Get list of holdings"""
        return self.portfolio["holdings"]
    
    def get_holding_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get specific holding by symbol"""
        for holding in self.portfolio["holdings"]:
            if holding["symbol"].upper() == symbol.upper():
                return holding
        return None
    
    def get_cash_balance(self) -> float:
        """Get current cash balance"""
        return self.portfolio["cash_balance"]
    
    def get_transactions(self) -> List[Dict[str, Any]]:
        """Get transaction history"""
        return self.portfolio.get("transactions", [])
    
    async def buy_stock(self, symbol: str, quantity: float) -> Dict[str, Any]:
        """Buy a stock with improved error handling and validation"""
        try:
            from database import db_service
            from market_data import MarketDataService
            
            symbol = symbol.upper()
            
            # Validate inputs
            if not symbol:
                return {"error": "Symbol is required"}
            
            if not quantity or quantity <= 0:
                return {"error": "Quantity must be positive"}
            
            # Check if we have a user ID (required for database operations)
            if not self.user_id:
                return {"error": "User ID is required for transactions"}
            
            # Get current price
            market_service = MarketDataService()
            price_data = await market_service.get_stock_price(symbol)
            
            if not price_data or "error" in price_data:
                return {"error": f"Could not retrieve current price for {symbol}. Please try again later."}
            
            current_price = price_data.get("price")
            if not current_price:
                return {"error": f"Could not determine current price for {symbol}"}
            
            # Calculate total cost
            total_cost = current_price * quantity
            
            # Get the user's portfolio from database
            portfolios = await db_service.get_user_portfolios(self.user_id)
            if not portfolios:
                return {"error": "No portfolio found for this user"}
            
            portfolio_id = portfolios[0]["id"]
            portfolio = portfolios[0]
            
            # Check if user has enough cash
            if portfolio["cash_balance"] < total_cost:
                return {
                    "error": "Insufficient funds",
                    "cash_balance": portfolio["cash_balance"],
                    "required": total_cost,
                    "shortfall": total_cost - portfolio["cash_balance"]
                }
            
            # Execute the buy order
            try:
                result = await db_service.execute_buy_order(
                    portfolio_id=portfolio_id,
                    user_id=self.user_id,
                    symbol=symbol,
                    shares=quantity,
                    price_per_share=current_price
                )
                
                # Update the portfolio manager's data
                updated_portfolio = await db_service.get_portfolio_by_id(portfolio_id, self.user_id)
                updated_holdings = await db_service.get_portfolio_holdings(portfolio_id)
                
                self.portfolio = {
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
                    "total_cost": total_cost,
                    "new_cash_balance": result["new_cash_balance"],
                    "transaction_id": result["transaction"]["id"],
                    "message": f"Successfully purchased {quantity} shares of {symbol} at ${current_price:.2f} per share."
                }
            except Exception as db_error:
                return {"error": f"Database error during purchase: {str(db_error)}"}
                
        except Exception as e:
            return {"error": f"Error buying stock: {str(e)}"}
    
    async def sell_stock(self, symbol: str, quantity: float) -> Dict[str, Any]:
        """Sell a stock with improved error handling and validation"""
        try:
            from database import db_service
            from market_data import MarketDataService
            
            symbol = symbol.upper()
            
            # Validate inputs
            if not symbol:
                return {"error": "Symbol is required"}
            
            if not quantity or quantity <= 0:
                return {"error": "Quantity must be positive"}
            
            # Check if we have a user ID (required for database operations)
            if not self.user_id:
                return {"error": "User ID is required for transactions"}
            
            # Get the user's portfolio from database
            portfolios = await db_service.get_user_portfolios(self.user_id)
            if not portfolios:
                return {"error": "No portfolio found for this user"}
            
            portfolio_id = portfolios[0]["id"]
            
            # Check if the user owns the stock and has enough shares
            holdings = await db_service.get_portfolio_holdings(portfolio_id)
            holding = next((h for h in holdings if h["symbol"].upper() == symbol.upper()), None)
            
            if not holding:
                return {"error": f"You don't own any shares of {symbol}"}
            
            if holding["shares"] < quantity:
                return {
                    "error": f"Insufficient shares. You own {holding['shares']} shares of {symbol} but are trying to sell {quantity}.",
                    "owned_shares": holding["shares"],
                    "requested_shares": quantity
                }
            
            # Get current price
            market_service = MarketDataService()
            price_data = await market_service.get_stock_price(symbol)
            
            if not price_data or "error" in price_data:
                return {"error": f"Could not retrieve current price for {symbol}. Please try again later."}
            
            current_price = price_data.get("price")
            if not current_price:
                return {"error": f"Could not determine current price for {symbol}"}
            
            # Calculate total proceeds
            total_proceeds = current_price * quantity
            
            # Execute the sell order
            try:
                result = await db_service.execute_sell_order(
                    portfolio_id=portfolio_id,
                    user_id=self.user_id,
                    symbol=symbol,
                    shares=quantity,
                    price_per_share=current_price
                )
                
                # Update the portfolio manager's data
                updated_portfolio = await db_service.get_portfolio_by_id(portfolio_id, self.user_id)
                updated_holdings = await db_service.get_portfolio_holdings(portfolio_id)
                
                self.portfolio = {
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
            except Exception as db_error:
                return {"error": f"Database error during sale: {str(db_error)}"}
                
        except Exception as e:
            return {"error": f"Error selling stock: {str(e)}"}
    
    def can_afford(self, symbol: str, quantity: int, current_price: float) -> Dict[str, Any]:
        """Check if user can afford to buy the specified quantity"""
        total_cost = quantity * current_price
        can_afford = total_cost <= self.portfolio["cash_balance"]
        
        return {
            "can_afford": can_afford,
            "total_cost": total_cost,
            "available_cash": self.portfolio["cash_balance"],
            "shortfall": max(0, total_cost - self.portfolio["cash_balance"]),
            "max_affordable_shares": int(self.portfolio["cash_balance"] / current_price) if current_price > 0 else 0
        }

    def calculate_portfolio_value(self, market_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculate total portfolio value with current market prices"""
        total_value = 0
        total_cost = 0
        holdings_with_current_value = []
        
        for holding in self.portfolio["holdings"]:
            symbol = holding["symbol"]
            quantity = holding["quantity"]
            purchase_price = holding["purchase_price"]
            current_price = market_prices.get(symbol, purchase_price)
            
            cost_basis = quantity * purchase_price
            current_value = quantity * current_price
            pnl = current_value - cost_basis
            pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            holdings_with_current_value.append({
                **holding,
                "current_price": current_price,
                "current_value": current_value,
                "cost_basis": cost_basis,
                "pnl": pnl,
                "pnl_percent": pnl_percent
            })
        
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        total_account_value = total_value + self.portfolio["cash_balance"]
        
        return {
            "holdings": holdings_with_current_value,
            "portfolio_value": total_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "cash_balance": self.portfolio["cash_balance"],
            "total_account_value": total_account_value,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_portfolio_summary(self, market_prices: Dict[str, float]) -> str:
        """Get a text summary of portfolio performance"""
        portfolio_data = self.calculate_portfolio_value(market_prices)
        
        summary = f"""Portfolio Summary:
        - Total Portfolio Value: ${portfolio_data['portfolio_value']:,.2f}
        - Total P&L: ${portfolio_data['total_pnl']:,.2f} ({portfolio_data['total_pnl_percent']:+.2f}%)
        - Cash Balance: ${portfolio_data['cash_balance']:,.2f}
        - Total Account Value: ${portfolio_data['total_account_value']:,.2f}
        
        Holdings Performance:"""
        
        for holding in portfolio_data['holdings']:
            summary += f"\n        - {holding['symbol']}: {holding['quantity']} shares, ${holding['pnl']:,.2f} ({holding['pnl_percent']:+.2f}%)"
        
        return summary
    
    def get_stock_performance(self, symbol: str, market_prices: Dict[str, float]) -> str:
        """Get performance data for a specific stock"""
        holding = self.get_holding_by_symbol(symbol)
        if not holding:
            return f"No holding found for {symbol.upper()}"
        
        current_price = market_prices.get(symbol.upper(), holding["purchase_price"])
        quantity = holding["quantity"]
        purchase_price = holding["purchase_price"]
        
        cost_basis = quantity * purchase_price
        current_value = quantity * current_price
        pnl = current_value - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        return f"""{symbol.upper()} Performance:
        - Shares Owned: {quantity}
        - Purchase Price: ${purchase_price:.2f}
        - Current Price: ${current_price:.2f}
        - Total Investment: ${cost_basis:,.2f}
        - Current Value: ${current_value:,.2f}
        - P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)""" 