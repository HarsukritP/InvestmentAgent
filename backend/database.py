import os
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo  # Use built-in zoneinfo instead of pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        # Prefer service role key on the server to bypass RLS safely
        self.supabase_key = (
            os.getenv('SUPABASE_SERVICE_KEY') or
            os.getenv('SUPABASE_SERVICE_ROLE_KEY') or
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        key_desc = 'service' if os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'anon'
        print(f"✅ Database service initialized successfully (key: {key_desc})")

    # User Management
    async def create_or_get_user(self, google_id: str, email: str, name: str, picture_url: str = None) -> Dict[str, Any]:
        """Create a new user or get existing user by ID/email.

        During auth provider migrations, the provider subject (google_id) may change while
        email stays the same. This method first tries to find by provider id, then falls back
        to email and updates the provider id to avoid duplicate-key errors on email.
        """
        try:
            # 1) Lookup by provider id (google_id column used to store Auth0 sub as well)
            result = self.supabase.table('users').select('*').eq('google_id', google_id).execute()

            if result.data and len(result.data) > 0:
                # User exists by provider id → update basic info
                user_data = {
                    'email': email,
                    'name': name,
                    'picture_url': picture_url,
                    'updated_at': datetime.utcnow().isoformat()
                }
                updated = self.supabase.table('users').update(user_data).eq('google_id', google_id).execute()
                logger.info(f"Updated existing user by provider id: {email}")
                return updated.data[0]

            # 2) Fallback: lookup by email to handle provider id changes
            email_lookup = self.supabase.table('users').select('*').eq('email', email).execute()
            if email_lookup.data and len(email_lookup.data) > 0:
                existing = email_lookup.data[0]
                # Update record to attach new provider id
                user_data = {
                    'google_id': google_id,
                    'name': name,
                    'picture_url': picture_url,
                    'updated_at': datetime.utcnow().isoformat()
                }
                updated = self.supabase.table('users').update(user_data).eq('id', existing['id']).execute()
                logger.info(f"Updated existing user by email with new provider id: {email}")
                return updated.data[0]

            # 3) Create new user
            user_data = {
                'google_id': google_id,
                'email': email,
                'name': name,
                'picture_url': picture_url
            }
            new_user = self.supabase.table('users').insert(user_data).execute()
            logger.info(f"Created new user: {email}")

            # Create default portfolio for new user
            await self.create_portfolio(new_user.data[0]['id'], "My Portfolio")

            return new_user.data[0]

        except Exception as e:
            logger.error(f"Error creating/getting user: {str(e)}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None

    # Portfolio Management
    async def create_portfolio(self, user_id: str, name: str, cash_balance: float = 10000.0) -> Dict[str, Any]:
        """Create a new portfolio for a user"""
        try:
            portfolio_data = {
                'user_id': user_id,
                'name': name,
                'cash_balance': cash_balance
            }
            
            result = self.supabase.table('portfolios').insert(portfolio_data).execute()
            logger.info(f"Created portfolio '{name}' for user {user_id}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            raise

    async def get_user_portfolios(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all portfolios for a user"""
        try:
            result = self.supabase.table('portfolios').select('*').eq('user_id', user_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user portfolios: {str(e)}")
            return []

    async def get_portfolio_by_id(self, portfolio_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific portfolio by ID (with user verification)"""
        try:
            result = self.supabase.table('portfolios').select('*').eq('id', portfolio_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            return None

    async def update_portfolio_cash(self, portfolio_id: str, new_cash_balance: float) -> bool:
        """Update portfolio cash balance"""
        try:
            self.supabase.table('portfolios').update({
                'cash_balance': new_cash_balance,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', portfolio_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating portfolio cash: {str(e)}")
            return False

    # Holdings Management
    async def get_portfolio_holdings(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Get all holdings for a portfolio"""
        try:
            result = self.supabase.table('holdings').select('*').eq('portfolio_id', portfolio_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting portfolio holdings: {str(e)}")
            return []

    async def add_or_update_holding(self, portfolio_id: str, symbol: str, shares: float, price_per_share: float) -> Dict[str, Any]:
        """Add new holding or update existing one"""
        try:
            # Check if holding exists
            existing = self.supabase.table('holdings').select('*').eq('portfolio_id', portfolio_id).eq('symbol', symbol).execute()
            
            if existing.data:
                # Update existing holding
                current_holding = existing.data[0]
                current_shares = current_holding['shares']
                current_avg_cost = current_holding['average_cost']
                
                # Calculate new average cost
                total_current_value = current_shares * current_avg_cost
                new_investment = shares * price_per_share
                new_total_shares = current_shares + shares
                new_avg_cost = (total_current_value + new_investment) / new_total_shares
                
                updated_holding = self.supabase.table('holdings').update({
                    'shares': new_total_shares,
                    'average_cost': new_avg_cost,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', current_holding['id']).execute()
                
                return updated_holding.data[0]
            else:
                # Create new holding
                holding_data = {
                    'portfolio_id': portfolio_id,
                    'symbol': symbol,
                    'shares': shares,
                    'average_cost': price_per_share
                }
                
                new_holding = self.supabase.table('holdings').insert(holding_data).execute()
                return new_holding.data[0]
                
        except Exception as e:
            logger.error(f"Error adding/updating holding: {str(e)}")
            raise

    async def remove_or_reduce_holding(self, portfolio_id: str, symbol: str, shares_to_sell: float) -> bool:
        """Remove or reduce a holding"""
        try:
            # Get current holding
            result = self.supabase.table('holdings').select('*').eq('portfolio_id', portfolio_id).eq('symbol', symbol).execute()
            
            if not result.data:
                return False
                
            holding = result.data[0]
            current_shares = holding['shares']
            
            if shares_to_sell >= current_shares:
                # Remove entire holding
                self.supabase.table('holdings').delete().eq('id', holding['id']).execute()
            else:
                # Reduce holding
                new_shares = current_shares - shares_to_sell
                self.supabase.table('holdings').update({
                    'shares': new_shares,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', holding['id']).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing/reducing holding: {str(e)}")
            return False

    # Transaction Management
    async def record_transaction(self, portfolio_id: str, user_id: str, transaction_type: str, symbol: str,
                               shares: float, price_per_share: float, cash_balance_after: float, 
                               notes: str = None) -> Dict[str, Any]:
        """Record a transaction"""
        try:
            transaction_data = {
                'portfolio_id': portfolio_id,
                'user_id': user_id,  # Fixed: now properly uses the user_id parameter
                'transaction_type': transaction_type,
                'symbol': symbol,
                'shares': shares,
                'price_per_share': price_per_share,
                'total_amount': shares * price_per_share,
                'cash_balance_after': cash_balance_after,
                'notes': notes
            }
            
            result = self.supabase.table('transactions').insert(transaction_data).execute()
            logger.info(f"Recorded {transaction_type} transaction: {shares} shares of {symbol}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error recording transaction: {str(e)}")
            raise

    async def get_portfolio_transactions(self, portfolio_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history for a portfolio"""
        try:
            result = self.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting portfolio transactions: {str(e)}")
            return []

    async def get_transaction_by_id(self, transaction_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID (with user verification)"""
        try:
            result = self.supabase.table('transactions').select('*').eq('id', transaction_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting transaction: {str(e)}")
            return None
    
    async def update_transaction(self, transaction_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a transaction (with user verification)"""
        try:
            # First check if transaction exists and belongs to user
            existing = await self.get_transaction_by_id(transaction_id, user_id)
            if not existing:
                return None
                
            # Remove fields that shouldn't be updated
            safe_update = {k: v for k, v in update_data.items() if k in ['notes', 'symbol']}
            
            if not safe_update:
                return existing  # Nothing to update
                
            # Update the transaction
            result = self.supabase.table('transactions').update(safe_update).eq('id', transaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating transaction: {str(e)}")
            return None
    
    async def delete_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Delete a transaction (with user verification)"""
        try:
            # First check if transaction exists and belongs to user
            existing = await self.get_transaction_by_id(transaction_id, user_id)
            if not existing:
                return False
                
            # Delete the transaction
            self.supabase.table('transactions').delete().eq('id', transaction_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting transaction: {str(e)}")
            return False
            
    async def get_transaction_stats(self, portfolio_id: str) -> Dict[str, Any]:
        """Get transaction statistics for a portfolio"""
        try:
            # Try to use the RPC function if available
            try:
                result = self.supabase.rpc('get_transaction_stats', {'p_portfolio_id': portfolio_id}).execute()
                if result.data:
                    return result.data
            except Exception as e:
                logger.warning(f"Failed to use get_transaction_stats RPC: {str(e)}")
            
            # Fallback: Calculate stats manually
            transactions = await self.get_portfolio_transactions(portfolio_id, limit=100)
            
            # Count buys and sells
            buys = sum(1 for t in transactions if t.get('transaction_type', '').startswith('BUY'))
            sells = sum(1 for t in transactions if t.get('transaction_type') == 'SELL')
            
            # Calculate total amounts
            total_buy_amount = sum(t.get('total_amount', 0) for t in transactions if t.get('transaction_type', '').startswith('BUY'))
            total_sell_amount = sum(t.get('total_amount', 0) for t in transactions if t.get('transaction_type') == 'SELL')
            
            # Find most traded symbol
            symbol_counts = {}
            for t in transactions:
                symbol = t.get('symbol')
                if symbol:
                    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            
            most_traded_symbol = None
            if symbol_counts:
                most_traded_symbol = max(symbol_counts.items(), key=lambda x: x[1])[0]
            
            # Find largest transaction
            largest_transaction = None
            if transactions:
                largest_transaction = max(transactions, key=lambda t: t.get('total_amount', 0))
            
            return {
                "total_transactions": len(transactions),
                "buys": buys,
                "sells": sells,
                "total_buy_amount": total_buy_amount,
                "total_sell_amount": total_sell_amount,
                "most_traded_symbol": most_traded_symbol,
                "largest_transaction": largest_transaction
            }
        except Exception as e:
            logger.error(f"Error getting transaction stats: {str(e)}")
            return {
                "total_transactions": 0,
                "buys": 0,
                "sells": 0,
                "total_buy_amount": 0,
                "total_sell_amount": 0,
                "most_traded_symbol": None,
                "largest_transaction": None
            }

    # ============================
    # Actions Automation (Rules)
    # ============================
    async def create_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new background action (rule)."""
        try:
            # Ensure enums/strings are upper/lower as expected
            if action_data.get('symbol'):
                action_data['symbol'] = action_data['symbol'].upper()
            result = self.supabase.table('actions').insert(action_data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating action: {str(e)}")
            raise

    async def get_actions(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List actions for a user with optional filters."""
        try:
            query = self.supabase.table('actions').select('*').eq('user_id', user_id)
            if filters:
                if 'status' in filters:
                    query = query.eq('status', filters['status'])
                if 'symbol' in filters and filters['symbol']:
                    query = query.eq('symbol', filters['symbol'].upper())
                if 'action_type' in filters:
                    query = query.eq('action_type', filters['action_type'])
                if 'trigger_type' in filters:
                    query = query.eq('trigger_type', filters['trigger_type'])
            result = query.order('created_at', desc=True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting actions: {str(e)}")
            return []

    async def get_action_by_id(self, action_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single action by ID for a user."""
        try:
            result = self.supabase.table('actions').select('*').eq('id', action_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting action by id: {str(e)}")
            return None

    async def update_action(self, action_id: str, user_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an action for a user."""
        try:
            # Only allow safe fields to be updated
            allowed_fields = {
                'status', 'action_type', 'symbol', 'quantity', 'amount_usd',
                'trigger_type', 'trigger_params', 'valid_from', 'valid_until',
                'max_executions', 'cooldown_seconds', 'notes'
            }
            safe_patch = {k: v for k, v in patch.items() if k in allowed_fields}
            # Normalize symbol casing
            if 'symbol' in safe_patch and safe_patch['symbol']:
                safe_patch['symbol'] = str(safe_patch['symbol']).upper()
            if not safe_patch:
                # Nothing to update
                return await self.get_action_by_id(action_id, user_id)

            result = self.supabase.table('actions').update(safe_patch).eq('id', action_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating action: {str(e)}")
            return None

    async def cancel_action(self, action_id: str, user_id: str) -> bool:
        """Soft-cancel an action by setting status to 'cancelled'."""
        try:
            self.supabase.table('actions').update({'status': 'cancelled'}).eq('id', action_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error cancelling action: {str(e)}")
            return False

    async def delete_action(self, action_id: str, user_id: str) -> bool:
        """Hard delete an action (use cancel in most cases)."""
        try:
            self.supabase.table('actions').delete().eq('id', action_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting action: {str(e)}")
            return False

    async def attempt_lease_action(self, action_id: str, lease_seconds: int = 30) -> bool:
        """Attempt to acquire a short processing lease for an action.
        Returns True if lease acquired, False otherwise.
        """
        try:
            # Only lease if current lease is null or expired
            lease_until = (datetime.utcnow() + timedelta(seconds=lease_seconds)).isoformat()
            # Supabase python client lacks WHERE with inequality on same update ergonomically;
            # we do a two-step optimistic approach: check -> update, acceptable for MVP.
            action = self.supabase.table('actions').select('id, processing_lease_until').eq('id', action_id).execute()
            if not action.data:
                return False
            current_lease = action.data[0].get('processing_lease_until')
            if current_lease:
                try:
                    from datetime import datetime as dt
                    current_dt = dt.fromisoformat(current_lease.replace('Z', '+00:00'))
                    if current_dt > datetime.utcnow():
                        return False
                except Exception:
                    # If parsing fails, proceed to try update
                    pass
            self.supabase.table('actions').update({'processing_lease_until': lease_until}).eq('id', action_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error leasing action {action_id}: {str(e)}")
            return False

    async def record_action_execution(self, action_id: str, execution_status: str, details: Dict[str, Any], transaction_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Record an action execution result."""
        try:
            payload = {
                'action_id': action_id,
                'execution_status': execution_status,
                'details': details,
                'transaction_id': transaction_id
            }
            result = self.supabase.table('action_executions').insert(payload).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error recording action execution: {str(e)}")
            return None

    # Trading Operations
    async def execute_buy_order(self, portfolio_id: str, user_id: str, symbol: str, shares: float, price_per_share: float) -> Dict[str, Any]:
        """Execute a buy order"""
        try:
            # Get portfolio
            portfolio = await self.get_portfolio_by_id(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            total_cost = shares * price_per_share
            
            if portfolio['cash_balance'] < total_cost:
                raise ValueError("Insufficient funds")
            
            # Update cash balance
            new_cash_balance = portfolio['cash_balance'] - total_cost
            await self.update_portfolio_cash(portfolio_id, new_cash_balance)
            
            # Add/update holding
            holding = await self.add_or_update_holding(portfolio_id, symbol, shares, price_per_share)
            
            # Record transaction
            transaction = await self.record_transaction(
                portfolio_id, user_id, 'BUY', symbol, shares, price_per_share, 
                new_cash_balance, f"Bought {shares} shares at ${price_per_share:.2f}"
            )
            
            return {
                'success': True,
                'transaction': transaction,
                'holding': holding,
                'new_cash_balance': new_cash_balance
            }
            
        except Exception as e:
            logger.error(f"Error executing buy order: {str(e)}")
            raise

    async def execute_sell_order(self, portfolio_id: str, user_id: str, symbol: str, shares: float, price_per_share: float) -> Dict[str, Any]:
        """Execute a sell order"""
        try:
            # Get portfolio
            portfolio = await self.get_portfolio_by_id(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            # Check if user has enough shares
            holdings = await self.get_portfolio_holdings(portfolio_id)
            current_holding = next((h for h in holdings if h['symbol'].upper() == symbol.upper()), None)
            
            if not current_holding or current_holding['shares'] < shares:
                raise ValueError("Insufficient shares to sell")
            
            # Calculate proceeds
            total_proceeds = shares * price_per_share
            
            # Update cash balance
            new_cash_balance = portfolio['cash_balance'] + total_proceeds
            await self.update_portfolio_cash(portfolio_id, new_cash_balance)
            
            # Remove/reduce holding
            await self.remove_or_reduce_holding(portfolio_id, symbol, shares)
            
            # Record transaction
            transaction = await self.record_transaction(
                portfolio_id, user_id, 'SELL', symbol, shares, price_per_share, 
                new_cash_balance, f"Sold {shares} shares at ${price_per_share:.2f}"
            )
            
            return {
                'success': True,
                'transaction': transaction,
                'new_cash_balance': new_cash_balance
            }
            
        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
            raise

    # Market Data Storage Methods
    async def store_market_data(self, symbol: str, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store market data in the collaborative cache with enhanced validation"""
        try:
            # Data validation
            price = float(price_data.get('price', 0))
            if price <= 0:
                raise ValueError(f"Invalid price for {symbol}: {price}")
            
            # Check for reasonable price bounds (basic sanity check)
            if price > 100000:  # $100k per share seems unreasonable for most stocks
                print(f"⚠️  HIGH PRICE | {symbol:6} | Unusually high price: ${price:,.2f}")
            
            market_data = {
                'symbol': symbol.upper(),
                'price': price,
                'volume': int(price_data.get('volume', 0)) if price_data.get('volume') else None,
                'open_price': float(price_data.get('open_price')) if price_data.get('open_price') else None,
                'high_price': float(price_data.get('high_price')) if price_data.get('high_price') else None,
                'low_price': float(price_data.get('low_price')) if price_data.get('low_price') else None,
                'close_price': float(price_data.get('close_price')) if price_data.get('close_price') else None,
                'change_amount': float(price_data.get('change', 0)),
                'change_percent': float(price_data.get('change_percent', 0)),
                'source': price_data.get('source', 'twelvedata'),
                'data_type': price_data.get('data_type', 'realtime')
            }
            
            # Store in historical data table
            result = self.supabase.table('market_data_history').insert(market_data).execute()
            
            # Update or insert current price (upsert operation)
            await self._update_current_price(symbol.upper(), market_data)
            
            # Don't log here - let the market_data service handle the logging
            return result.data[0]
            
        except ValueError as e:
            print(f"⚠️  DATA ERROR | {symbol:6} | {str(e)}")
            raise
        except Exception as e:
            # Check for specific database permission errors
            if "row-level security policy" in str(e):
                # This is expected in some configurations - don't log as error
                pass
            else:
                print(f"⚠️  DB ERROR   | {symbol:6} | {str(e)}")
            raise

    async def _update_current_price(self, symbol: str, market_data: Dict[str, Any]):
        """Update current price table with upsert logic"""
        try:
            # Check if current price exists
            existing = self.supabase.table('current_prices').select('*').eq('symbol', symbol).execute()
            
            current_price_data = {
                'symbol': symbol,
                'price': market_data['price'],
                'volume': market_data.get('volume'),
                'change_amount': market_data.get('change_amount'),
                'change_percent': market_data.get('change_percent'),
                'source': market_data.get('source'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # Update existing record
                self.supabase.table('current_prices').update(current_price_data).eq('symbol', symbol).execute()
            else:
                # Insert new record
                self.supabase.table('current_prices').insert(current_price_data).execute()
                
        except Exception as e:
            # Don't log here as this is a secondary operation and errors are handled upstream
            pass

    async def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the most recent price for a symbol from cache with enhanced data"""
        try:
            result = self.supabase.table('current_prices').select('*').eq('symbol', symbol.upper()).execute()
            
            if result.data:
                price_data = result.data[0]
                
                # Calculate data age
                timestamp = datetime.fromisoformat(price_data['timestamp'].replace('Z', '+00:00'))
                age_minutes = (datetime.now(timestamp.tzinfo) - timestamp).total_seconds() / 60
                
                return {
                    'symbol': price_data['symbol'],
                    'price': float(price_data['price']),
                    'volume': price_data.get('volume'),
                    'change': price_data.get('change_amount'),
                    'change_percent': price_data.get('change_percent'),
                    'timestamp': price_data['timestamp'],
                    'source': price_data.get('source', 'twelvedata'),
                    'cached': True,
                    'cache_age_minutes': round(age_minutes, 1),
                    'is_fresh': age_minutes <= 5  # Fresh if less than 5 minutes old
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None

    async def get_cached_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get cached prices for multiple symbols with batch optimization"""
        try:
            if not symbols:
                return {}
            
            # Convert symbols to uppercase for consistency
            upper_symbols = [s.upper() for s in symbols]
            
            # Batch query for better performance
            result = self.supabase.table('current_prices').select('*').in_('symbol', upper_symbols).execute()
            
            cached_prices = {}
            current_time = datetime.now()
            
            for price_data in result.data:
                try:
                    # Calculate data age
                    timestamp = datetime.fromisoformat(price_data['timestamp'].replace('Z', '+00:00'))
                    age_minutes = (current_time.replace(tzinfo=timestamp.tzinfo) - timestamp).total_seconds() / 60
                    
                    cached_prices[price_data['symbol']] = {
                        'symbol': price_data['symbol'],
                        'price': float(price_data['price']),
                        'volume': price_data.get('volume'),
                        'change': price_data.get('change_amount'),
                        'change_percent': price_data.get('change_percent'),
                        'timestamp': price_data['timestamp'],
                        'source': price_data.get('source', 'twelvedata'),
                        'cached': True,
                        'cache_age_minutes': round(age_minutes, 1),
                        'is_fresh': age_minutes <= 5
                    }
                except Exception as e:
                    print(f"⚠️  PARSE ERROR| {price_data.get('symbol', 'unknown'):6} | {str(e)}")
                    continue
            
            # Log cache hit statistics in a clean format
            hit_rate = len(cached_prices) / len(upper_symbols) * 100 if upper_symbols else 0
            print(f"📊 CACHE BATCH| {len(cached_prices)}/{len(upper_symbols)} hits ({hit_rate:.0f}%)")
            
            return cached_prices
            
        except Exception as e:
            print(f"⚠️  CACHE ERROR| Batch query failed: {str(e)}")
            return {}

    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical price data for analysis with improved performance"""
        try:
            # Calculate the date threshold
            from datetime import datetime, timedelta
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Optimized query with limit to prevent excessive data
            result = self.supabase.table('market_data_history').select('*').eq('symbol', symbol.upper()).gte('timestamp', date_threshold).order('timestamp', desc=True).limit(1000).execute()
            
            historical_data = []
            for record in result.data:
                try:
                    historical_data.append({
                        'symbol': record['symbol'],
                        'price': float(record['price']),
                        'volume': record.get('volume'),
                        'open_price': float(record['open_price']) if record.get('open_price') else None,
                        'high_price': float(record['high_price']) if record.get('high_price') else None,
                        'low_price': float(record['low_price']) if record.get('low_price') else None,
                        'close_price': float(record['close_price']) if record.get('close_price') else None,
                        'change_amount': float(record['change_amount']) if record.get('change_amount') else None,
                        'change_percent': float(record['change_percent']) if record.get('change_percent') else None,
                        'timestamp': record['timestamp'],
                        'source': record.get('source', 'twelvedata')
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing historical record for {symbol}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(historical_data)} historical records for {symbol} ({days} days)")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return []

    async def is_price_data_fresh(self, symbol: str, max_age_minutes: int = 5) -> bool:
        """Check if we have fresh price data for a symbol with intelligent freshness"""
        try:
            from datetime import datetime, timedelta, time
            
            # Get current market conditions for intelligent freshness
            current_time = datetime.now()
            
            # Define market hours (Eastern Time)
            eastern_tz = ZoneInfo('US/Eastern')
            now_et = datetime.now(eastern_tz)
            market_open = time(9, 30)  # 9:30 AM ET
            market_close = time(16, 0)  # 4:00 PM ET
            
            # Check if it's a weekday (0=Monday, 6=Sunday)
            is_weekend = now_et.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            # Check if within market hours
            current_et_time = now_et.time()
            is_market_hours = market_open <= current_et_time <= market_close and not is_weekend
            
            # Adjust freshness threshold based on market conditions
            if is_weekend:
                max_age_minutes = 60 * 24  # 24 hours on weekends
            elif not is_market_hours:
                max_age_minutes = 20 * 60  # 20 minutes outside market hours
            else:
                max_age_minutes = 3 * 60  # 3 minutes during market hours
            
            # Override with passed parameter if it's stricter
            if max_age_minutes < 5:
                max_age_minutes = 5  # Minimum threshold
            
            # Calculate the freshness threshold
            threshold = (current_time - timedelta(minutes=max_age_minutes)).isoformat()
            
            result = self.supabase.table('current_prices').select('timestamp').eq('symbol', symbol.upper()).gte('timestamp', threshold).execute()
            
            is_fresh = len(result.data) > 0
            logger.debug(f"Freshness check for {symbol}: {'fresh' if is_fresh else 'stale'} (threshold: {max_age_minutes}min)")
            
            return is_fresh
            
        except Exception as e:
            logger.error(f"Error checking price freshness for {symbol}: {str(e)}")
            return False

    async def get_market_data_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about our market data cache"""
        try:
            # Count total records
            total_result = self.supabase.table('market_data_history').select('id', count='exact').execute()
            total_records = total_result.count
            
            # Count unique symbols
            symbols_result = self.supabase.table('current_prices').select('symbol').execute()
            unique_symbols = len(symbols_result.data)
            
            # Get latest update
            latest_result = self.supabase.table('market_data_history').select('timestamp').order('timestamp', desc=True).limit(1).execute()
            latest_update = latest_result.data[0]['timestamp'] if latest_result.data else None
            
            # Calculate data freshness distribution
            from datetime import datetime, timedelta
            now = datetime.now()
            
            # Count fresh data (< 5 minutes)
            fresh_threshold = (now - timedelta(minutes=5)).isoformat()
            fresh_result = self.supabase.table('current_prices').select('symbol', count='exact').gte('timestamp', fresh_threshold).execute()
            fresh_count = fresh_result.count
            
            # Count recent data (< 1 hour)
            recent_threshold = (now - timedelta(hours=1)).isoformat()
            recent_result = self.supabase.table('current_prices').select('symbol', count='exact').gte('timestamp', recent_threshold).execute()
            recent_count = recent_result.count
            
            # Calculate cache efficiency
            fresh_percentage = (fresh_count / unique_symbols * 100) if unique_symbols > 0 else 0
            recent_percentage = (recent_count / unique_symbols * 100) if unique_symbols > 0 else 0
            
            # Get source distribution
            source_result = self.supabase.table('current_prices').select('source').execute()
            source_counts = {}
            for record in source_result.data:
                source = record.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            return {
                'total_records': total_records,
                'unique_symbols': unique_symbols,
                'latest_update': latest_update,
                'cache_status': 'active',
                'freshness': {
                    'fresh_symbols': fresh_count,
                    'fresh_percentage': round(fresh_percentage, 1),
                    'recent_symbols': recent_count,
                    'recent_percentage': round(recent_percentage, 1)
                },
                'sources': source_counts,
                'performance': {
                    'avg_records_per_symbol': round(total_records / unique_symbols, 1) if unique_symbols > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting market data stats: {str(e)}")
            return {
                'total_records': 0,
                'unique_symbols': 0,
                'latest_update': None,
                'cache_status': 'error',
                'error': str(e)
            }

    async def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """Clean up old market data to maintain performance"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Count records to be deleted
            count_result = self.supabase.table('market_data_history').select('id', count='exact').lt('timestamp', cutoff_date).execute()
            records_to_delete = count_result.count
            
            if records_to_delete > 0:
                # Delete old records
                delete_result = self.supabase.table('market_data_history').delete().lt('timestamp', cutoff_date).execute()
                
                logger.info(f"Cleaned up {records_to_delete} old market data records (older than {days_to_keep} days)")
                
                return {
                    'success': True,
                    'records_deleted': records_to_delete,
                    'cutoff_date': cutoff_date,
                    'days_kept': days_to_keep
                }
            else:
                return {
                    'success': True,
                    'records_deleted': 0,
                    'message': 'No old records to clean up'
                }
                
        except Exception as e:
            logger.error(f"Error during data cleanup: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_cached_market_context(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached market context data by key"""
        try:
            result = self.supabase.table('market_context_cache').select('*').eq('key', key).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting cached market context: {str(e)}")
            return None

    async def store_market_context(self, key: str, data: Dict[str, Any]) -> bool:
        """Store market context data in cache"""
        try:
            # Check if entry exists
            result = self.supabase.table('market_context_cache').select('id').eq('key', key).execute()
            
            cache_data = {
                'key': key,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if result.data:
                # Update existing entry
                self.supabase.table('market_context_cache').update(cache_data).eq('key', key).execute()
            else:
                # Insert new entry
                self.supabase.table('market_context_cache').insert(cache_data).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error storing market context: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test database connection"""
        if not self.supabase:
            raise Exception("Database not configured")
            
        # Simple test query
        try:
            result = self.supabase.table('users').select('count').limit(1).execute()
            return True
        except Exception as e:
            raise Exception(f"Database connection test failed: {str(e)}")

# Global database service instance
db_service = DatabaseService() 