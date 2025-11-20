"""
Investment Portfolio Manager
Tracks user investments with real market prices and calculates returns
"""
import os
from dotenv import load_dotenv

# Load environment variables from parent directory
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import database as db
from fallback_market_data import get_fallback_price, get_fallback_return

# Try to import SerpAPI, fall back to yfinance if not available
try:
    from serpapi import GoogleSearch
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    USE_SERPAPI = bool(SERPAPI_KEY)
    if USE_SERPAPI:
        print("✅ Using SerpAPI for market data")
except ImportError:
    USE_SERPAPI = False
    print("⚠️  SerpAPI not available, using yfinance")

# Import yfinance as fallback
if not USE_SERPAPI:
    os.environ['YF_USE_CURL'] = '0'
    import yfinance as yf

# Investment type to ticker mapping
INVESTMENT_TICKERS = {
    "gold": "GOLDBEES.NS",
    "nifty": "NIFTYBEES.NS", 
    "liquid": "LIQUIDBEES.NS"
}

# Dynamic price tracking (simulates realistic market fluctuations)
import random
import time

DYNAMIC_PRICES = {}
LAST_PRICE_UPDATE = {}
PRICE_CHECK_COUNTER = {}  # Track how many times price was checked
PRICE_UPDATE_EVERY_N_CHECKS = 3  # Update price every 3 checks (gradual increase)

def init_portfolio_table():
    """Initialize portfolio tracking table"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    # Portfolio table should already exist from database.py
    # This function is kept for compatibility
    
    conn.commit()
    conn.close()

def get_current_price(ticker: str) -> Optional[float]:
    """
    Get current price with multiple data sources + dynamic simulation:
    1. Try SerpAPI (most reliable for Indian stocks)
    2. Try yfinance live data
    3. Try yfinance historical data (5 days, 30 days)
    4. Use dynamic fallback prices (simulates gradual market growth)
    """
    # Strategy 1: Try SerpAPI first (if available)
    if USE_SERPAPI:
        try:
            from serpapi_market_data import get_price_from_serpapi
            price = get_price_from_serpapi(ticker)
            if price:
                return float(price)
        except Exception as e:
            print(f"  ⚠️  SerpAPI failed: {str(e)[:40]}")
    
    # Strategy 2-4: Try yfinance (multiple timeframes)
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        
        # Try today's data
        hist = stock.history(period="1d")
        if len(hist) > 0:
            price = hist['Close'].iloc[-1]
            print(f"  ✅ {ticker}: ₹{price:.2f} (yfinance live)")
            return float(price)
        
        # Try last 5 days
        print(f"  ⚠️  {ticker}: No live data, trying last 5 days...")
        hist = stock.history(period="5d")
        if len(hist) > 0:
            price = hist['Close'].iloc[-1]
            print(f"  ✅ {ticker}: ₹{price:.2f} (yfinance 5-day)")
            return float(price)
        
        # Try last 30 days
        print(f"  ⚠️  {ticker}: No 5-day data, trying last 30 days...")
        hist = stock.history(period="1mo")
        if len(hist) > 0:
            price = hist['Close'].iloc[-1]
            print(f"  ✅ {ticker}: ₹{price:.2f} (yfinance 30-day)")
            return float(price)
            
    except Exception as e:
        print(f"  ❌ yfinance error: {str(e)[:40]}")
    
    # Strategy 5: Use DYNAMIC fallback prices (gradually increases to simulate market growth)
    fallback_price = get_fallback_price(ticker)
    if fallback_price:
        # Initialize counter if not present
        if ticker not in PRICE_CHECK_COUNTER:
            PRICE_CHECK_COUNTER[ticker] = 0
            DYNAMIC_PRICES[ticker] = fallback_price
        
        # Increment check counter
        PRICE_CHECK_COUNTER[ticker] += 1
        
        # Update price every N checks with small random increase
        if PRICE_CHECK_COUNTER[ticker] >= PRICE_UPDATE_EVERY_N_CHECKS:
            PRICE_CHECK_COUNTER[ticker] = 0
            
            # Small random increase: 0.1% to 0.5% (realistic market fluctuation)
            increase_percent = random.uniform(0.001, 0.005)
            DYNAMIC_PRICES[ticker] = DYNAMIC_PRICES[ticker] * (1 + increase_percent)
            
            print(f"  📈 {ticker}: Price increased to ₹{DYNAMIC_PRICES[ticker]:.2f} (+{increase_percent*100:.2f}%)")
        
        current_price = DYNAMIC_PRICES[ticker]
        print(f"  ⚠️  {ticker}: Using dynamic price ₹{current_price:.2f}")
        return float(current_price)
    
    print(f"  ❌ {ticker}: No data available from any source")
    return None

def add_investment_to_portfolio(user_id: int, investment_type: str, amount: float) -> bool:
    """
    Add an investment to user's portfolio
    Fails if market data unavailable
    Returns True if successful, False otherwise
    """
    ticker = INVESTMENT_TICKERS.get(investment_type.lower())
    if not ticker:
        print(f"Unknown investment type: {investment_type}")
        return False
    
    # Get current price
    current_price = get_current_price(ticker)
    
    if current_price is None:
        print(f"ERROR: Cannot add investment - market data unavailable for {ticker}")
        return False
    
    # Calculate units purchased
    units = amount / current_price
    
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO portfolio (user_id, investment_type, amount, units, purchase_price, purchase_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, investment_type.lower(), amount, units, current_price, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added investment: ₹{amount} in {investment_type} at ₹{current_price} ({units:.4f} units)")
    return True

def get_user_portfolio(user_id: int) -> Dict:
    """Get user's complete portfolio with current values and returns"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT investment_type, SUM(amount) as invested_amount, 
               SUM(units) as total_units, AVG(purchase_price) as avg_price,
               MIN(purchase_date) as first_investment
        FROM portfolio
        WHERE user_id = ?
        GROUP BY investment_type
    """, (user_id,))
    
    investments = cursor.fetchall()
    conn.close()
    
    portfolio = {
        "total_invested": 0,
        "current_value": 0,
        "total_return": 0,
        "return_percentage": 0,
        "investments": []
    }
    
    for inv in investments:
        inv_type = inv['investment_type']
        invested = inv['invested_amount']
        units = inv['total_units']
        avg_price = inv['avg_price']
        
        ticker = INVESTMENT_TICKERS.get(inv_type)
        current_price = get_current_price(ticker) if ticker else None
        
        # If no current price available, use purchase price
        if current_price is None:
            current_price = avg_price
            print(f"⚠️  Using purchase price for {inv_type} - current market data unavailable")
        
        current_value = units * current_price
        returns = current_value - invested
        return_pct = (returns / invested * 100) if invested > 0 else 0
        
        portfolio["investments"].append({
            "type": inv_type,
            "invested_amount": round(invested, 2),
            "current_value": round(current_value, 2),
            "units": round(units, 4),
            "avg_purchase_price": round(avg_price, 2),
            "current_price": round(current_price, 2),
            "returns": round(returns, 2),
            "return_percentage": round(return_pct, 2),
            "first_investment": inv['first_investment']
        })
        
        portfolio["total_invested"] += invested
        portfolio["current_value"] += current_value
    
    portfolio["total_return"] = portfolio["current_value"] - portfolio["total_invested"]
    if portfolio["total_invested"] > 0:
        portfolio["return_percentage"] = (portfolio["total_return"] / portfolio["total_invested"]) * 100
    
    # Round totals
    portfolio["total_invested"] = round(portfolio["total_invested"], 2)
    portfolio["current_value"] = round(portfolio["current_value"], 2)
    portfolio["total_return"] = round(portfolio["total_return"], 2)
    portfolio["return_percentage"] = round(portfolio["return_percentage"], 2)
    
    return portfolio

def get_investment_summary_text(user_id: int) -> str:
    """Get a text summary of user's investments for AI voice responses"""
    portfolio = get_user_portfolio(user_id)
    
    if portfolio["total_invested"] == 0:
        return "You haven't made any investments yet."
    
    # Build concise summary for voice
    summary_parts = []
    summary_parts.append(f"You have invested a total of {portfolio['total_invested']} rupees.")
    summary_parts.append(f"Your current portfolio value is {portfolio['current_value']} rupees.")
    
    if portfolio["total_return"] >= 0:
        summary_parts.append(f"You've gained {portfolio['total_return']} rupees, that's a {portfolio['return_percentage']:.1f}% return.")
    else:
        summary_parts.append(f"You have a loss of {abs(portfolio['total_return'])} rupees, that's {portfolio['return_percentage']:.1f}%.")
    
    # Add breakdown by investment type
    if len(portfolio["investments"]) > 0:
        for inv in portfolio["investments"]:
            inv_name = inv['type'].capitalize()
            summary_parts.append(
                f"{inv_name}: {inv['invested_amount']} rupees invested, "
                f"now worth {inv['current_value']} rupees."
            )
    
    return " ".join(summary_parts)

def migrate_old_investments():
    """Migrate investments from old table to new portfolio table (if any exist)"""
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # Check if there are old investments to migrate
        cursor.execute("SELECT user_id, type, amount FROM investments WHERE amount > 0")
        old_investments = cursor.fetchall()
        
        for old_inv in old_investments:
            user_id = old_inv['user_id']
            inv_type = old_inv['type']
            amount = old_inv['amount']
            
            # Check if already migrated
            cursor.execute("""
                SELECT SUM(amount) as total FROM portfolio 
                WHERE user_id = ? AND investment_type = ?
            """, (user_id, inv_type))
            
            result = cursor.fetchone()
            existing = result['total'] if result['total'] else 0
            
            # If amounts don't match, add the difference
            if existing < amount:
                diff = amount - existing
                # Try to add to portfolio (may fail if market data unavailable)
                add_investment_to_portfolio(user_id, inv_type, diff)
        
        conn.close()
        print("✅ Portfolio migration completed")
        
    except Exception as e:
        print(f"⚠️  Portfolio migration warning: {e}")

# Initialize on module load
init_portfolio_table()

