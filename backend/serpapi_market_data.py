"""
SerpAPI Integration for Market Data
More reliable than yfinance for Indian stock market data
"""
import os
from typing import Optional, Dict
from dotenv import load_dotenv
import os

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

try:
    from serpapi import GoogleSearch
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    SERPAPI_AVAILABLE = bool(SERPAPI_KEY)
except ImportError:
    SERPAPI_AVAILABLE = False
    SERPAPI_KEY = None

# Mapping of our tickers to Google Finance symbols
TICKER_TO_GOOGLE_FINANCE = {
    "GOLDBEES.NS": "GOLDBEES:NSE",
    "NIFTYBEES.NS": "NIFTYBEES:NSE",
    "LIQUIDBEES.NS": "LIQUIDBEES:NSE",
    "^NSEI": "NIFTY_50:INDEXNSE",
    "^BSESN": "SENSEX:INDEXBOM",
}

def get_price_from_serpapi(ticker: str) -> Optional[float]:
    """
    Fetch current price using SerpAPI Google Finance
    
    Args:
        ticker: Ticker symbol (e.g., "GOLDBEES.NS")
    
    Returns:
        Current price as float, or None if unavailable
    """
    if not SERPAPI_AVAILABLE:
        print(f"  ⚠️  SerpAPI not configured")
        return None
    
    # Convert ticker to Google Finance format
    google_symbol = TICKER_TO_GOOGLE_FINANCE.get(ticker)
    if not google_symbol:
        print(f"  ⚠️  {ticker}: No Google Finance mapping")
        return None
    
    try:
        params = {
            "engine": "google_finance",
            "q": google_symbol,
            "api_key": SERPAPI_KEY
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extract price from results
        if "summary" in results:
            summary = results["summary"]
            
            # Try to get current price
            if "price" in summary:
                price = float(summary["price"])
                print(f"  ✅ {ticker}: ₹{price:.2f} (SerpAPI)")
                return price
            
            # Try to get price from string (e.g., "65.50 INR")
            if "price_movement" in summary:
                price_str = summary["price_movement"].get("price", "")
                try:
                    price = float(price_str.replace(",", "").split()[0])
                    print(f"  ✅ {ticker}: ₹{price:.2f} (SerpAPI)")
                    return price
                except (ValueError, IndexError):
                    pass
        
        # Try markets data
        if "markets" in results:
            for market in results["markets"]:
                if "price" in market:
                    price = float(market["price"])
                    print(f"  ✅ {ticker}: ₹{price:.2f} (SerpAPI markets)")
                    return price
        
        print(f"  ⚠️  {ticker}: No price in SerpAPI response")
        return None
        
    except Exception as e:
        print(f"  ❌ SerpAPI error for {ticker}: {str(e)[:60]}")
        return None

def get_market_info(ticker: str) -> Optional[Dict]:
    """
    Get detailed market information using SerpAPI
    
    Returns:
        Dict with price, change, change_percent, etc.
    """
    if not SERPAPI_AVAILABLE:
        return None
    
    google_symbol = TICKER_TO_GOOGLE_FINANCE.get(ticker)
    if not google_symbol:
        return None
    
    try:
        params = {
            "engine": "google_finance",
            "q": google_symbol,
            "api_key": SERPAPI_KEY
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "summary" in results:
            return results["summary"]
        
        return None
        
    except Exception as e:
        print(f"Error fetching market info: {e}")
        return None

# Test function
if __name__ == "__main__":
    print("=== SerpAPI Market Data Test ===\n")
    
    if not SERPAPI_AVAILABLE:
        print("❌ SerpAPI not available")
        print("   Install: pip install google-search-results")
        print("   Set SERPAPI_KEY in .env file")
    else:
        print(f"✅ SerpAPI configured")
        print(f"   API Key: {SERPAPI_KEY[:10]}...\n")
        
        test_tickers = ["GOLDBEES.NS", "NIFTYBEES.NS", "LIQUIDBEES.NS"]
        
        for ticker in test_tickers:
            print(f"Testing {ticker}:")
            price = get_price_from_serpapi(ticker)
            if price:
                print(f"  Price: ₹{price}\n")
            else:
                print(f"  Failed to get price\n")

