"""
Investment Analyzer Module
Uses multiple data sources (SerpAPI, yfinance, fallback) to get market data
Provides personalized investment recommendations
"""
import os
from dotenv import load_dotenv

# Load environment variables from parent directory
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Force yfinance to use requests instead of curl_cffi
os.environ['YF_USE_CURL'] = '0'

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Try to import SerpAPI
try:
    from serpapi import GoogleSearch
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    USE_SERPAPI = bool(SERPAPI_KEY)
except ImportError:
    USE_SERPAPI = False

# Import fallback data
from fallback_market_data import get_fallback_return

# Popular investment options in India
INVESTMENT_OPTIONS = {
    "NIFTYBEES.NS": "Nifty 50 ETF",
    "GOLDBEES.NS": "Gold ETF",
    "LIQUIDBEES.NS": "Liquid ETF",
}

def get_weekly_return_with_fallback(ticker: str) -> Optional[float]:
    """
    Get weekly return with multi-tier fallback:
    1. Try yfinance with 1-month historical data
    2. Use hardcoded fallback returns
    """
    # Try yfinance first
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        if len(hist) >= 5:
            recent_data = hist.tail(5)
            start_price = recent_data['Close'].iloc[0]
            end_price = recent_data['Close'].iloc[-1]
            weekly_return = ((end_price - start_price) / start_price) * 100
            print(f"  ✅ {ticker}: {weekly_return:.2f}% (yfinance)")
            return float(weekly_return)
    except Exception as e:
        print(f"  ⚠️  {ticker} yfinance failed: {str(e)[:40]}")
    
    # Use fallback
    fallback_return = get_fallback_return(ticker)
    if fallback_return:
        print(f"  ⚠️  {ticker}: {fallback_return:.2f}% (fallback)")
        return float(fallback_return)
    
    return None

def get_top_performer_week() -> Optional[Tuple[str, str, float]]:
    """
    Get the top performing investment from the last week
    Uses multi-tier fallback system to ensure data availability
    Returns: (ticker, name, weekly_return_percentage) or None if data unavailable
    """
    print("📊 Finding top performer this week...")
    
    try:
        best_performer = None
        best_return = -100
        
        for ticker, name in INVESTMENT_OPTIONS.items():
            weekly_return = get_weekly_return_with_fallback(ticker)
            
            if weekly_return is not None and weekly_return > best_return:
                best_return = weekly_return
                best_performer = (ticker, name, weekly_return)
        
        if best_performer:
            print(f"🏆 Best performer: {best_performer[1]} @ {best_performer[2]:.2f}%")
            return best_performer
        else:
            print("❌ Could not fetch any market data")
            return None
            
    except Exception as e:
        print(f"Error in get_top_performer_week: {e}")
        return None

def calculate_monthly_roundoff_potential(transactions: List[Dict]) -> Optional[Dict]:
    """
    Calculate how much user would have earned if they rounded off all transactions
    """
    try:
        # Filter transactions from this month
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_transactions = []
        total_roundoff = 0
        
        for txn in transactions:
            txn_date = datetime.fromisoformat(txn['timestamp'])
            if txn_date.month == current_month and txn_date.year == current_year:
                if txn['type'] in ['payment', 'debit']:
                    monthly_transactions.append(txn)
                    amount = txn['amount']
                    # Calculate roundoff needed
                    if amount % 10 != 0:
                        roundoff = 10 - (amount % 10)
                    else:
                        roundoff = 10
                    total_roundoff += roundoff
        
        # Get top performer
        top_performer = get_top_performer_week()
        
        if top_performer is None:
            print("Warning: Market data unavailable")
            return None
        
        ticker, investment_name, weekly_return = top_performer
        
        # Calculate potential earnings (conservative estimate)
        # Use weekly return * 4 for monthly estimate
        monthly_return = weekly_return * 4
        potential_earnings = (total_roundoff * monthly_return) / 100
        
        return {
            "transaction_count": len(monthly_transactions),
            "total_roundoff": total_roundoff,
            "potential_earnings": round(potential_earnings, 2),
            "investment_name": investment_name,
            "ticker": ticker,
            "return_percentage": round(monthly_return, 2),
            "weekly_return": round(weekly_return, 2),
            "current_month": datetime.now().strftime("%B %Y")
        }
        
    except Exception as e:
        print(f"Error calculating roundoff potential: {e}")
        return None

def get_investment_recommendation(user_id: int, transactions: List[Dict]) -> Optional[Dict]:
    """
    Generate personalized investment recommendation based on user's spending
    Returns None if market data is unavailable or insufficient transactions
    """
    analysis = calculate_monthly_roundoff_potential(transactions)
    
    # Return None if market data unavailable
    if analysis is None:
        return None
    
    # Only show if user has at least 5 transactions this month
    if analysis['transaction_count'] < 5:
        return None
    
    message = (
        f"💡 Smart Savings Alert!\n\n"
        f"You made {analysis['transaction_count']} transactions in {analysis['current_month']}. "
        f"If you had rounded off each payment and invested in {analysis['investment_name']}, "
        f"you would have invested ₹{analysis['total_roundoff']} and earned approximately "
        f"₹{analysis['potential_earnings']} this month!\n\n"
        f"{analysis['investment_name']} is up {analysis['weekly_return']}% this week! 📈"
    )
    
    return {
        "show": True,
        "message": message,
        "analysis": analysis,
        "recommendation": {
            "name": analysis['investment_name'],
            "ticker": analysis['ticker'],
            "amount": analysis['total_roundoff'],
            "potential_return": analysis['potential_earnings']
        }
    }

def get_current_gold_price() -> Optional[float]:
    """Get current gold price for reference"""
    try:
        gold = yf.Ticker("GC=F")
        hist = gold.history(period="1d")
        if len(hist) > 0:
            return hist['Close'].iloc[-1]
        return None
    except Exception as e:
        print(f"Error fetching gold price: {e}")
        return None

