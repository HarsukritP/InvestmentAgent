"""Market context service for AI Portfolio Agent"""
import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketContextService:
    def __init__(self, db_service=None):
        # API keys
        self.fred_api_key = os.getenv("FRED_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # Base URLs
        self.fred_base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.news_api_base_url = "https://newsapi.org/v2"
        
        # Import database service for caching
        if db_service is None:
            from database import db_service as default_db_service
            self.db_service = default_db_service
        else:
            self.db_service = db_service
            
        # Log configuration status
        if not self.fred_api_key:
            print("⚠️  ERROR: FRED_API_KEY not found in environment variables")
            raise ValueError("FRED_API_KEY not configured. This service requires real API data.")
            
        if not self.news_api_key:
            print("⚠️  ERROR: NEWS_API_KEY not found in environment variables")
            raise ValueError("NEWS_API_KEY not configured. This service requires real API data.")
        
        print(f"✅ FRED API configured")
        print(f"✅ News API configured")
            
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators from FRED with caching"""
        try:
            # Check cache first
            cache_key = "economic_indicators"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            # Key economic indicators to track
            indicators = {
                "GDP": "Gross Domestic Product",
                "UNRATE": "Unemployment Rate",
                "CPIAUCSL": "Consumer Price Index (Inflation)",
                "FEDFUNDS": "Federal Funds Rate",
                "T10Y2Y": "10Y-2Y Treasury Yield Spread (Recession Indicator)",
                "UMCSENT": "Consumer Sentiment Index"
            }
            
            results = {}
            
            for series_id, description in indicators.items():
                try:
                    # Fetch the latest value for each indicator
                    params = {
                        "series_id": series_id,
                        "api_key": self.fred_api_key,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 1
                    }
                    
                    response = requests.get(self.fred_base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "observations" in data and len(data["observations"]) > 0:
                        latest = data["observations"][0]
                        results[series_id] = {
                            "name": description,
                            "value": float(latest["value"]) if latest["value"] != "." else None,
                            "date": latest["date"],
                            "units": self._get_units_for_indicator(series_id)
                        }
                except Exception as e:
                    logger.error(f"Error fetching {series_id}: {str(e)}")
                    # Continue with other indicators if one fails
                    results[series_id] = {
                        "name": description,
                        "value": None,
                        "error": str(e)
                    }
            
            # Add timestamp and cache
            results["_timestamp"] = datetime.now().isoformat()
            results["_source"] = "FRED API"
            
            # Cache the results
            await self._cache_data(cache_key, results, 24 * 60)  # Cache for 24 hours
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting economic indicators: {str(e)}")
            raise Exception(f"Failed to fetch economic indicators: {str(e)}")
    
    def _get_units_for_indicator(self, series_id: str) -> str:
        """Get the units for a specific economic indicator"""
        units_map = {
            "GDP": "Billions of USD",
            "UNRATE": "Percent",
            "CPIAUCSL": "Index",
            "FEDFUNDS": "Percent",
            "T10Y2Y": "Percentage Points",
            "UMCSENT": "Index"
        }
        return units_map.get(series_id, "Value")
    
    async def get_market_news(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get financial news with optional stock-specific news"""
        try:
            # Check cache first
            cache_key = f"market_news_{','.join(symbols) if symbols else 'general'}"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            results = {
                "general_news": [],
                "symbol_news": {}
            }
            
            # Get general financial news
            params = {
                "apiKey": self.news_api_key,
                "category": "business",
                "language": "en",
                "pageSize": 10
            }
            
            response = requests.get(f"{self.news_api_base_url}/top-headlines", params=params)
            response.raise_for_status()
            data = response.json()
            
            if "articles" in data:
                results["general_news"] = [
                    {
                        "title": article["title"],
                        "source": article["source"]["name"],
                        "published_at": article["publishedAt"],
                        "url": article["url"],
                        "description": article["description"]
                    }
                    for article in data["articles"]
                ]
            
            # Get stock-specific news if symbols provided
            if symbols:
                for symbol in symbols:
                    params = {
                        "apiKey": self.news_api_key,
                        "q": symbol,
                        "language": "en",
                        "pageSize": 5
                    }
                    
                    response = requests.get(f"{self.news_api_base_url}/everything", params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "articles" in data:
                        results["symbol_news"][symbol] = [
                            {
                                "title": article["title"],
                                "source": article["source"]["name"],
                                "published_at": article["publishedAt"],
                                "url": article["url"],
                                "description": article["description"]
                            }
                            for article in data["articles"][:5]  # Limit to 5 articles per symbol
                        ]
            
            # Add timestamp and cache
            results["_timestamp"] = datetime.now().isoformat()
            results["_source"] = "News API"
            
            # Cache the results - shorter cache time for news
            await self._cache_data(cache_key, results, 60)  # Cache for 1 hour
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting market news: {str(e)}")
            raise Exception(f"Failed to fetch market news: {str(e)}")
    
    async def analyze_market_sentiment(self) -> Dict[str, Any]:
        """Analyze current market sentiment based on news and indicators"""
        try:
            # Get economic data and news
            economic_data = await self.get_economic_indicators()
            news_data = await self.get_market_news()
            
            # Simple sentiment analysis based on economic indicators
            sentiment_score = 0
            sentiment_factors = []
            
            # Analyze yield curve (recession indicator)
            if "T10Y2Y" in economic_data:
                yield_spread = economic_data["T10Y2Y"].get("value")
                if yield_spread is not None:
                    if yield_spread < -0.5:
                        sentiment_score -= 2
                        sentiment_factors.append("Inverted yield curve suggests recession risk")
                    elif yield_spread < 0:
                        sentiment_score -= 1
                        sentiment_factors.append("Slightly inverted yield curve suggests caution")
                    else:
                        sentiment_score += 0.5
                        sentiment_factors.append("Normal yield curve suggests economic stability")
            
            # Analyze unemployment
            if "UNRATE" in economic_data:
                unemployment = economic_data["UNRATE"].get("value")
                if unemployment is not None:
                    if unemployment < 4:
                        sentiment_score += 1
                        sentiment_factors.append("Low unemployment indicates strong job market")
                    elif unemployment > 6:
                        sentiment_score -= 1
                        sentiment_factors.append("Higher unemployment suggests economic challenges")
            
            # Analyze fed funds rate
            if "FEDFUNDS" in economic_data:
                fed_rate = economic_data["FEDFUNDS"].get("value")
                if fed_rate is not None:
                    if fed_rate > 5:
                        sentiment_score -= 0.5
                        sentiment_factors.append("High interest rates may slow economic growth")
                    elif fed_rate < 2:
                        sentiment_score += 0.5
                        sentiment_factors.append("Low interest rates support economic expansion")
            
            # Analyze consumer sentiment
            if "UMCSENT" in economic_data:
                consumer_sentiment = economic_data["UMCSENT"].get("value")
                if consumer_sentiment is not None:
                    if consumer_sentiment > 90:
                        sentiment_score += 1
                        sentiment_factors.append("Strong consumer sentiment indicates positive outlook")
                    elif consumer_sentiment < 70:
                        sentiment_score -= 1
                        sentiment_factors.append("Weak consumer sentiment suggests consumer caution")
            
            # Determine overall sentiment
            sentiment_category = "neutral"
            if sentiment_score >= 2:
                sentiment_category = "very_bullish"
            elif sentiment_score >= 0.5:
                sentiment_category = "bullish"
            elif sentiment_score <= -2:
                sentiment_category = "very_bearish"
            elif sentiment_score <= -0.5:
                sentiment_category = "bearish"
            
            # Format the response
            result = {
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category,
                "sentiment_factors": sentiment_factors,
                "economic_indicators_summary": self._summarize_economic_indicators(economic_data),
                "_timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {str(e)}")
            raise Exception(f"Failed to analyze market sentiment: {str(e)}")
    
    def _summarize_economic_indicators(self, economic_data: Dict[str, Any]) -> str:
        """Create a text summary of economic indicators"""
        if not economic_data:
            return "Economic data unavailable"
        
        summary_points = []
        
        # GDP
        if "GDP" in economic_data and economic_data["GDP"].get("value") is not None:
            summary_points.append(f"GDP: {economic_data['GDP']['value']} {economic_data['GDP']['units']}")
        
        # Unemployment
        if "UNRATE" in economic_data and economic_data["UNRATE"].get("value") is not None:
            summary_points.append(f"Unemployment: {economic_data['UNRATE']['value']}%")
        
        # Inflation
        if "CPIAUCSL" in economic_data and economic_data["CPIAUCSL"].get("value") is not None:
            summary_points.append(f"Inflation: {economic_data['CPIAUCSL']['value']}%")
        
        # Fed Rate
        if "FEDFUNDS" in economic_data and economic_data["FEDFUNDS"].get("value") is not None:
            summary_points.append(f"Fed Rate: {economic_data['FEDFUNDS']['value']}%")
        
        # Yield Curve
        if "T10Y2Y" in economic_data and economic_data["T10Y2Y"].get("value") is not None:
            curve_status = "inverted" if economic_data["T10Y2Y"]["value"] < 0 else "normal"
            summary_points.append(f"Yield Curve: {curve_status} ({economic_data['T10Y2Y']['value']} points)")
        
        return ", ".join(summary_points)
    
    async def get_market_context(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive market context including economic data, news, and sentiment"""
        try:
            # Get all the data components
            economic_data = await self.get_economic_indicators()
            news_data = await self.get_market_news(symbols)
            sentiment_analysis = await self.analyze_market_sentiment()
            
            # Combine into a comprehensive context
            market_context = {
                "economic_indicators": economic_data,
                "market_news": news_data,
                "market_sentiment": sentiment_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            return market_context
            
        except Exception as e:
            logger.error(f"Error getting market context: {str(e)}")
            raise Exception(f"Failed to get market context: {str(e)}")
    
    async def _get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if available and fresh"""
        try:
            # Check if we have the data in the database
            cache_data = await self.db_service.get_cached_market_context(key)
            
            if cache_data:
                # Check if the cache is still fresh
                cache_time = datetime.fromisoformat(cache_data.get("timestamp", "2000-01-01T00:00:00"))
                cache_age_minutes = (datetime.now() - cache_time).total_seconds() / 60
                
                # Get the max age based on the type of data
                if "news" in key:
                    max_age = 60  # News cache for 1 hour
                else:
                    max_age = 24 * 60  # Economic data cache for 24 hours
                
                if cache_age_minutes < max_age:
                    print(f"🎯 CACHE HIT | {key} | Age: {cache_age_minutes:.1f} min")
                    return cache_data["data"]
                else:
                    print(f"⏰ CACHE EXPIRED | {key} | Age: {cache_age_minutes:.1f} min > {max_age} min")
            else:
                print(f"❌ CACHE MISS | {key} | No data found")
                
            return None
        except Exception as e:
            logger.error(f"Cache error: {str(e)}")
            return None
    
    async def _cache_data(self, key: str, data: Dict[str, Any], max_age_minutes: int) -> bool:
        """Cache data with expiration"""
        try:
            # Store in database cache
            await self.db_service.store_market_context(key, data)
            print(f"💾 CACHE STORE | {key} | Max age: {max_age_minutes} min")
            return True
        except Exception as e:
            logger.error(f"Cache error: {str(e)}")
            return False
