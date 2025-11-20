"""
VoicePay v2 - AI-Powered Voice Payment System
FastAPI backend with Groq LLM integration (blazingly fast!)
"""
import os
from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import random
import json
from groq import Groq
from dotenv import load_dotenv
import tempfile
# Audio preprocessing removed - focusing on Hindi & English transcription only

# Import local modules
import database as db
import investment_analyzer as ia
import investment_portfolio as portfolio
from auth_routes import router as auth_router
import auth

# Load environment variables from parent directory
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="VoicePay API v2",
    description="AI-Powered Voice Payment System with Groq LLM and Google OAuth",
    version="2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Groq (super fast LLM inference!)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise ValueError(
        "❌ GROQ_API_KEY is required!\n"
        "   Set GROQ_API_KEY environment variable.\n"
        "   Get your key from: https://console.groq.com/keys\n"
        "   Groq is 10-20x faster than OpenAI!"
    )

# Fix SSL certificate verification for Python 3.13 on macOS
import httpx
import certifi
import ssl

# TEMPORARY FIX: Disable SSL verification for development only
# This is a workaround for Python 3.13 SSL issues on macOS
# TODO: Re-enable SSL verification for production
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

http_client = httpx.Client(
    verify=False,  # Temporarily disable SSL verification
    timeout=30.0
)

client = Groq(
    api_key=GROQ_API_KEY,
    http_client=http_client
)
print("✅ Groq LLM initialized successfully! (Blazingly fast! ⚡)")
print("⚠️  SSL verification disabled (development mode only)")

# Groq also provides Whisper transcription - FREE!
# We'll use the same Groq client for both LLM and transcription
print("✅ Groq Whisper initialized for speech transcription! (FREE!)")

# Include authentication routes
app.include_router(auth_router)

# Pydantic Models
class VoiceCommand(BaseModel):
    text: str
    language: Optional[str] = "en"
    user_id: Optional[int] = 1

class PaymentRequest(BaseModel):
    recipient: str
    amount: float
    pin: str
    user_id: int

class InvestmentRequest(BaseModel):
    amount: float
    type: str = "gold"
    user_id: int

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    intent: Optional[str] = None

# Tool Functions (that the agent can call)
def get_transaction_history(user_id: int, limit: int = 10):
    """Get user's transaction history and spending"""
    transactions = db.get_user_transactions(user_id, limit)
    
    if not transactions:
        return {
            "transactions": [],
            "total_spent": 0,
            "scenario": "no_transactions"
        }
    
    # Calculate total spending (only count money SENT = 'debit')
    total_spent = sum(
        txn['amount'] 
        for txn in transactions 
        if txn['type'] == 'debit'  # Only count money sent, not received
    )
    
    return {
        "transactions": transactions,
        "total_spent": total_spent,
        "count": len(transactions),
        "scenario": "transaction_history"
    }

def detect_hindi(text: str) -> bool:
    """Detect if text contains Hindi/Hinglish keywords"""
    hindi_keywords = ['ko', 'bhejo', 'bhej', 'karo', 'kar', 'mera', 'aapka', 'kitna', 'hai', 'ka', 'ki', 'ke']
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in hindi_keywords)

def detect_language(text: str) -> str:
    """Detect the primary language of user's text"""
    text_lower = text.lower()
    
    # Hindi/Hinglish indicators
    hindi_keywords = ['ko', 'bhejo', 'bhej', 'karo', 'kar', 'mera', 'aapka', 'kitna', 'hai', 'ka', 'ki', 'ke', 'ka', 'se', 'me', 'par', 'pe']
    
    # Check for Hindi words
    hindi_count = sum(1 for word in hindi_keywords if word in text_lower)
    
    # If 2+ Hindi words found, it's Hindi/Hinglish
    if hindi_count >= 2:
        return "Hindi/Hinglish"
    
    # Otherwise, default to English
    return "English"

def transliterate_devanagari_to_roman(text: str) -> str:
    """
    Convert Devanagari script to Roman/English script for database lookup
    Each consonant in Hindi has an inherent 'a' sound unless followed by a virama (्)
    """
    # Devanagari to Roman mapping
    devanagari_to_roman = {
        # Vowels (independent)
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
        'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
        
        # Consonants (each has inherent 'a')
        'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
        'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
        'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
        'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
        'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
        'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'w': 'wa',
        'श': 'sha', 'ष': 'sha', 'स': 'sa', 'ह': 'ha',
        
        # Vowel signs (matras) - these modify the inherent 'a'
        'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
        'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
        '्': '', # Virama (removes the inherent 'a')
        
        # Special characters
        'ं': 'm', 'ः': 'h', 'ँ': 'n',
    }
    
    result = []
    chars = list(text)
    i = 0
    
    while i < len(chars):
        char = chars[i]
        
        if char in devanagari_to_roman:
            # Check if it's a consonant
            is_consonant = char in 'कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह'
            
            if is_consonant:
                # Add consonant with inherent 'a'
                base = devanagari_to_roman[char]
                result.append(base)
                
                # Check next character for vowel sign or virama
                if i + 1 < len(chars):
                    next_char = chars[i + 1]
                    if next_char == '्':  # Virama - remove inherent 'a'
                        result[-1] = base[:-1]  # Remove the 'a'
                        i += 1  # Skip virama
                    elif next_char in 'ािीुूृेैोौ':  # Vowel sign - modify inherent 'a'
                        result[-1] = base[:-1]  # Remove inherent 'a'
                        result.append(devanagari_to_roman[next_char])
                        i += 1  # Skip vowel sign
            else:
                result.append(devanagari_to_roman[char])
        else:
            result.append(char)  # Keep non-Devanagari characters as is
        
        i += 1
    
    return ''.join(result)

def generate_response_from_data(result: Dict, scenario: str = "general", language: str = "en") -> str:
    """
    Generate natural language response from function call result
    Uses LLM for context-aware response generation with language support
    """
    
    # Use provided language (already detected by frontend)
    if language == "hi":
        detected_language = "Hindi (Devanagari script)"
        language_name = "हिन्दी"
    else:
        detected_language = "English"
        language_name = "English"
    
    # Get user text from result if available (for context)
    user_text = result.get('user_text', '')
    
    # Build context for LLM based on scenario
    scenario_contexts = {
        # Payment scenarios
        "payment_to_existing_contact": f"User wants to pay {result.get('amount')} rupees to {result.get('recipient')}. They need to enter their PIN.",
        "payment_to_existing_phone": f"User wants to pay {result.get('amount')} rupees to phone number {result.get('recipient_phone')} ({result.get('recipient')}). They need to enter their PIN.",
        "payment_to_new_phone": f"A new account was automatically created for phone {result.get('recipient_phone')}. User wants to pay {result.get('amount')} rupees. They need to enter their PIN.",
        "payment_to_self": "User tried to send money to themselves, which is not allowed.",
        "incomplete_phone_number": f"User provided incomplete phone number: {result.get('incomplete_phone')} ({len(result.get('incomplete_phone', ''))} digits). Phone numbers must be exactly 10 digits. Tell them they provided {len(result.get('incomplete_phone', ''))} digits so far. Ask them to either: 1) Say the complete 10-digit number again, OR 2) Say just the remaining {10 - len(result.get('incomplete_phone', ''))} digits.",
        "recipient_not_found": f"Recipient '{result.get('pending_recipient')}' was not found. Ask if they want to add a phone number for this contact.",
        
        # Phone collection scenarios
        "prompt_for_phone_digits": "User agreed to add phone number. Ask them to say the 10-digit phone number.",
        "invalid_phone_number": f"Invalid phone number. Only {result.get('digits_received', 0)} digits received. Ask them to say all 10 digits clearly.",
        "confirm_phone_number": f"Phone number received: {result.get('phone_digits')}. Ask them to confirm if this is correct.",
        "phone_rejected_retry": "User said the phone number was incorrect. Ask them to say the phone number again.",
        "phone_confirmed_ready_for_pin": f"Phone number confirmed. {'Account found for ' + (result.get('recipient') or 'recipient') if result.get('account_exists') else 'New account created for ' + (result.get('recipient') or 'recipient')}. Ready to transfer {result.get('amount', 0)} rupees. Ask for PIN.",
        "no_pending_phone_request": "There's no pending phone number request. User should start again.",
        "no_phone_to_confirm": "There's no phone number to confirm. User should start again.",
        
        # User info scenario
        "user_info": f"User's name is {result.get('name', 'unknown')}. Email: {result.get('email', 'not set')}. Phone: {result.get('phone', 'not set')}.",
        "user_not_found": "User information not found.",
        
        # Balance scenario
        "balance_check": f"User's current balance is {result.get('balance', 0):,.0f} rupees.",
        
        # Transaction history scenarios
        "no_transactions": "User has no transactions yet.",
        "transaction_history": f"User has {result.get('count', 0)} transactions. Total spending is {result.get('total_spent', 0):,.0f} rupees.",
        
        # Investment scenarios
        "investment_query": f"User's investment portfolio: Total invested = {result.get('portfolio', {}).get('total_invested', 0):,.0f} rupees, Current value = {result.get('portfolio', {}).get('current_value', 0):,.0f} rupees, Total gains = {result.get('portfolio', {}).get('total_return', 0):,.0f} rupees ({result.get('portfolio', {}).get('return_percentage', 0):.1f}% return). Tell them ALL these numbers.",
        "no_investments": "User has not made any investments yet.",
        "investments_summary": f"User's investments: {result.get('investments')}. Total invested: {result.get('investments', {}).get('total', 0)} rupees.",
        
        # Account linking scenarios
        "accounts_linked": f"Found existing account and linked it with Google account. Combined balance is {result.get('new_balance', 0):,.0f} rupees.",
        "phone_saved": "Phone number saved successfully for the new user.",
        "invalid_phone_on_signup": "Invalid phone number during signup. Should be 10 digits.",
        "account_created_for_phone": f"Account created for phone {result.get('recipient_phone')}. Ready to send {result.get('amount')} rupees. Ask for PIN.",
        "no_pending_account_creation": "No pending account creation. User should start again.",
    }
    
    context_message = scenario_contexts.get(scenario, f"Unknown scenario: {scenario}. Data: {result}")
    
    # Language-specific instructions
    if language == "en":
        language_instruction = """CRITICAL: The user is speaking PURE ENGLISH. You MUST respond in PURE ENGLISH ONLY.
Do NOT use any Hindi, Hinglish, or mixed language. Use only English words.

Examples:
- "Please confirm payment of 500 rupees to John. Enter your PIN."
- "Your current balance is 12,000 rupees."
- "Would you like to add their phone number?"
"""
    else:  # language == "hi"
        language_instruction = """CRITICAL: The user is speaking HINDI (Devanagari script). You MUST respond in PURE HINDI using DEVANAGARI SCRIPT ONLY.
Do NOT use Roman/Latin script. Do NOT use English words. Use ONLY Hindi Devanagari characters (हिन्दी).

IMPORTANT: Write your entire response in Devanagari script like this:

Examples:
- "नीरज नामजोशी को 500 रुपये भेजने के लिए कृपया अपना पिन दर्ज करें।"
- "आपका बैलेंस ₹12,000 है।"
- "क्या आप उनका फोन नंबर जोड़ना चाहेंगे?"
- "मुझे नीरज नहीं मिले। क्या आप उनका फोन नंबर जोड़ना चाहते हैं?"

Remember: ONLY Devanagari script (हिन्दी), NO Roman/English letters!
"""
    
    # Generate response using LLM
    # Three tiers: ultra-short for basic, semi-short for investments, creative for rest
    is_ultra_short = scenario in ["payment_to_existing_contact", "payment_to_existing_phone", 
                                   "payment_to_new_phone", "balance_check", "user_info"]
    
    is_semi_short = scenario in ["investment_query", "no_investments"]
    
    if is_ultra_short:
        # Ultra-short responses for basic actions
        if language == "hi":
            system_msg = """Be EXTREMELY brief (1 short sentence).

For payments: "X को Y रुपये देने के लिए पिन डालें"
For balance: "आपका बैलेंस X रुपये है"
For user info: "आपका नाम X है"

Only Devanagari."""
        else:
            system_msg = """Be EXTREMELY brief (1 short sentence).

For payments: "Enter PIN to pay X rupees to Y"
For balance: "Your balance is X rupees"
For user info: "Your name is X"

English only."""
    
    elif is_semi_short:
        # Semi-short for investments - direct but include all numbers
        if language == "hi":
            system_msg = """Be direct and concise (2 sentences max).

For investments, ALWAYS say ALL 4 numbers:
"आपने X रुपये निवेश किए। अभी Y रुपये है। Z रुपये कमाए, यानी W% लाभ।"

Only Devanagari."""
        else:
            system_msg = """Be direct and concise (2 sentences max).

For investments, ALWAYS say ALL 4 numbers:
"You invested X rupees. Now worth Y rupees. You earned Z rupees, that's W% gain."

English only."""
    
    else:
        # Creative and natural for everything else
        if language == "hi":
            system_msg = """Be friendly and conversational. 
Use only हिन्दी Devanagari script."""
        else:
            system_msg = """Be friendly and conversational.
English only."""
    
    response_prompt = f"""{context_message}

{'Use only Devanagari (हिन्दी).' if language == 'hi' else 'English only.'}"""
    
    # Use Groq with SMARTER 70B model for more intelligent responses
    llm_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Much smarter 70B model!
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": response_prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )
    
    return llm_response.choices[0].message.content.strip()

def process_payment_intent(user_id: int, recipient: str, amount: float, user_text: str = ""):
    """Process payment intent and prepare for PIN confirmation"""
    
    # Check if recipient is a phone number (10 digits)
    clean_recipient = ''.join(filter(str.isdigit, recipient))
    
    # Check if it looks like a phone number (5+ digits indicates intent to use phone)
    if len(clean_recipient) >= 5 and len(clean_recipient) <= 11:
        # Validate it's exactly 10 digits (Indian phone number)
        if len(clean_recipient) != 10:
            # Save state for continuation
            save_state_with_language(user_id, 'awaiting_remaining_digits', {
                'partial_phone': clean_recipient,
                'amount': amount,
                'digits_needed': 10 - len(clean_recipient)
            })
            
            return {
                "success": False,
                "requires_pin": False,
                "incomplete_phone": clean_recipient,
                "digits_provided": len(clean_recipient),
                "digits_needed": 10 - len(clean_recipient),
                "pending_recipient": recipient,
                "pending_amount": amount,
                "scenario": "incomplete_phone_number"
            }
        
        # It's a complete 10-digit phone number - look it up
        recipient_user = db.get_user_by_phone(clean_recipient)
        
        if recipient_user and recipient_user['id'] != user_id:
            # Found user by phone number
            digits_list = list(clean_recipient)
            digits_spoken = ', '.join(digits_list)
            
            return {
                "success": True,
                "recipient": recipient_user['name'],
                "recipient_phone": clean_recipient,
                "amount": amount,
                "requires_pin": True,
                "scenario": "payment_to_existing_phone"
            }
        else:
            # Phone number not found or trying to pay self
            if recipient_user and recipient_user['id'] == user_id:
                return {
                    "success": False,
                    "requires_pin": False,
                    "scenario": "payment_to_self"
                }
            
            # Phone number doesn't exist - CREATE ACCOUNT AUTOMATICALLY
            digits_list = list(clean_recipient)
            digits_spoken = ', '.join(digits_list)
            
            # Create account with temporary name (will be updated when user signs up)
            new_user_id = db.create_phone_user(name=f"User {clean_recipient[-4:]}", phone_number=clean_recipient)
            new_user = db.get_user_by_id(new_user_id)
            
            return {
                "success": True,
                "recipient": new_user['name'],
                "recipient_id": new_user_id,
                "recipient_phone": clean_recipient,
                "amount": amount,
                "requires_pin": True,
                "auto_created": True,
                "scenario": "payment_to_new_phone"
            }
    
    # Not a phone number - try name lookup
    # First, try transliterating if it contains Devanagari script
    recipient_roman = transliterate_devanagari_to_roman(recipient)
    print(f"🔤 Transliterated '{recipient}' → '{recipient_roman}'")
    
    # Try both original and transliterated versions
    recipient_user = db.get_user_by_name(recipient)
    if not recipient_user and recipient_roman != recipient:
        print(f"🔍 Trying transliterated name: {recipient_roman}")
        recipient_user = db.get_user_by_name(recipient_roman)
    
    if not recipient_user or recipient_user['id'] == user_id:
        # Save conversation state for phone collection flow
        save_state_with_language(user_id, 'awaiting_phone_response', {
            'recipient_name': recipient,
            'amount': amount
        })
        
        return {
            "success": False,
            "requires_pin": False,
            "offer_phone_collection": True,
            "pending_recipient": recipient,
            "pending_amount": amount,
            "scenario": "recipient_not_found"
        }
    
    return {
        "success": True,
        "recipient": recipient_user['name'],
        "amount": amount,
        "requires_pin": True,
        "scenario": "payment_to_existing_contact"
    }

def user_agrees_to_add_phone(user_id: int):
    """User agreed to add phone number - prompt for digits"""
    # Check if we have a pending payment
    state = db.get_conversation_state(user_id)
    
    if not state or state['state'] != 'awaiting_phone_response':
        return {
            "success": False,
            "scenario": "no_pending_phone_request"
        }
    
    # Update state to awaiting phone digits
    context = state['context']
    save_state_with_language(user_id, 'awaiting_phone_digits', context)
    
    return {
        "success": True,
        "scenario": "prompt_for_phone_digits"
    }

def user_agrees_to_create_phone_account(user_id: int):
    """User agreed to create account for new phone number and send payment"""
    state = db.get_conversation_state(user_id)
    
    if not state or state['state'] != 'awaiting_phone_confirmation_for_new':
        return {
            "success": False,
            "scenario": "no_pending_account_creation"
        }
    
    context = state['context']
    phone = context['phone']
    amount = context['amount']
    
    # Create new account with phone number only (temporary name)
    new_user_id = db.create_phone_user(name=f"User_{phone}", phone_number=phone)
    recipient = db.get_user_by_id(new_user_id)
    
    # Clear state and require PIN
    db.clear_conversation_state(user_id)
    
    return {
        "success": True,
        "recipient": f"User_{phone}",
        "recipient_id": recipient['id'],
        "recipient_phone": phone,
        "amount": amount,
        "requires_pin": True,
        "scenario": "account_created_for_phone"
    }

def handle_phone_number_collection(user_id: int, phone_number: str, recipient_name: str = None, amount: float = None):
    """Handle phone number collection for new contacts"""
    # Check if we have context from conversation state
    state = db.get_conversation_state(user_id)
    if state and state['state'] == 'awaiting_phone_digits':
        context = state['context']
        recipient_name = context.get('recipient_name', recipient_name)
        amount = context.get('amount', amount)
    
    # Validate phone number (10 digits)
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    
    if len(clean_phone) != 10:
        return {
            "success": False,
            "requires_confirmation": False,
            "digits_received": len(clean_phone),
            "scenario": "invalid_phone_number"
        }
    
    # Create confirmation message with individual digits
    digits_list = list(clean_phone)
    digits_spoken = ', '.join(digits_list)
    
    # Save state for confirmation
    save_state_with_language(user_id, 'confirming_phone', {
        'phone': clean_phone,
        'recipient_name': recipient_name,
        'amount': amount
    })
    
    return {
        "success": True,
        "requires_confirmation": True,
        "phone": clean_phone,
        "phone_digits": digits_spoken,
        "scenario": "confirm_phone_number"
    }

def confirm_phone_and_transfer(user_id: int, confirmation: bool):
    """Confirm phone number and process payment"""
    state = db.get_conversation_state(user_id)
    
    if not state or state['state'] != 'confirming_phone':
        return {
            "success": False,
            "scenario": "no_phone_to_confirm"
        }
    
    if not confirmation:
        db.clear_conversation_state(user_id)
        return {
            "success": False,
            "scenario": "phone_rejected_retry"
        }
    
    # Phone confirmed, proceed with payment
    context = state['context']
    phone = context['phone']
    recipient_name = context['recipient_name']
    amount = context['amount']
    
    # Check if phone exists
    recipient = db.get_user_by_phone(phone)
    
    if recipient:
        # Account exists - proceed with payment
        recipient_display = recipient['name']
        account_exists = True
    else:
        # Create new account with phone number
        new_user_id = db.create_phone_user(name=recipient_name, phone_number=phone)
        recipient = db.get_user_by_id(new_user_id)
        recipient_display = f"{recipient_name} ({phone})"
        account_exists = False
    
    # Clear state and require PIN
    db.clear_conversation_state(user_id)
    
    return {
        "success": True,
        "recipient": recipient_display,
        "recipient_id": recipient['id'],
        "recipient_phone": phone,
        "amount": amount,
        "requires_pin": True,
        "account_exists": account_exists,
        "scenario": "phone_confirmed_ready_for_pin"
    }

def save_state_with_language(user_id: int, state: str, context: dict):
    """Helper to save conversation state while preserving language preference"""
    # Get existing state to preserve language
    existing_state = db.get_conversation_state(user_id)
    if existing_state and existing_state.get('context', {}).get('preferred_language'):
        # Preserve language preference
        context['preferred_language'] = existing_state['context']['preferred_language']
    
    db.save_conversation_state(user_id, state, context)

def check_and_link_phone_on_signup(user_id: int, phone_number: str):
    """Check if phone exists and link accounts on new Google signup"""
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    
    if len(clean_phone) != 10:
        return {
            "success": False,
            "scenario": "invalid_phone_on_signup"
        }
    
    # Check if phone already exists
    existing_user = db.get_user_by_phone(clean_phone)
    
    if existing_user and existing_user['id'] != user_id:
        # Get balances before linking
        current_user = db.get_user_by_id(user_id)
        combined_balance = current_user['balance'] + existing_user['balance']
        
        # Link accounts
        db.link_accounts(google_user_id=user_id, phone_user_id=existing_user['id'])
        
        # Update phone number on Google account
        db.update_user_phone(user_id, clean_phone)
        
        return {
            "success": True,
            "linked": True,
            "new_balance": combined_balance,
            "scenario": "accounts_linked"
        }
    else:
        # Just save phone number
        db.update_user_phone(user_id, clean_phone)
        
        return {
            "success": True,
            "linked": False,
            "scenario": "phone_saved"
        }

def get_user_info(user_id: int):
    """Get basic user information (name, email, phone)"""
    user = db.get_user_by_id(user_id)
    if not user:
        return {
            "success": False,
            "scenario": "user_not_found"
        }
    
    return {
        "success": True,
        "name": user.get('name'),
        "email": user.get('email'),
        "phone": user.get('phone'),
        "scenario": "user_info"
    }

def check_balance(user_id: int):
    """Check user's current balance"""
    balance = db.get_user_balance(user_id)
    return {
        "balance": balance,
        "scenario": "balance_check"
    }

def query_investments(user_id: int):
    """Query user's investment portfolio"""
    portfolio_data = portfolio.get_user_portfolio(user_id)
    
    return {
        "portfolio": portfolio_data,
        "scenario": "investment_query"
    }

def query_investments_db(user_id: int):
    """Query user's investments from database (legacy)"""
    investments = db.get_user_investments(user_id)
    
    if investments['total'] == 0:
        return {
            "investments": investments,
            "scenario": "no_investments"
        }
    
    return {
        "investments": investments,
        "scenario": "investments_summary"
    }

# Create AI Agent with tools
def create_payvoice_agent(text: str, user_id: int = 1, language: str = "en"):
    """
    Create PayVoice agent with proper tool definitions
    
    The agent handles:
    1. Payment intents: "send 500 to Rahul", "pay 1000 rupees to Priya"
    2. Balance queries: "what's my balance", "how much money do I have"
    3. Transaction history: "show my transactions", "what did I spend"
    4. Investment queries: "show my investments", "what's my portfolio"
    Currency handling:
    - Treat "R S", "RS", "rupees", "bucks", "dollars" as Indian Rupees (₹)
    - Extract only numeric amounts
    
    Language flexibility:
    - Support natural language, slang, regional terms
    - Handle mixed languages (English + Hindi)
    
    Output format:
    - Clear, natural spoken English for Text-to-Speech
    - No abbreviations
    - Human-like delivery
    """
    
    # SIMPLE LANGUAGE LOCKING: Once set, never switch automatically
    state = db.get_conversation_state(user_id)
    persisted_language = None
    
    if state and state.get('context'):
        persisted_language = state['context'].get('preferred_language')
    
    if persisted_language:
        # LOCKED: Use persisted language no matter what
        detected_language = persisted_language
        print(f"🔒 LOCKED to {persisted_language} - ALL responses will be in {persisted_language.upper()}")
    else:
        # First message - detect and LOCK language
        detected_language = language
        print(f"🆕 First message - LOCKING to {detected_language.upper()} for this conversation")
    
    print(f"💬 Processing: {text[:50]}... | Language: {detected_language}")
    
    # Define function declarations for OpenAI
    functions = [
        {
            "type": "function",
            "function": {
                "name": "get_transaction_history",
                "description": "Get user's spending/expense data, transaction history, or monthly spending. Use for: 'how much did I spend', 'monthly spending', 'show expenses', 'show transactions', 'spending history'. This calculates total money spent (debits).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of transactions to retrieve (default: 10)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "process_payment_intent",
                "description": "Process a payment or money transfer. Use for 'pay', 'send money', 'transfer'. Recipient can be a name OR a 10-digit phone number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Name of person OR 10-digit phone number (e.g., 'Anuj' or '9686270688')"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount in rupees"
                        }
                    },
                    "required": ["recipient", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_info",
                "description": "Get user's basic information (name, email, phone). Use for ENGLISH: 'what is my name', 'who am I', 'my profile', 'my details', 'my info'. Use for HINDI: 'मेरा नाम क्या है', 'मैं कौन हूं', 'मेरी जानकारी', 'मेरा profile'.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_balance",
                "description": "Check user's CURRENT WALLET BALANCE (money they have right now). Use for ENGLISH: 'what's my balance', 'how much money do I have', 'wallet balance', 'my balance'. Use for HINDI: 'मेरा balance', 'balance कितना है', 'मेरे पास कितने पैसे', 'wallet balance'. DO NOT use for: spending/expenses/investment queries (invest/निवेश/कमा).",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_investments",
                "description": "Get user's INVESTMENT DATA with GAINS/RETURNS (total invested, current value, gains/returns). DEFAULT FUNCTION FOR ALL INVESTMENT QUERIES. Use for ENGLISH: 'how much have I invested', 'what are my investments', 'show my portfolio', 'how much have I gained', 'how much have I earned', 'what are my returns', 'investment gains', 'portfolio value', 'investment performance'. Use for HINDI: 'कितना invest किया', 'कितना निवेश किया', 'कितना कमा सकता', 'कितना कमाया', 'कितना खमाया' (typo), 'मेरा portfolio', 'मेरी investments', 'returns क्या है', 'अभी तक कितना कमाया', 'कितना profit'. This ALWAYS returns: total_invested, current_value, total_return (gains in rupees), return_percentage.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_investments_db",
                "description": "DEPRECATED: Only for basic database totals. DO NOT USE THIS for gains/returns/earnings queries. For ANY investment query about gains, returns, or earnings, use query_investments instead.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "user_agrees_to_add_phone",
                "description": "Call this when user says YES to adding a phone number (yes, yeah, sure, ok, add it, etc.). This will prompt them for the 10-digit number.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "collect_phone_number",
                "description": "Collect and verify phone number when user speaks the 10 digits. Use when user provides phone number digits.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "10-digit phone number spoken by user"
                        }
                    },
                    "required": ["phone_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "confirm_phone_number",
                "description": "Confirm the phone number after user says yes or no. Use when verifying phone number digits.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "confirmation": {
                            "type": "boolean",
                            "description": "True if user confirmed (yes/correct/right), False if denied (no/wrong)"
                        }
                    },
                    "required": ["confirmation"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "save_phone_on_signup",
                "description": "Save phone number when new Google user signs up. Use when user provides phone number during onboarding.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "10-digit phone number"
                        }
                    },
                    "required": ["phone_number"]
                }
            }
        }
    ]
    
    # Create system prompt
    system_prompt = """You are a voice-enabled UPI payment assistant with phone-based contact creation.

LANGUAGE SUPPORT - CRITICAL:
- ALWAYS match the user's language in your response!
- If user uses Hindi words (like "bhejo", "karo", "mera", "ko") → respond COMPLETELY IN HINDI/HINGLISH
- If user uses only English → respond in English
- Detect language from keywords:
  * Hindi indicators: bhejo, karo, kitna, mera, aapka, hai, ko, ka, ki, ke
  * English indicators: pay, send, my, check, what, is
- When in doubt, use Hinglish (mix of Hindi and English)

EXAMPLES:
User: "Anuj ko 120 bhejo" → You: "Theek hai. Anuj ko 120 rupees bhejne ke liye apna PIN daaliye."
User: "Pay 120 to Anuj" → You: "Please confirm payment of 120 rupees to Anuj. Enter your PIN."
User: "Balance check karo" → You: "Aapka balance ₹12,000 hai."

Your task:
account for tts typo in names like niraj as neeraj ect.. this is important

IMPORTANT: DO NOT confuse general questions with phone number inputs!
- If user asks "what is my name?" → call get_user_info
- If user asks a simple question → try to answer with appropriate function
- ONLY call collect_phone_number when conversation state is "awaiting_phone_digits"

1. **Understand the user's intent** and call the correct function:
   - For user info queries (name, profile, who am I) → call **get_user_info**
   - For spending, expense, or monthly spending queries → call **get_transaction_history**
   - For sending or transferring money (to name OR phone number) → call **process_payment_intent**
   - For checking account balance → call **check_balance**
   - For ANY investment queries (invested amount, gains, returns, earnings, portfolio) → call **query_investments** (DEFAULT for all investment queries)
   - When user says YES to adding phone number → call **user_agrees_to_add_phone**
   - When user provides phone number digits → call **collect_phone_number**
   - When user confirms/denies phone number → call **confirm_phone_number**
   - When new user provides phone on signup → call **save_phone_on_signup**

2. **Phone number collection flow (IMPORTANT - FOLLOW EXACTLY):**
   
   **CRITICAL: When user says "pay X to NAME", remember X is the AMOUNT, not phone digits!**
   
   Step 1: Recipient not found → **process_payment_intent** returns offer
   → Message: "I couldn't find [name]. Would you like to add their phone number?"
   → Wait for user response
   → **REMEMBER THE ORIGINAL PAYMENT AMOUNT FROM STEP 1!**
   
   Step 2: User says YES (yes, yeah, sure, ok, add it, add the number, etc.)
   → Call **user_agrees_to_add_phone** (NO parameters needed)
   → This will respond: "Okay, please tell me the 10-digit phone number"
   → Wait for user to speak the digits
   → **DO NOT confuse phone digits with the payment amount!**
   
   Step 3: User speaks phone number (e.g., "seven three three eight two zero seven one two three")
   → Extract ONLY the 10-digit phone number: "7338207123"
   → **DO NOT use any of these digits as the payment amount!**
   → Call **collect_phone_number** with ONLY:
     * phone_number: "7338207123" (the 10 digits they just said)
   → System will respond with digit confirmation
   
   Step 4: System confirms digits (e.g., "7, 3, 3, 8, 2, 0, 7, 1, 2, 3")
   → User says YES/NO
   → Call **confirm_phone_number** with:
     * confirmation: true (for yes) or false (for no)
   
   Step 5: System creates account or links existing
   → Proceeds to payment PIN confirmation
   → **Uses the ORIGINAL amount from Step 1, NOT the phone digits!**

3. **Payment to unregistered phone number flow:**
   
   → System AUTOMATICALLY creates account with temporary name (e.g., "User 1234")
   → Proceeds directly to PIN confirmation
   → User enters PIN → payment completes to temporary account
   → Later when someone signs up with that phone number → accounts merge automatically
   → Money, transactions, and portfolio are transferred seamlessly

4. **Payment recipient handling:**
   - Users can pay to either a NAME or a PHONE NUMBER
   - If user says a 10-digit number → extract and pass as recipient
     Example: "Pay 331 to nine six eight six two seven zero six eight eight" → recipient: "9686270688"
   - If user says a name → pass the name as recipient
     Example: "Pay 500 to Anuj" → recipient: "Anuj"
   - System will automatically detect if it's a phone number and look up the account
   
4b. **Handling incomplete phone numbers (voice cutoff):**
   - If user's voice cuts off mid-phone-number, system detects partial digits
   - System saves state and asks for remaining digits
   - When user provides remaining digits, COMBINE with previous partial number
   - Example: User says "91080" (5 digits), system asks for 5 more
   - User says "12345", you combine to get "9108012345" and call process_payment_intent

5. **Currency handling:**
   - Treat all mentions like "R S", "RS", "rupees", "bucks", or "dollars" as **Indian Rupees (₹)**.
   - Extract only the numeric amount.  
     Example: "Send 500 R S" → 500; "Pay 1000 rupees" → 1000.

6. **Language flexibility:**
   - Be flexible with **natural language, slang, regional terms, or mixed languages**.
   - Understand "yes" variations: yes, yeah, sure, okay, ok, yep, correct, right
   - Understand "no" variations: no, nope, wrong, incorrect
   
7. **Output format:**
   - **CRITICAL**: Match the user's language! If they use Hindi words, respond in Hindi/Hinglish!
   - Respond in **clear, natural spoken language** (English, Hindi, or Hinglish) suitable for Text-to-Speech.
   - **Do not abbreviate** or shorten phrases unnaturally.  
   - Ensure the response sounds as if it's being spoken aloud to the user.
   - Common Hindi phrases to use when user speaks Hindi:
     * "Theek hai" or "Achha" (Okay)
     * "Aapka balance ₹X hai" (Your balance is ₹X)
     * "Payment successful ho gaya" or "Paisa pahunch gaya" (Payment successful)
     * "Apna PIN daaliye" (Enter your PIN)
     * "X rupees Y ko bhejne ke liye confirm karein" (Confirm sending X rupees to Y)
     * "Kitna invest karna hai?" (How much to invest?)
     * Natural Hindi/Hinglish mixing is encouraged for Indian users

Focus on accuracy, clarity, conversational flow, and a human-like spoken delivery."""
    
    # Check conversation state to provide context
    state = db.get_conversation_state(user_id)
    context_info = ""
    
    if state:
        if state['state'] == 'awaiting_remaining_digits':
            context = state.get('context', {})
            partial_phone = context.get('partial_phone', '')
            amount = context.get('amount', 0)
            digits_needed = context.get('digits_needed', 0)
            context_info = f"\n\nIMPORTANT CONTEXT: User started giving a phone number: {partial_phone} ({len(partial_phone)} digits). They need to provide {digits_needed} more digits to complete it. The payment amount is {amount} rupees. If user provides digits now, COMBINE them with the partial phone: {partial_phone}. Then call process_payment_intent with the COMPLETE 10-digit phone number as the recipient."
        elif state['state'] == 'awaiting_phone_digits':
            context = state.get('context', {})
            recipient = context.get('recipient_name', 'unknown')
            amount = context.get('amount', 0)
            context_info = f"\n\nIMPORTANT CONTEXT: User is currently providing a phone number for recipient '{recipient}' for a payment of {amount} rupees. If the user says digits or a number, treat it as the phone number and call collect_phone_number. HOWEVER, if user asks a GENERAL QUESTION (like 'what is my name', 'my balance', 'my investments'), answer that question with the appropriate function INSTEAD of treating it as phone digits."
        elif state['state'] == 'confirming_phone':
            context_info = f"\n\nIMPORTANT CONTEXT: User is confirming a phone number. If they say 'yes', 'yeah', 'correct', call confirm_phone_number with confirmation=true. If they say 'no', 'wrong', call confirm_phone_number with confirmation=false."
    
    # Call Groq with function calling (blazingly fast!)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Best Groq model for function calling
        messages=[
            {"role": "system", "content": system_prompt + context_info},
            {"role": "user", "content": f"The user said: '{text}'"}
        ],
        tools=functions,
        tool_choice="auto",
        temperature=0.5
    )
    
    # Check for function call
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"🤖 Agent called: {function_name}({function_args})")
        
        # Execute the function
        if function_name == "get_transaction_history":
            limit = function_args.get("limit", 100)  # Increased default from 10 to 100
            result = get_transaction_history(user_id, limit)
            intent = "history"
        
        elif function_name == "process_payment_intent":
            recipient = function_args.get("recipient", "").lower()
            amount = function_args.get("amount")
            result = process_payment_intent(user_id, recipient, amount, text)
            intent = "payment"
        
        elif function_name == "get_user_info":
            result = get_user_info(user_id)
            intent = "user_info"
        
        elif function_name == "check_balance":
            result = check_balance(user_id)
            intent = "balance"
        
        elif function_name == "query_investments":
            result = query_investments(user_id)
            intent = "investment"
        
        elif function_name == "query_investments_db":
            result = query_investments_db(user_id)
            intent = "investment"
        
        elif function_name == "user_agrees_to_add_phone":
            result = user_agrees_to_add_phone(user_id)
            intent = "phone_agree"
        
        elif function_name == "collect_phone_number":
            phone = function_args.get("phone_number")
            result = handle_phone_number_collection(user_id, phone)
            intent = "phone_collection"
        
        elif function_name == "confirm_phone_number":
            confirmation = function_args.get("confirmation")
            result = confirm_phone_and_transfer(user_id, confirmation)
            intent = "phone_confirmation"
        
        elif function_name == "save_phone_on_signup":
            phone = function_args.get("phone_number")
            result = check_and_link_phone_on_signup(user_id, phone)
            intent = "phone_signup"
        else:
            return {"intent": "unknown", "message": "I couldn't understand that command. Please try again."}
        
        # Update or create conversation state with language preference
        if state:
            # Update existing state with language
            context = state.get('context', {})
            context['preferred_language'] = detected_language
            db.save_conversation_state(user_id, state['state'], context)
        elif not persisted_language:
            # First message - create state with just language preference
            db.save_conversation_state(user_id, 'active', {'preferred_language': detected_language})
        
        # Generate LLM response based on structured data and user's language
        message = generate_response_from_data(result, result.get('scenario', 'general'), detected_language)
        return {"intent": intent, "data": result, "message": message}
    
    # No function call, use LLM's direct response
    assistant_message = response.choices[0].message.content
    if assistant_message:
        return {"intent": "direct", "message": assistant_message}
    
    return {"intent": "unknown", "message": "I couldn't understand that command. Please try again."}

# API Endpoints
@app.get("/")
def root():
    return {
        "message": "VoicePay API v2 is running",
        "version": "2.0",
        "ai_engine": "OpenAI GPT with Agent Pattern",
        "model": "gpt-4o-mini",
        "auth": "Google OAuth 2.0",
        "status": "ready"
    }

# ============ Authentication Endpoints ============

@app.get("/api/auth/google")
async def login_google(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = request.url_for('auth_callback')
    return await auth.oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/callback")
async def auth_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        token = await auth.oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Create or get user from Google info
        user = auth.create_or_get_user_from_google(user_info)
        
        # Create JWT token
        access_token = auth.create_access_token(
            data={"sub": user["id"], "email": user.get("email"), "name": user["name"]}
        )
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/auth/success?token={access_token}")
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/auth/error?message={str(e)}")

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(auth.get_current_user)):
    """Get current authenticated user"""
    return Response(
        success=True,
        message="User retrieved",
        data={
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user.get("email"),
            "picture": current_user.get("picture"),
            "balance": current_user["balance"]
        }
    )

@app.post("/api/auth/logout")
async def logout():
    """Logout user"""
    return Response(
        success=True,
        message="Logged out successfully"
    )

@app.get("/api/users")
def get_users():
    """Get all users"""
    users = db.get_all_users()
    return Response(
        success=True,
        message="Users retrieved",
        data={"users": users}
    )

@app.get("/api/user/{user_id}")
def get_user(user_id: int):
    """Get user data"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = db.get_user_transactions(user_id, 100)  # Increased from 10 to 100
    investments = db.get_user_investments(user_id)
    
    return Response(
        success=True,
        message="User data retrieved",
        data={
            "id": user['id'],
            "name": user['name'],
            "email": user.get('email'),
            "phone_number": user.get('phone_number'),
            "balance": user['balance'],
            "transactions": transactions,
            "investments": investments
        }
    )

@app.post("/api/user/{user_id}/phone")
def save_user_phone(user_id: int, request: dict):
    """Save user phone number and link accounts if exists"""
    phone_number = request.get('phone_number')
    
    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")
    
    # Validate phone number (10 digits)
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    if len(clean_phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be 10 digits")
    
    # Check if user exists
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if phone already exists with another user
    existing_user = db.get_user_by_phone(clean_phone)
    
    if existing_user and existing_user['id'] != user_id:
        # Link accounts
        combined_balance = user['balance'] + existing_user['balance']
        db.link_accounts(google_user_id=user_id, phone_user_id=existing_user['id'])
        db.update_user_phone(user_id, clean_phone)
        
        return Response(
            success=True,
            message=f"Phone number saved! Found and linked your existing account. Combined balance: ₹{combined_balance:,.0f}",
            data={
                "linked": True,
                "new_balance": combined_balance,
                "phone_number": clean_phone
            }
        )
    else:
        # Just save phone number
        db.update_user_phone(user_id, clean_phone)
        
        return Response(
            success=True,
            message="Phone number saved successfully!",
            data={
                "linked": False,
                "phone_number": clean_phone
            }
        )

@app.post("/api/process_voice")
async def process_voice(command: VoiceCommand, current_user: dict = Depends(auth.get_current_user)):
    """Process voice command using PayVoice AI Agent (requires authentication)"""
    try:
        # Use authenticated user's ID
        user_id = current_user["id"]
        language = command.language or 'en'
        print(f"🎤 Processing voice command: '{command.text}' (lang: {language}) for user {user_id}")
        result = create_payvoice_agent(command.text, user_id, language)
        
        return Response(
            success=True,
            message=result["message"],
            intent=result["intent"],
            data=result.get("data")
        )
    except Exception as e:
        # Print full error details for debugging
        import traceback
        error_msg = str(e)
        print(f"❌ Voice processing error: {error_msg}")
        print(traceback.format_exc())
        
        if "429" in error_msg or "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
            return Response(
                success=False,
                message="I'm experiencing high traffic. Please wait and try again.",
                intent="error"
            )
        return Response(
            success=False,
            message="I encountered an error. Please try again.",
            intent="error"
        )

@app.post("/api/payment")
async def make_payment(payment: PaymentRequest, current_user: dict = Depends(auth.get_current_user)):
    """Execute payment transaction (requires authentication)"""
    # Use authenticated user's ID
    user_id = current_user["id"]
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify PIN
    if not db.verify_user_pin(user_id, payment.pin):
        return Response(success=False, message="Incorrect PIN. Payment failed.")
    
    # Check recipient
    recipient = db.get_user_by_name(payment.recipient)
    if not recipient:
        return Response(success=False, message=f"Recipient {payment.recipient} not found.")
    
    # Check balance
    if user["balance"] < payment.amount:
        return Response(success=False, message="Insufficient balance. Payment failed.")
    
    # Execute transaction atomically (prevents database locking issues)
    try:
        result = db.execute_payment_transaction(
            sender_id=user["id"],
            recipient_id=recipient["id"],
            amount=payment.amount,
            sender_name=user["name"],
            recipient_name=recipient["name"]
        )
        new_sender_balance = result["new_balance"]
    except Exception as e:
        return Response(success=False, message=f"Payment failed: {str(e)}")
    
    # Generate investment nudge
    roundoff = 10 - (payment.amount % 10) if payment.amount % 10 != 0 else 10
    nudge = {
        "amount": roundoff,
        "message": f"Round off ₹{roundoff} and invest in gold!",
        "type": "gold"
    }
    
    return Response(
        success=True,
        message=f"Payment of ₹{payment.amount} to {recipient['name']} successful!",
        data={"new_balance": new_sender_balance, "nudge": nudge}
    )

@app.post("/api/invest")
async def invest(investment: InvestmentRequest):
    """Process investment"""
    # Get user from request (for backward compatibility with frontend)
    user_id = investment.user_id
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["balance"] < investment.amount:
        return Response(success=False, message="Insufficient balance for investment.")
    
    # Try to add to portfolio with market prices
    portfolio_added = portfolio.add_investment_to_portfolio(
        user_id, investment.type, investment.amount
    )
    
    if not portfolio_added:
        return Response(
            success=False,
            message="Investment failed. Market data unavailable. Please try again later."
        )
    
    # Execute investment
    new_balance = user["balance"] - investment.amount
    db.update_user_balance(user["id"], new_balance)
    db.update_user_investment(user["id"], investment.type, investment.amount)
    
    # Add transaction
    db.add_transaction(user["id"], "investment", investment.amount,
                      f"Invested ₹{investment.amount} in {investment.type}", None)
    
    investments = db.get_user_investments(user["id"])
    
    return Response(
        success=True,
        message=f"Successfully invested ₹{investment.amount} in {investment.type}!",
        data={
            "new_balance": new_balance,
            "total_investments": investments["total"],
            "investment_type": investment.type,
            "investment_amount": investment.amount
        }
    )

@app.get("/api/balance/{user_id}")
def get_balance(user_id: int):
    """Get current balance"""
    balance = db.get_user_balance(user_id)
    return Response(
        success=True,
        message=f"Your current balance is ₹{balance:,.0f}.",
        data={"balance": balance}
    )

@app.get("/api/transactions/{user_id}")
def get_transactions(user_id: int, limit: int = 10):
    """Get transaction history"""
    transactions = db.get_user_transactions(user_id, limit)
    return Response(
        success=True,
        message=f"Retrieved {len(transactions)} transactions",
        data={"transactions": transactions}
    )

@app.post("/api/clear-conversation/{user_id}")
def clear_conversation(user_id: int):
    """Clear conversation state (useful for switching languages or resetting context)"""
    db.clear_conversation_state(user_id)
    return Response(
        success=True,
        message="Conversation reset successfully. You can start fresh!",
        data={}
    )

@app.get("/api/portfolio/{user_id}")
def get_portfolio(user_id: int):
    """Get investment portfolio"""
    try:
        portfolio_data = portfolio.get_user_portfolio(user_id)
        summary_text = portfolio.get_investment_summary_text(user_id)
        
        return Response(
            success=True,
            message=summary_text,
            data={"portfolio": portfolio_data}
        )
    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        return Response(success=False, message="Failed to fetch portfolio data")

@app.get("/api/investment-analysis/{user_id}")
def get_investment_analysis(user_id: int):
    """Get investment analysis"""
    try:
        transactions = db.get_user_transactions(user_id, 100)
        
        # Count monthly transactions
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_txn_count = sum(
            1 for txn in transactions 
            if datetime.fromisoformat(txn['timestamp']).month == current_month 
            and datetime.fromisoformat(txn['timestamp']).year == current_year
            and txn['type'] in ['payment', 'debit']
        )
        
        # Check market data
        top_performer = ia.get_top_performer_week()
        if top_performer is None:
            return Response(success=False, message="Market data unavailable.", 
                          data={"show": False})
        
        if monthly_txn_count < 5:
            return Response(success=False, 
                          message=f"Need 5 transactions for analysis. You have {monthly_txn_count}.",
                          data={"show": False})
        
        recommendation = ia.get_investment_recommendation(user_id, transactions)
        
        if recommendation:
            return Response(success=True, message="Investment analysis ready", 
                          data=recommendation)
        else:
            return Response(success=False, message="Analysis failed.", 
                          data={"show": False})
    except Exception as e:
        print(f"Error in investment analysis: {e}")
        return Response(success=False, message="Analysis failed. Market data unavailable.",
                      data={"show": False})

@app.get("/api/top-performer")
def get_top_performer():
    """Get top performing investment"""
    try:
        top_performer = ia.get_top_performer_week()
        
        if top_performer is None:
            return Response(success=False, message="Market data unavailable.")
        
        ticker, name, weekly_return = top_performer
        
        return Response(
            success=True,
            message=f"{name} is the top performer this week",
            data={
                "ticker": ticker,
                "name": name,
                "weekly_return": round(weekly_return, 2),
                "description": f"Up {round(weekly_return, 2)}% this week"
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        return Response(success=False, message="Failed to fetch top performer.")

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio using Groq Whisper (FREE!)
    Supports Hindi and English with auto-detection
    """
    temp_audio_path = None
    
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Create temporary file with proper extension
        suffix = os.path.splitext(audio.filename)[1] or '.webm'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        try:
            # Transcribe using Groq Whisper - Auto-detect Hindi or English
            # Enhanced prompt with Hindi examples to improve recognition
            with open(temp_audio_path, 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                    response_format="verbose_json",
                    language=None,  # Auto-detect language
                    # Enhanced bilingual prompt with Hindi examples
                    prompt="Hindi examples: Niraj ko sau rupaye bhejo. Mera balance kitna hai. Anuj ko paanch sau rupaye bhejo. English examples: Send 100 rupees to Anuj. What is my balance. Pay 500 to Rahul. Common names: Niraj, Anuj, Rahul, Priya, Amit."
                )
            
            # Extract text and language
            transcribed_text = transcription.text if hasattr(transcription, 'text') else str(transcription)
            detected_lang = transcription.language if hasattr(transcription, 'language') else 'unknown'
            
            print(f"🎤 Transcribed: {transcribed_text}")
            print(f"🌍 Language: {detected_lang}")
            
            return {
                "success": True,
                "text": transcribed_text,
                "language": detected_lang
            }
            
        finally:
            # Clean up temp file
            if temp_audio_path:
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
                
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

# NOTE: Groq doesn't have TTS API - only Whisper (STT)
# TTS will be handled by browser's native speech synthesis

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Starting VoicePay v2...")
    print("📊 Initializing investment portfolio system...")
    
    try:
        portfolio.migrate_old_investments()
        print("✅ Investment portfolio ready!")
    except Exception as e:
        print(f"⚠️  Portfolio migration warning: {e}")
    
    print("✅ VoicePay API is ready!")
    print("🎯 Using Groq LLama 3.3 70B + Groq Whisper (All FREE!)")

if __name__ == "__main__":
    import uvicorn
    # Enable auto-reload in development (restarts server on file changes)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)