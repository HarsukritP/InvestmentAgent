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
    
    def buy_stock(self, symbol: str, quantity: int, current_price: float) -> Dict[str, Any]:
        """Buy stock - add to portfolio or increase existing position"""
        try:
            symbol = symbol.upper()
            total_cost = quantity * current_price
            
            # Check if we have enough cash
            if total_cost > self.portfolio["cash_balance"]:
                return {
                    "success": False,
                    "error": f"Insufficient funds. Need ${total_cost:,.2f}, have ${self.portfolio['cash_balance']:,.2f}",
                    "required": total_cost,
                    "available": self.portfolio["cash_balance"]
                }
            
            # Check if we already own this stock
            existing_holding = self.get_holding_by_symbol(symbol)
            
            if existing_holding:
                # Calculate new average price
                old_quantity = existing_holding["quantity"]
                old_total_cost = old_quantity * existing_holding["purchase_price"]
                new_total_cost = old_total_cost + total_cost
                new_quantity = old_quantity + quantity
                new_avg_price = new_total_cost / new_quantity
                
                # Update existing holding
                existing_holding["quantity"] = new_quantity
                existing_holding["purchase_price"] = new_avg_price
                
                transaction_type = "BUY_ADD"
            else:
                # Add new holding
                new_holding = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "purchase_price": current_price
                }
                self.portfolio["holdings"].append(new_holding)
                transaction_type = "BUY_NEW"
            
            # Deduct cash
            self.portfolio["cash_balance"] -= total_cost
            
            # Record transaction
            transaction = {
                "id": len(self.portfolio.get("transactions", [])) + 1,
                "type": transaction_type,
                "symbol": symbol,
                "quantity": quantity,
                "price": current_price,
                "total_amount": total_cost,
                "timestamp": datetime.now().isoformat(),
                "cash_balance_after": self.portfolio["cash_balance"]
            }
            
            if "transactions" not in self.portfolio:
                self.portfolio["transactions"] = []
            self.portfolio["transactions"].append(transaction)
            
            # Update portfolio timestamp
            self.portfolio["updated_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "transaction": transaction,
                "message": f"Successfully bought {quantity} shares of {symbol} at ${current_price:.2f} each",
                "total_cost": total_cost,
                "remaining_cash": self.portfolio["cash_balance"],
                "holding": self.get_holding_by_symbol(symbol)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error buying stock: {str(e)}"
            }
    
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