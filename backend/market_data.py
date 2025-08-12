"""
Market data integration with Twelve Data API and collaborative database caching
"""
import requests
import os
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta, time
import json
import logging
import random
import aiohttp
import asyncio
from zoneinfo import ZoneInfo  # Use built-in zoneinfo instead of pytz

# Configure cleaner logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Market hours configuration (Eastern Time)
MARKET_OPEN_TIME = time(9, 30)  # 9:30 AM ET
MARKET_CLOSE_TIME = time(16, 0)  # 4:00 PM ET
MARKET_TIMEZONE = ZoneInfo('America/New_York')  # Use ZoneInfo instead of pytz.timezone
REFRESH_INTERVAL_MARKET_OPEN = 3 * 60  # 3 minutes in seconds
REFRESH_INTERVAL_MARKET_CLOSED = 20 * 60  # 20 minutes in seconds

class MarketDataService:
    def __init__(self, db_service=None):
        # Twelve Data API configuration
        self.twelvedata_api_key = os.getenv("TWELVEDATA_API_KEY")
        self.twelvedata_base_url = "https://api.twelvedata.com"
        
        # Import database service
        if db_service is None:
            from database import db_service as default_db_service
            self.db_service = default_db_service
        else:
            self.db_service = db_service
        
        # Background task state
        self._auto_refresh_task = None
        self._watchlist_symbols = set()
        self._is_refreshing = False
        self._last_refresh = datetime.now() - timedelta(hours=1)  # Initialize to trigger immediate refresh
        
        if not self.twelvedata_api_key:
            print("⚠️  Warning: TWELVEDATA_API_KEY not found in environment variables")
        else:
            print(f"✅ Twelve Data API configured (key: {self.twelvedata_api_key[:8]}...)")
            
        # Start the auto-refresh background task
        self.start_auto_refresh()
    
    def is_market_open(self) -> bool:
        """Check if the US stock market is currently open"""
        # Get current time in Eastern Time
        now_et = datetime.now(MARKET_TIMEZONE)
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now_et.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if within market hours
        current_time = now_et.time()
        return MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME
    
    def get_refresh_interval(self) -> int:
        """Get the appropriate refresh interval based on market hours"""
        return REFRESH_INTERVAL_MARKET_OPEN if self.is_market_open() else REFRESH_INTERVAL_MARKET_CLOSED
    
    def start_auto_refresh(self):
        """Start the background task for auto-refreshing stock prices"""
        if self._auto_refresh_task is None:
            self._auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())
            print("✅ Auto-refresh background task started")
    
    def stop_auto_refresh(self):
        """Stop the background task for auto-refreshing stock prices"""
        if self._auto_refresh_task:
            self._auto_refresh_task.cancel()
            self._auto_refresh_task = None
            print("⏹️ Auto-refresh background task stopped")
    
    def add_to_watchlist(self, symbols: List[str]):
        """Add symbols to the auto-refresh watchlist"""
        for symbol in symbols:
            self._watchlist_symbols.add(symbol.upper())
        print(f"👀 Watchlist updated: {len(self._watchlist_symbols)} symbols")
    
    async def _auto_refresh_loop(self):
        """Background task loop for auto-refreshing stock prices"""
        try:
            while True:
                # Determine the appropriate refresh interval
                interval = self.get_refresh_interval()
                
                # Check if it's time to refresh
                time_since_last_refresh = (datetime.now() - self._last_refresh).total_seconds()
                
                if time_since_last_refresh >= interval and self._watchlist_symbols and not self._is_refreshing:
                    self._is_refreshing = True
                    try:
                        # Log the refresh with market status
                        market_status = "OPEN" if self.is_market_open() else "CLOSED"
                        print(f"\n🔄 AUTO-REFRESH | Market {market_status} | Refreshing {len(self._watchlist_symbols)} symbols")
                        
                        # Refresh prices for watchlist symbols
                        await self.get_multiple_quotes_optimized(list(self._watchlist_symbols))
                        
                        # Update last refresh time
                        self._last_refresh = datetime.now()
                        
                        # Log completion
                        print(f"✅ AUTO-REFRESH | Complete | Next refresh in {interval//60} minutes")
                    except Exception as e:
                        print(f"❌ AUTO-REFRESH | Failed | Error: {str(e)}")
                    finally:
                        self._is_refreshing = False
                
                # Sleep for a short time before checking again
                await asyncio.sleep(10)  # Check every 10 seconds
        except asyncio.CancelledError:
            print("🛑 Auto-refresh task cancelled")
        except Exception as e:
            print(f"❌ Auto-refresh task error: {str(e)}")
            # Restart the task if it fails
            self._auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())
    
    async def _get_cached_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price from database cache if fresh enough with intelligent freshness"""
        try:
            # Check if we have fresh data with intelligent freshness logic
            is_fresh = await self.db_service.is_price_data_fresh(symbol, max_age_minutes=5)
            
            if is_fresh:
                cached_data = await self.db_service.get_current_price(symbol)
                if cached_data:
                    age_min = cached_data.get('cache_age_minutes', 0)
                    print(f"🎯 CACHE HIT  | {symbol:6} | ${cached_data['price']:8.2f} | Age: {age_min:.1f}min")
                    return cached_data
            
            print(f"❌ CACHE MISS | {symbol:6} | Data too old or not found")
            return None
            
        except Exception as e:
            print(f"⚠️  CACHE ERROR| {symbol:6} | {str(e)}")
            return None
    
    async def _store_price_data(self, symbol: str, price_data: Dict[str, Any]):
        """Store price data in collaborative database cache with validation"""
        try:
            # Validate data before storing
            if not price_data.get('price') or price_data['price'] <= 0:
                print(f"⚠️  INVALID DATA| {symbol:6} | Price: {price_data.get('price', 'N/A')}")
                return
            
            await self.db_service.store_market_data(symbol, price_data)
            # Also upsert the current price immediately to avoid stale values
            try:
                await self.db_service._update_current_price(symbol.upper(), price_data)
            except Exception:
                pass
            print(f"💾 CACHE STORE| {symbol:6} | ${price_data['price']:8.2f} | Stored successfully")
        except Exception as e:
            if "row-level security policy" in str(e):
                print(f"🔒 CACHE SKIP | {symbol:6} | Database permissions issue")
            else:
                print(f"⚠️  CACHE ERROR| {symbol:6} | {str(e)}")
    
    async def _fetch_from_twelvedata(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock quote from Twelve Data API"""
        try:
            if not self.twelvedata_api_key:
                raise Exception("Twelve Data API key not configured")
            
            # Use the quote endpoint for real-time data
            url = f"{self.twelvedata_base_url}/quote"
            params = {
                "symbol": symbol,
                "apikey": self.twelvedata_api_key
            }
            
            print(f"🌐 API CALL   | {symbol:6} | Fetching from Twelve Data...")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "status" in data and data["status"] == "error":
                error_msg = data.get("message", "Unknown error")
                print(f"❌ API ERROR  | {symbol:6} | {error_msg}")
                raise Exception(f"API Error: {error_msg}")
            
            # Check if we have the required fields
            if "symbol" not in data or "close" not in data:
                print(f"❌ API ERROR  | {symbol:6} | Invalid response format")
                raise Exception("Invalid API response format")
            
            # Parse the response. Prefer real-time price when available
            # TwelveData's quote response includes `price` for the current price; `close` may be prior close
            price_raw = data.get("price", data.get("close", 0))
            price = float(price_raw or 0)
            previous_close = float(data.get("previous_close", price))
            change = price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0

            # Fallback: Some symbols occasionally return stale/incorrect `close`.
            # If the delta is implausible (>35%), hit the lightweight price endpoint.
            try:
                if previous_close and previous_close > 0 and abs(price - previous_close) / previous_close > 0.35:
                    price_url = f"{self.twelvedata_base_url}/price"
                    r = requests.get(price_url, params={"symbol": symbol, "apikey": self.twelvedata_api_key}, timeout=8)
                    if r.status_code == 200:
                        pr = r.json().get("price")
                        if pr:
                            price = float(pr)
                            change = price - previous_close
                            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            except Exception:
                # Ignore fallback errors; keep original values
                pass
            
            result = {
                "symbol": symbol.upper(),
                "price": price,
                "change": change,
                "change_percent": change_percent,
                "volume": data.get("volume"),
                "open_price": data.get("open"),
                "high_price": data.get("high"),
                "low_price": data.get("low"),
                "close_price": data.get("previous_close"),
                "cached": False,
                "timestamp": datetime.now().isoformat(),
                "source": "twelvedata",
                "api_key_used": "twelvedata"
            }
            
            change_str = f"{change:+.2f} ({change_percent:+.2f}%)"
            print(f"✅ API SUCCESS| {symbol:6} | ${price:8.2f} | {change_str}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ NETWORK ERR| {symbol:6} | {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            print(f"❌ API ERROR  | {symbol:6} | {str(e)}")
            raise Exception(f"API fetch error: {str(e)}")
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current stock quote with collaborative caching"""
        try:
            print(f"\n📊 QUOTE REQ  | {symbol:6} | Starting price lookup...")
            
            # Check cache first
            cached_data = await self._get_cached_price(symbol)
            if cached_data:
                return cached_data
            
            # Try Twelve Data API
            if self.twelvedata_api_key:
                try:
                    quote_data = await self._fetch_from_twelvedata(symbol)
                    if quote_data and quote_data.get('price'):
                        # Store in collaborative cache
                        await self._store_price_data(symbol, quote_data)
                        return quote_data
                except Exception as e:
                    print(f"❌ FETCH FAIL | {symbol:6} | {str(e)}")
                    raise Exception(f"Failed to fetch data for {symbol}: {str(e)}")
            else:
                raise Exception("Twelve Data API key not configured")
            
        except Exception as e:
            print(f"❌ QUOTE FAIL | {symbol:6} | {str(e)}")
            raise Exception(f"Unable to fetch quote for {symbol}: {str(e)}")
    
    async def get_multiple_quotes(self, symbols: list) -> Dict[str, float]:
        """Get quotes for multiple symbols using collaborative cache"""
        print(f"\n📊 BATCH REQ  | Fetching {len(symbols)} symbols: {', '.join(symbols)}")
        quotes = {}
        
        # First, try to get as many as possible from cache
        cached_prices = await self.db_service.get_cached_prices(symbols)
        
        cache_hits = 0
        api_calls = 0
        
        for symbol in symbols:
            symbol_upper = symbol.upper()
            if symbol_upper in cached_prices:
                quotes[symbol_upper] = cached_prices[symbol_upper]["price"]
                cache_hits += 1
            else:
                # Need to fetch from API
                try:
                    quote_data = await self.get_stock_quote(symbol)
                    quotes[symbol_upper] = quote_data["price"]
                    api_calls += 1
                except Exception as e:
                    print(f"❌ SKIP       | {symbol:6} | Failed: {str(e)}")
                    continue
        
        print(f"📈 BATCH DONE | Cache: {cache_hits}/{len(symbols)} | API: {api_calls}/{len(symbols)}")
        return quotes
    
    async def get_portfolio_quotes(self, portfolio_symbols: list) -> Dict[str, any]:
        """Get quotes for all symbols in portfolio with metadata"""
        print(f"\n💼 PORTFOLIO  | Fetching quotes for {len(portfolio_symbols)} holdings")
        quotes = {}
        
        success_count = 0
        for symbol in portfolio_symbols:
            try:
                quotes[symbol.upper()] = await self.get_stock_quote(symbol)
                success_count += 1
            except Exception as e:
                print(f"❌ SKIP       | {symbol:6} | Failed: {str(e)}")
                continue
        
        print(f"💼 PORTFOLIO  | Success: {success_count}/{len(portfolio_symbols)} quotes fetched")
        return quotes
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical price data from our collaborative cache"""
        try:
            return await self.db_service.get_historical_data(symbol, days)
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return []
    
    async def backfill_historical_data(self, symbol: str, period: str = "1year", interval: str = "1day") -> Dict[str, Any]:
        """Backfill historical data from Twelve Data API into our database"""
        try:
            if not self.twelvedata_api_key:
                return {"error": "Twelve Data API key not configured"}
            
            # Convert period to outputsize for Twelve Data API
            outputsize_map = {
                "1week": 7,
                "1month": 30,
                "3months": 90,
                "6months": 180,
                "1year": 365,
                "2years": 730,
                "5years": 1825
            }
            
            outputsize = outputsize_map.get(period, 365)
            
            # Fetch from Twelve Data API
            url = f"{self.twelvedata_base_url}/time_series"
            params = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": min(outputsize, 5000),  # API limit
                "apikey": self.twelvedata_api_key,
                "order": "ASC"  # Oldest first for chronological insertion
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {"error": f"API request failed: {response.status}"}
                    
                    data = await response.json()
                    
                    if data.get("status") == "error":
                        return {"error": data.get("message", "API returned error")}
                    
                    values = data.get("values", [])
                    if not values:
                        return {"error": "No historical data received"}
                    
                    # Process and store historical data
                    stored_count = 0
                    for record in values:
                        try:
                            price_data = {
                                "price": float(record["close"]),
                                "volume": int(record.get("volume", 0)) if record.get("volume") else None,
                                "open_price": float(record["open"]),
                                "high_price": float(record["high"]),
                                "low_price": float(record["low"]),
                                "close_price": float(record["close"]),
                                "source": "twelvedata",
                                "data_type": "historical",
                                "timestamp": record["datetime"]
                            }
                            
                            # Check if this timestamp already exists to avoid duplicates
                            existing = await self._check_existing_data(symbol, record["datetime"])
                            if not existing:
                                await self.db_service.store_market_data(symbol, price_data)
                                stored_count += 1
                        
                        except (ValueError, KeyError) as e:
                            logger.warning(f"Error processing record for {symbol}: {str(e)}")
                            continue
                    
                    logger.info(f"📈 BACKFILL   | {symbol:6} | Stored {stored_count}/{len(values)} records ({period})")
                    
                    return {
                        "symbol": symbol,
                        "period": period,
                        "interval": interval,
                        "total_records": len(values),
                        "stored_records": stored_count,
                        "skipped_records": len(values) - stored_count
                    }
                    
        except Exception as e:
            logger.error(f"Error backfilling historical data for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    async def _check_existing_data(self, symbol: str, timestamp: str) -> bool:
        """Check if historical data already exists for this symbol and timestamp"""
        try:
            result = self.db_service.supabase.table('market_data_history').select('id').eq('symbol', symbol.upper()).eq('timestamp', timestamp).limit(1).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    async def ensure_historical_data(self, symbol: str, period: str = "6months") -> Dict[str, Any]:
        """Ensure we have enough historical data, backfill if needed"""
        try:
            # Check how much data we currently have
            # Include long horizons so we don't mistakenly treat partial data as "sufficient"
            period_days = {
                "1week": 7,
                "1month": 30,
                "3months": 90,
                "6months": 180,
                "1year": 365,
                "2years": 730,
                "5years": 1825,
            }
            days = period_days.get(period, 180)
            
            existing_data = await self.get_historical_data(symbol, days)
            
            # If we have less than 80% of expected data points, backfill
            expected_points = days if period not in ("1week",) else 5  # Account for weekends
            if len(existing_data) < (expected_points * 0.8):
                logger.info(f"📊 DATA GAP   | {symbol:6} | Only {len(existing_data)}/{expected_points} records, backfilling...")
                backfill_result = await self.backfill_historical_data(symbol, period)
                return {
                    "action": "backfilled",
                    "existing_records": len(existing_data),
                    "backfill_result": backfill_result
                }
            else:
                return {
                    "action": "sufficient",
                    "existing_records": len(existing_data),
                    "message": f"Sufficient data available ({len(existing_data)} records)"
                }
                
        except Exception as e:
            logger.error(f"Error ensuring historical data for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    async def get_intraday_data(self, symbol: str, interval: str = "1h", outputsize: int = 24) -> Dict[str, Any]:
        """Get intraday data for hover charts (hours/minutes) with intelligent caching"""
        try:
            if not self.twelvedata_api_key:
                return {"error": "Twelve Data API key not configured"}
            
            # Check cache first
            cache_key = f"intraday_{symbol.upper()}_{interval}"
            cached_data = await self._get_cached_intraday_data(cache_key)
            
            if cached_data:
                logger.info(f"📊 CACHE HIT  | {symbol:6} | Using cached {interval} intraday data")
                return cached_data
            
            # Cache miss - fetch from API
            logger.info(f"📊 CACHE MISS | {symbol:6} | Fetching fresh {interval} intraday data")
            
            # Fetch intraday data from Twelve Data API
            url = f"{self.twelvedata_base_url}/time_series"
            params = {
                "symbol": symbol,
                "interval": interval,  # 1h, 30min, 15min, 5min, 1min
                "outputsize": min(outputsize, 100),  # Limit for responsiveness
                "apikey": self.twelvedata_api_key,
                "order": "ASC"  # Oldest first for chronological charts
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.warning(f"Twelve Data API request failed for {symbol}: Status {response.status}, Response: {response_text[:200]}")
                        return {"error": f"API request failed for {symbol}: {response.status}"}
                    
                    data = await response.json()
                    
                    if data.get("status") == "error":
                        error_msg = data.get("message", "API returned error")
                        logger.warning(f"Twelve Data API error for {symbol}: {error_msg}")
                        return {"error": f"Market data unavailable for {symbol}: {error_msg}"}
                    
                    values = data.get("values", [])
                    if not values:
                        logger.warning(f"No intraday data received for {symbol}")
                        return {"error": f"No intraday data available for {symbol}"}
                    
                    # Format data for charts
                    chart_data = []
                    for record in values:
                        try:
                            chart_data.append({
                                "datetime": record["datetime"],
                                "time": record["datetime"].split(' ')[1] if ' ' in record["datetime"] else record["datetime"][-8:],  # Extract time part
                                "open": float(record["open"]),
                                "high": float(record["high"]),
                                "low": float(record["low"]),
                                "close": float(record["close"]),
                                "volume": int(record.get("volume", 0)) if record.get("volume") else None,
                                "price": float(record["close"])  # For simple line charts
                            })
                        except (ValueError, KeyError) as e:
                            logger.warning(f"Error processing intraday record for {symbol}: {str(e)}")
                            continue
                    
                    result = {
                        "symbol": symbol,
                        "interval": interval,
                        "data_points": len(chart_data),
                        "data": chart_data,
                        "current_price": chart_data[-1]["close"] if chart_data else None,  # Most recent price
                        "change": chart_data[-1]["close"] - chart_data[0]["close"] if len(chart_data) > 1 else 0  # Change from first to last
                    }
                    
                    # Cache the result for future requests
                    await self._cache_intraday_data(cache_key, result)
                    
                    logger.info(f"📈 INTRADAY  | {symbol:6} | Fetched & cached {len(chart_data)} {interval} data points")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error getting intraday data for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    async def _get_cached_intraday_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached intraday data if it's still fresh"""
        try:
            from datetime import datetime, timedelta
            
            # Check if cache entry exists
            cached = await self.db_service.get_cached_market_context(cache_key)
            if not cached:
                return None
            
            # Check if cache is still fresh (30 minutes for intraday data)
            cache_time = datetime.fromisoformat(cached['timestamp'].replace('Z', '+00:00'))
            now = datetime.now(cache_time.tzinfo)
            cache_age_minutes = (now - cache_time).total_seconds() / 60
            
            # Cache expiry based on interval
            max_age_minutes = 30  # Default 30 minutes
            if 'interval' in cached.get('data', {}):
                interval = cached['data']['interval']
                if interval in ['1min', '5min']:
                    max_age_minutes = 5  # 5 minutes for very short intervals
                elif interval in ['15min', '30min']:
                    max_age_minutes = 15  # 15 minutes for short intervals
                elif interval in ['1h', '2h']:
                    max_age_minutes = 30  # 30 minutes for hourly data
                else:
                    max_age_minutes = 60  # 1 hour for longer intervals
            
            if cache_age_minutes <= max_age_minutes:
                return cached['data']
            else:
                logger.info(f"📊 CACHE STALE| {cache_key} | Age: {cache_age_minutes:.1f}min > {max_age_minutes}min")
                return None
                
        except Exception as e:
            logger.warning(f"Error reading intraday cache for {cache_key}: {str(e)}")
            return None
    
    async def _cache_intraday_data(self, cache_key: str, data: Dict[str, Any]) -> bool:
        """Cache intraday data for future requests"""
        try:
            success = await self.db_service.store_market_context(cache_key, data)
            if success:
                logger.info(f"📊 CACHED     | {cache_key} | Stored {data.get('data_points', 0)} data points")
            return success
        except Exception as e:
            logger.warning(f"Error caching intraday data for {cache_key}: {str(e)}")
            return False
    
    async def cleanup_old_intraday_cache(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up old intraday cache entries to prevent database bloat"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cutoff_iso = cutoff_time.isoformat()
            
            # Find old intraday cache entries
            result = self.db_service.supabase.table('market_context_cache').select('key').like('key', 'intraday_%').lt('timestamp', cutoff_iso).execute()
            
            old_entries = [entry['key'] for entry in result.data]
            
            if old_entries:
                # Delete old entries
                delete_result = self.db_service.supabase.table('market_context_cache').delete().in_('key', old_entries).execute()
                logger.info(f"🧹 CACHE CLEAN| Removed {len(old_entries)} old intraday cache entries")
                
                return {
                    "cleaned": True,
                    "removed_entries": len(old_entries),
                    "cutoff_hours": max_age_hours
                }
            else:
                return {
                    "cleaned": True,
                    "removed_entries": 0,
                    "cutoff_hours": max_age_hours
                }
                
        except Exception as e:
            logger.error(f"Error cleaning intraday cache: {str(e)}")
            return {"error": str(e)}
    
    async def get_intraday_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about intraday cache usage"""
        try:
            # Count total intraday cache entries
            result = self.db_service.supabase.table('market_context_cache').select('key, timestamp').like('key', 'intraday_%').execute()
            
            total_entries = len(result.data)
            if total_entries == 0:
                return {"total_entries": 0, "fresh_entries": 0, "stale_entries": 0}
            
            # Analyze freshness
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            fresh_count = 0
            stale_count = 0
            symbols = set()
            
            for entry in result.data:
                cache_time = datetime.fromisoformat(entry['timestamp'].replace('Z', ''))
                age_minutes = (now - cache_time).total_seconds() / 60
                
                if age_minutes <= 60:  # Consider 1 hour as fresh
                    fresh_count += 1
                else:
                    stale_count += 1
                
                # Extract symbol from key (format: intraday_SYMBOL_interval)
                key_parts = entry['key'].split('_')
                if len(key_parts) >= 2:
                    symbols.add(key_parts[1])
            
            return {
                "total_entries": total_entries,
                "fresh_entries": fresh_count,
                "stale_entries": stale_count,
                "unique_symbols": len(symbols),
                "symbols_cached": list(symbols)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about our collaborative cache"""
        try:
            return await self.db_service.get_market_data_stats()
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, any]:
        """Health check for market data service"""
        try:
            # Get market status
            is_market_open = self.is_market_open()
            market_status = "open" if is_market_open else "closed"
            refresh_interval = self.get_refresh_interval()
            
            # Calculate time to next refresh
            time_since_last_refresh = (datetime.now() - self._last_refresh).total_seconds()
            time_to_next_refresh = max(0, refresh_interval - time_since_last_refresh)
            
            return {
                "status": "healthy",
                "twelvedata_key_configured": bool(self.twelvedata_api_key),
                "database_connected": True,
                "last_test": datetime.now().isoformat(),
                "cache_type": "collaborative_database",
                "api_source": "Twelve Data (800 requests/day)",
                "auto_refresh": {
                    "enabled": self._auto_refresh_task is not None,
                    "market_status": market_status,
                    "refresh_interval_minutes": refresh_interval // 60,
                    "watchlist_size": len(self._watchlist_symbols),
                    "last_refresh": self._last_refresh.isoformat(),
                    "next_refresh_in_seconds": round(time_to_next_refresh),
                    "is_refreshing": self._is_refreshing
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "twelvedata_key_configured": bool(self.twelvedata_api_key),
                "error": str(e)
            }
    
    async def _search_twelvedata(self, query: str) -> List[Dict[str, Any]]:
        """Search stocks using Twelve Data API with intelligent filtering"""
        try:
            # Common company name to ticker mappings for better search
            company_mappings = {
                'nvidia': 'NVDA',
                'apple': 'AAPL', 
                'microsoft': 'MSFT',
                'google': 'GOOGL',
                'alphabet': 'GOOGL',
                'amazon': 'AMZN',
                'meta': 'META',
                'facebook': 'META',
                'tesla': 'TSLA',
                'netflix': 'NFLX',
                'disney': 'DIS',
                'boeing': 'BA',
                'intel': 'INTC',
                'amd': 'AMD',
                'cisco': 'CSCO',
                'oracle': 'ORCL',
                'salesforce': 'CRM',
                'adobe': 'ADBE',
                'paypal': 'PYPL',
                'visa': 'V',
                'mastercard': 'MA',
                'jpmorgan': 'JPM',
                'bank of america': 'BAC',
                'wells fargo': 'WFC',
                'berkshire': 'BRK.A',
                'johnson': 'JNJ',
                'procter': 'PG',
                'cocacola': 'KO',
                'coca cola': 'KO',
                'pepsi': 'PEP',
                'walmart': 'WMT',
                'target': 'TGT',
                'home depot': 'HD',
                'lowes': 'LOW'
            }
            
            # Check if query matches a known company name
            query_lower = query.lower().strip()
            preferred_symbol = None
            for company, symbol in company_mappings.items():
                if company in query_lower or query_lower in company:
                    preferred_symbol = symbol
                    break
            
            url = f"{self.twelvedata_base_url}/symbol_search"
            params = {
                "symbol": query,
                "apikey": self.twelvedata_api_key
            }
            
            logger.info(f"Searching stocks with Twelve Data for query: {query} (preferred: {preferred_symbol})")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            logger.info(f"Twelve Data search response: {data}")
            
            # Check for API errors
            if "status" in data and data["status"] == "error":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"Twelve Data Search API Error: {error_msg}")
                raise Exception(f"API Error: {error_msg}")
            
            # Parse search results with intelligent filtering and sorting
            results = []
            search_data = data.get("data", [])
            
            # Define preferred exchanges and unwanted instrument types
            us_exchanges = {'NYSE', 'NASDAQ', 'AMEX', 'NYSEARCA'}
            major_international = {'LSE', 'TSX', 'ASX', 'HKEX', 'EURONEXT'}
            unwanted_types = {'warrant', 'certificate', 'option', 'future', 'bond', 'etf', 'fund'}
            
            for item in search_data:
                try:
                    symbol = item.get('symbol', '')
                    name = item.get('instrument_name', '')
                    instrument_type = item.get('instrument_type', 'Equity').lower()
                    region = item.get('country', 'United States')
                    currency = item.get('currency', 'USD')
                    exchange = item.get('exchange', '')
                    
                    # Skip unwanted instrument types
                    if any(unwanted in instrument_type for unwanted in unwanted_types):
                        continue
                    
                    # Skip symbols that look like derivatives (contain numbers, F123456, etc)
                    if len(symbol) > 6 or any(char.isdigit() for char in symbol):
                        # Allow some exceptions for legitimate tickers with numbers
                        if not (symbol.upper() in ['3M', 'MMM'] or symbol.endswith('.TO') or symbol.endswith('.L')):
                            continue
                    
                    # Calculate relevance score
                    score = 0
                    
                    # Preferred symbol gets massive boost (for company name searches like "NVIDIA" -> NVDA)
                    if preferred_symbol and symbol.upper() == preferred_symbol.upper():
                        score += 200
                    
                    # Exact symbol match gets highest priority
                    if symbol.upper() == query.upper():
                        score += 100
                    elif symbol.upper().startswith(query.upper()):
                        score += 80
                    elif query.upper() in symbol.upper():
                        score += 60
                    
                    # Company name matching
                    if query.lower() in name.lower():
                        score += 50
                    
                    # Prefer US exchanges
                    if exchange in us_exchanges:
                        score += 30
                    elif exchange in major_international:
                        score += 20
                    elif region == 'United States':
                        score += 25
                    
                    # Prefer USD currency
                    if currency == 'USD':
                        score += 15
                    
                    # Prefer equity instruments
                    if instrument_type in ['equity', 'common stock', 'stock']:
                        score += 10
                    
                    # Penalty for very long names (often derivatives)
                    if len(name) > 50:
                        score -= 20
                    
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'type': instrument_type.title(),
                        'region': region,
                        'currency': currency,
                        'exchange': exchange,
                        'match_score': score
                    })
                    
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing Twelve Data search result: {e}")
                    continue
            
            # Sort by relevance score (highest first) and take top 8
            results.sort(key=lambda x: x['match_score'], reverse=True)
            results = results[:8]
            
            logger.info(f"✅ Found {len(results)} search results from Twelve Data for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Twelve Data search error: {e}")
            raise Exception(f"Search error: {str(e)}")

    async def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks using Twelve Data"""
        try:
            if not query or len(query.strip()) < 1:
                return []
            
            # Clean the query
            query = query.strip()
            
            # Use Twelve Data search
            if self.twelvedata_api_key:
                try:
                    logger.info(f"Searching stocks with Twelve Data for: {query}")
                    results = await self._search_twelvedata(query)
                    if results:
                        logger.info(f"✅ Successfully got {len(results)} search results from Twelve Data")
                        return results
                    else:
                        logger.warning(f"No search results found for: {query}")
                        return []
                except Exception as e:
                    logger.error(f"❌ Twelve Data search failed: {str(e)}")
                    raise Exception(f"Search failed for '{query}': {str(e)}")
            else:
                raise Exception("Twelve Data API key not configured")
            
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            raise Exception(f"Stock search failed: {str(e)}")

    async def get_multiple_quotes_optimized(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """Get quotes for multiple symbols with optimized caching and batch API calls"""
        if not symbols:
            return {}
        
        quotes = {}
        symbols_to_fetch = []
        
        # First, get as many as possible from cache in one batch query
        logger.info(f"Checking cache for {len(symbols)} symbols...")
        cached_prices = await self.db_service.get_cached_prices(symbols)
        
        # Separate fresh vs stale data
        fresh_symbols = []
        stale_symbols = []
        
        for symbol in symbols:
            symbol_upper = symbol.upper()
            cached_data = cached_prices.get(symbol_upper)
            
            if cached_data and cached_data.get('is_fresh', False):
                quotes[symbol_upper] = cached_data
                fresh_symbols.append(symbol_upper)
            else:
                stale_symbols.append(symbol_upper)
        
        logger.info(f"Cache results: {len(fresh_symbols)} fresh, {len(stale_symbols)} need refresh")
        
        # Fetch stale data from API (could be optimized with batch API calls in future)
        for symbol in stale_symbols:
            try:
                quote_data = await self.get_stock_quote(symbol)
                quotes[symbol] = quote_data
            except Exception as e:
                logger.error(f"Failed to get quote for {symbol}: {str(e)}")
                # Don't include failed symbols in results
                continue
        
        return quotes

    async def warm_cache(self, symbols: List[str]) -> Dict[str, Any]:
        """Warm the cache by pre-fetching data for commonly used symbols"""
        try:
            logger.info(f"Warming cache for {len(symbols)} symbols...")
            
            results = {
                'success': [],
                'failed': [],
                'skipped': []
            }
            
            for symbol in symbols:
                try:
                    # Check if data is already fresh
                    is_fresh = await self.db_service.is_price_data_fresh(symbol, max_age_minutes=5)
                    
                    if is_fresh:
                        results['skipped'].append(symbol)
                        continue
                    
                    # Fetch fresh data
                    quote_data = await self._fetch_from_twelvedata(symbol)
                    if quote_data and quote_data.get('price'):
                        await self._store_price_data(symbol, quote_data)
                        results['success'].append(symbol)
                    else:
                        results['failed'].append(symbol)
                        
                except Exception as e:
                    logger.error(f"Error warming cache for {symbol}: {str(e)}")
                    results['failed'].append(symbol)
            
            logger.info(f"Cache warming complete: {len(results['success'])} success, {len(results['failed'])} failed, {len(results['skipped'])} skipped")
            return results
            
        except Exception as e:
            logger.error(f"Error during cache warming: {str(e)}")
            return {'error': str(e)}

    async def get_cache_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed cache performance metrics"""
        try:
            stats = await self.db_service.get_market_data_stats()
            
            # Calculate additional performance metrics
            total_symbols = stats.get('unique_symbols', 0)
            fresh_symbols = stats.get('freshness', {}).get('fresh_symbols', 0)
            
            cache_hit_rate = (fresh_symbols / total_symbols * 100) if total_symbols > 0 else 0
            
            # Estimate API cost savings
            total_records = stats.get('total_records', 0)
            estimated_api_calls_saved = max(0, total_records - total_symbols)  # Rough estimate
            
            # Performance classification
            if cache_hit_rate >= 80:
                performance_grade = "A"
                performance_desc = "Excellent cache performance"
            elif cache_hit_rate >= 60:
                performance_grade = "B"
                performance_desc = "Good cache performance"
            elif cache_hit_rate >= 40:
                performance_grade = "C"
                performance_desc = "Fair cache performance"
            else:
                performance_grade = "D"
                performance_desc = "Poor cache performance - needs optimization"
            
            return {
                **stats,
                'performance_metrics': {
                    'cache_hit_rate': round(cache_hit_rate, 1),
                    'performance_grade': performance_grade,
                    'performance_description': performance_desc,
                    'estimated_api_calls_saved': estimated_api_calls_saved,
                    'cost_efficiency': 'high' if cache_hit_rate > 70 else 'medium' if cache_hit_rate > 40 else 'low'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cache performance metrics: {str(e)}")
            return {'error': str(e)}

    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the current price of a stock with robust error handling and fallbacks.
        This is the preferred method for getting a stock price.
        """
        try:
            symbol = symbol.upper()
            
            # First try to get from cache
            cached_data = await self._get_cached_price(symbol)
            if cached_data and 'price' in cached_data:
                return {
                    'symbol': symbol,
                    'price': cached_data['price'],
                    'currency': cached_data.get('currency', 'USD'),
                    'last_updated': cached_data.get('last_updated'),
                    'source': 'cache'
                }
            
            # If not in cache, try to get from API
            try:
                # First try the quote endpoint
                quote_data = await self.get_stock_quote(symbol)
                if quote_data and 'price' in quote_data and quote_data['price'] > 0:
                    # Store in cache for future use
                    await self._store_price_data(symbol, quote_data)
                    return {
                        'symbol': symbol,
                        'price': quote_data['price'],
                        'currency': quote_data.get('currency', 'USD'),
                        'last_updated': datetime.now().isoformat(),
                        'source': 'api_quote'
                    }
            except Exception as quote_error:
                logger.warning(f"Quote API error for {symbol}: {str(quote_error)}")
                # Continue to next fallback
            
            # Try search as a fallback to get basic info
            try:
                search_results = await self.search_stocks(symbol)
                if search_results and len(search_results) > 0:
                    # Find exact match
                    exact_match = next((r for r in search_results if r.get('symbol', '').upper() == symbol.upper()), None)
                    
                    if exact_match:
                        # We found the symbol but couldn't get a price
                        return {
                            'symbol': symbol,
                            'error': 'Could not retrieve current price',
                            'name': exact_match.get('instrument_name'),
                            'exchange': exact_match.get('exchange'),
                            'found': True,
                            'source': 'search'
                        }
                    else:
                        # No exact match found
                        return {
                            'symbol': symbol,
                            'error': f'Symbol {symbol} not found',
                            'suggestions': [r.get('symbol') for r in search_results[:3]],
                            'found': False,
                            'source': 'search'
                        }
                else:
                    # No search results
                    return {
                        'symbol': symbol,
                        'error': f'Symbol {symbol} not found',
                        'found': False,
                        'source': 'search'
                    }
            except Exception as search_error:
                logger.warning(f"Search API error for {symbol}: {str(search_error)}")
            
            # Last resort - return error
            return {
                'symbol': symbol,
                'error': 'Could not retrieve price data from any source',
                'found': False,
                'source': 'none'
            }
            
        except Exception as e:
            logger.error(f"Error in get_stock_price for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': str(e),
                'found': False,
                'source': 'error'
            } 