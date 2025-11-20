"""
Fallback Market Data for VoicePay
Used when yfinance API is unavailable or returns no data
Based on recent market prices (November 2024)
"""

# Investment prices (approximate current market values)
FALLBACK_PRICES = {
    # Indian ETFs
    "GOLDBEES.NS": 72.8,      # Gold ETF - tracks gold prices (~12% gain)
    "NIFTYBEES.NS": 285.0,    # Nifty 50 ETF - tracks Nifty 50 index
    "LIQUIDBEES.NS": 1000.0,  # Liquid ETF - money market fund
    
    # Indices
    "^NSEI": 19500.0,         # Nifty 50 Index
    "^BSESN": 65000.0,        # BSE Sensex
    
    # International
    "GC=F": 2050.0,           # Gold Futures (USD per ounce)
    "^GSPC": 4500.0,          # S&P 500
}

# Historical performance data (weekly returns in %)
FALLBACK_RETURNS = {
    "GOLDBEES.NS": 2.5,       # Gold typically stable with modest gains
    "NIFTYBEES.NS": 1.8,      # Equity ETF moderate growth
    "LIQUIDBEES.NS": 0.15,    # Liquid fund minimal but stable
    "^NSEI": 1.8,             # Nifty 50 index
    "^BSESN": 1.9,            # Sensex
}

# Investment categories and their properties
INVESTMENT_INFO = {
    "gold": {
        "ticker": "GOLDBEES.NS",
        "name": "Gold ETF",
        "risk": "Low",
        "min_investment": 10,
        "description": "Gold-backed ETF tracking physical gold prices",
        "typical_return_annual": "8-12%"
    },
    "nifty": {
        "ticker": "NIFTYBEES.NS",
        "name": "Nifty 50 ETF",
        "risk": "Medium",
        "min_investment": 10,
        "description": "Tracks top 50 companies on NSE",
        "typical_return_annual": "10-15%"
    },
    "liquid": {
        "ticker": "LIQUIDBEES.NS",
        "name": "Liquid Fund ETF",
        "risk": "Very Low",
        "min_investment": 10,
        "description": "Money market fund for parking cash",
        "typical_return_annual": "6-8%"
    }
}

def get_fallback_price(ticker: str) -> float:
    """Get fallback price for a ticker"""
    return FALLBACK_PRICES.get(ticker)

def get_fallback_return(ticker: str) -> float:
    """Get fallback weekly return for a ticker"""
    return FALLBACK_RETURNS.get(ticker, 0.0)

def get_investment_info(investment_type: str) -> dict:
    """Get detailed info about an investment type"""
    return INVESTMENT_INFO.get(investment_type.lower(), {})

def update_fallback_price(ticker: str, price: float):
    """
    Update fallback price (useful for periodic updates)
    Note: This only updates in-memory, not persisted
    """
    FALLBACK_PRICES[ticker] = price
    print(f"Updated fallback price for {ticker}: ₹{price}")

# Sample usage
if __name__ == "__main__":
    print("=== VoicePay Fallback Market Data ===\n")
    
    print("Investment Options:")
    print("-" * 50)
    for inv_type, info in INVESTMENT_INFO.items():
        price = get_fallback_price(info['ticker'])
        print(f"\n{info['name']} ({inv_type.upper()})")
        print(f"  Ticker: {info['ticker']}")
        print(f"  Price: ₹{price}")
        print(f"  Risk: {info['risk']}")
        print(f"  Min Investment: ₹{info['min_investment']}")
        print(f"  Expected Return: {info['typical_return_annual']}")
    
    print("\n" + "=" * 50)
    print("All fallback prices available ✅")

