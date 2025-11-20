"""
SQLite Database Module for VoicePay
Handles all database operations for users, transactions, investments, and portfolio
"""
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
import os
from fuzzywuzzy import fuzz, process

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "voicepay.db")

def get_db_connection():
    """Get database connection with row factory and concurrency handling"""
    conn = sqlite3.connect(
        DATABASE_PATH,
        timeout=30.0,  # Wait up to 30 seconds if database is locked
        check_same_thread=False  # Allow use across threads (needed for FastAPI)
    )
    conn.row_factory = sqlite3.Row
    # Enable Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
    return conn

def init_database():
    """Initialize database with schema and sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone_number TEXT UNIQUE,
            balance REAL NOT NULL DEFAULT 12000,
            pin TEXT NOT NULL DEFAULT '1234',
            google_id TEXT UNIQUE,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            recipient TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create investments table (legacy support)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, type)
        )
    """)
    
    # Create portfolio table for detailed tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            investment_type TEXT NOT NULL,
            amount REAL NOT NULL,
            units REAL NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create conversation state table for multi-turn dialogs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            state TEXT NOT NULL,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Check if users exist, if not add sample data
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()['count'] == 0:
        # Insert sample users (for demo/testing)
        sample_users = [
            ("Niraj", None, None, None, 10000, "1234"),
            ("Rahul", None, None, None, 15000, "1234"),
            ("Priya", None, None, None, 20000, "1234"),
            ("Amit", None, None, None, 12000, "1234")
        ]
        
        cursor.executemany(
            "INSERT INTO users (name, email, google_id, picture, balance, pin) VALUES (?, ?, ?, ?, ?, ?)",
            sample_users
        )
        
        print("✅ Sample users created")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# User operations
def get_all_users() -> List[Dict]:
    """Get all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, balance FROM users ORDER BY name")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_name(name: str) -> Optional[Dict]:
    """
    Get user by name with fuzzy matching for voice recognition typos
    Handles TTS/STT errors like: "Neeraj" → "Niraj", "Rahool" → "Rahul"
    
    Matching strategies (in order):
    1. Exact match: "Niraj" → Niraj
    2. Partial/contains: "raj" → Niraj
    3. Fuzzy match (80%+ similarity): "Neeraj" → Niraj
    4. First name match: "john" → John Doe
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Strategy 1: Try exact match first (fastest)
    cursor.execute("SELECT * FROM users WHERE LOWER(name) = LOWER(?)", (name,))
    user = cursor.fetchone()
    if user:
        # Removed verbose logging to reduce console spam
        conn.close()
        return dict(user)
    
    # Strategy 2: Try partial match (contains)
    search_pattern = f"%{name}%"
    cursor.execute(
        "SELECT * FROM users WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 1",
        (search_pattern,)
    )
    user = cursor.fetchone()
    if user:
        # Reduced verbose logging
        conn.close()
        return dict(user)
    
    # Strategy 3: Fuzzy matching for voice recognition typos
    # Get all users for fuzzy comparison
    cursor.execute("SELECT * FROM users")
    all_users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not all_users:
        return None
    
    # Try fuzzy matching on full names (using token_sort_ratio for better matching)
    user_names = {user['name']: user for user in all_users}
    best_match = process.extractOne(name, user_names.keys(), scorer=fuzz.token_sort_ratio)
    
    if best_match and best_match[1] >= 65:  # LOWERED: 65% similarity threshold for full names (was 70%)
        matched_name = best_match[0]
        print(f"🎯 Fuzzy match: '{name}' → '{matched_name}' ({best_match[1]}%)")
        return user_names[matched_name]
    
    # Strategy 4: Try fuzzy matching on first names only (most common for voice commands)
    first_names = {}
    for user in all_users:
        first_name = user['name'].split()[0]
        first_names[first_name] = user
    
    # Use multiple fuzzy algorithms for better voice typo matching
    best_match_ratio = process.extractOne(name, first_names.keys(), scorer=fuzz.ratio)
    best_match_partial = process.extractOne(name, first_names.keys(), scorer=fuzz.partial_ratio)
    
    # Take the best match from both algorithms
    best_match = best_match_ratio
    if best_match_partial and best_match_partial[1] > best_match[1]:
        best_match = best_match_partial
    
    if best_match and best_match[1] >= 60:  # LOWERED: 60% threshold for first name TTS/transliteration errors (was 65%)
        matched_first_name = best_match[0]
        matched_user = first_names[matched_first_name]
        print(f"🎯 Fuzzy first name: '{name}' → '{matched_user['name']}' ({best_match[1]}%)")
        return matched_user
    
    print(f"❌ No match: '{name}' (best was {best_match[1] if best_match else 0}%)")
    return None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_phone(phone_number: str) -> Optional[Dict]:
    """Get user by phone number"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_phone(user_id: int, phone_number: str):
    """Update user's phone number"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET phone_number = ? WHERE id = ?",
        (phone_number, user_id)
    )
    conn.commit()
    conn.close()

def link_accounts(google_user_id: int, phone_user_id: int):
    """Merge phone-based account into Google account"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get phone account balance
    cursor.execute("SELECT balance FROM users WHERE id = ?", (phone_user_id,))
    phone_user = cursor.fetchone()
    phone_balance = phone_user['balance'] if phone_user else 0
    
    # Transfer balance to Google account
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE id = ?",
        (phone_balance, google_user_id)
    )
    
    # Transfer transactions
    cursor.execute(
        "UPDATE transactions SET user_id = ? WHERE user_id = ?",
        (google_user_id, phone_user_id)
    )
    
    # Transfer portfolio
    cursor.execute(
        "UPDATE portfolio SET user_id = ? WHERE user_id = ?",
        (google_user_id, phone_user_id)
    )
    
    # Delete old phone account
    cursor.execute("DELETE FROM users WHERE id = ?", (phone_user_id,))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Linked phone account {phone_user_id} to Google account {google_user_id}")

def save_conversation_state(user_id: int, state: str, context: dict):
    """Save conversation state for multi-turn dialogs"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear old states for this user
    cursor.execute("DELETE FROM conversation_state WHERE user_id = ?", (user_id,))
    
    # Save new state
    cursor.execute(
        "INSERT INTO conversation_state (user_id, state, context) VALUES (?, ?, ?)",
        (user_id, state, json.dumps(context))
    )
    conn.commit()
    conn.close()
    print(f"💾 Saved conversation state: {state} for user {user_id}")

def get_conversation_state(user_id: int) -> Optional[Dict]:
    """Get current conversation state"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversation_state WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    state = cursor.fetchone()
    conn.close()
    
    if state:
        return {
            'state': state['state'],
            'context': json.loads(state['context'])
        }
    return None

def clear_conversation_state(user_id: int):
    """Clear conversation state"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversation_state WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"🗑️  Cleared conversation state for user {user_id}")

def create_user(name: str, email: str = None, google_id: str = None, picture: Optional[str] = None, phone_number: str = None, balance: float = 12000) -> int:
    """Create a new user (supports Google OAuth or phone-only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, google_id, picture, phone_number, balance, pin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, google_id, picture, phone_number, balance, "1234"))  # Default balance: ₹12,000 for Google, ₹0 for phone-only
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    print(f"✅ Created new user: {name} (ID: {user_id}, Phone: {phone_number or 'N/A'}, Balance: ₹{balance:,.0f})")
    return user_id

def create_phone_user(name: str, phone_number: str) -> int:
    """Create a new user with phone number only (starts with ₹0)"""
    return create_user(name=name, phone_number=phone_number, balance=0)

def update_user_info(user_id: int, name: str, picture: Optional[str] = None):
    """Update user information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if picture:
        cursor.execute("UPDATE users SET name = ?, picture = ? WHERE id = ?", (name, picture, user_id))
    else:
        cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
    conn.commit()
    conn.close()

def get_user_by_google_id(google_id: str) -> Optional[Dict]:
    """Get user by Google ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user_from_google(email: str, name: str, google_id: str, picture: str) -> int:
    """Create a new user from Google OAuth"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, balance, google_id, picture)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, 10000, google_id, picture))  # Start with ₹10,000 balance
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def update_user_google_info(user_id: int, google_id: str, picture: str):
    """Update user's Google info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET google_id = ?, picture = ? WHERE id = ?
    """, (google_id, picture, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> float:
    """Get user balance"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['balance'] if result else 0

def update_user_balance(user_id: int, new_balance: float):
    """Update user balance"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_payment_transaction(sender_id: int, recipient_id: int, amount: float, 
                                sender_name: str, recipient_name: str):
    """Execute complete payment transaction atomically"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Start transaction
        conn.execute("BEGIN IMMEDIATE")
        
        # Update balances
        cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender_id))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, recipient_id))
        
        # Add transactions
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, description, recipient)
            VALUES (?, 'debit', ?, ?, ?)
        """, (sender_id, amount, f"Paid ₹{amount} to {recipient_name}", recipient_name))
        
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, description, recipient)
            VALUES (?, 'credit', ?, ?, ?)
        """, (recipient_id, amount, f"Received ₹{amount} from {sender_name}", sender_name))
        
        # Commit all changes atomically
        conn.commit()
        
        # Get updated balances
        cursor.execute("SELECT balance FROM users WHERE id = ?", (sender_id,))
        new_sender_balance = cursor.fetchone()['balance']
        
        return {"success": True, "new_balance": new_sender_balance}
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def verify_user_pin(user_id: int, pin: str) -> bool:
    """Verify user PIN"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pin FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result['pin'] == pin

# Transaction operations
def get_user_transactions(user_id: int, limit: int = 10) -> List[Dict]:
    """Get user transactions with formatted dates and recipient display logic"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (user_id, limit))
    
    transactions = []
    # Cache recipient lookups to avoid N+1 queries
    recipient_cache = {}
    
    for row in cursor.fetchall():
        txn = dict(row)
        # Format date for display
        txn['date'] = datetime.fromisoformat(txn['timestamp']).strftime("%b %d, %Y %I:%M %p")
        
        # Enhanced recipient display: show phone number if account not linked
        if txn['recipient']:
            # Check cache first to avoid repeated lookups
            if txn['recipient'] not in recipient_cache:
                # Try to find recipient by name (only once per unique recipient)
                recipient_user = get_user_by_name(txn['recipient'])
                recipient_cache[txn['recipient']] = recipient_user
            else:
                recipient_user = recipient_cache[txn['recipient']]
            
            if recipient_user:
                # Linked account - show username
                txn['recipient_display'] = recipient_user['name']
            else:
                # Check if recipient is a phone number format
                clean_recipient = ''.join(filter(str.isdigit, txn['recipient']))
                if len(clean_recipient) == 10:
                    # Display as phone number
                    txn['recipient_display'] = clean_recipient
                else:
                    # Display as-is (name without linked account)
                    txn['recipient_display'] = txn['recipient']
        
        transactions.append(txn)
    
    conn.close()
    return transactions

def add_transaction(user_id: int, txn_type: str, amount: float, description: str, recipient: Optional[str] = None):
    """Add a transaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, type, amount, description, recipient, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, txn_type, amount, description, recipient, datetime.now().isoformat()))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    return transaction_id

# Investment operations
def get_user_investments(user_id: int) -> Dict:
    """Get user investments summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type, amount FROM investments WHERE user_id = ?", (user_id,))
    
    investments = {}
    total = 0
    for row in cursor.fetchall():
        investments[row['type']] = row['amount']
        total += row['amount']
    
    investments['total'] = total
    conn.close()
    
    # Return default if no investments
    return investments if investments else {"gold": 0, "total": 0}

def update_user_investment(user_id: int, investment_type: str, amount: float):
    """Update user investment (adds to existing amount)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if investment exists
    cursor.execute("SELECT amount FROM investments WHERE user_id = ? AND type = ?", 
                  (user_id, investment_type))
    existing = cursor.fetchone()
    
    if existing:
        new_amount = existing['amount'] + amount
        cursor.execute(
            "UPDATE investments SET amount = ? WHERE user_id = ? AND type = ?",
            (new_amount, user_id, investment_type)
        )
    else:
        cursor.execute(
            "INSERT INTO investments (user_id, type, amount) VALUES (?, ?, ?)",
            (user_id, investment_type, amount)
        )
    
    conn.commit()
    conn.close()

# Initialize database on module import
init_database()

