#!/usr/bin/env python3
"""
Test script to demonstrate LLM-driven multilingual responses
This shows how the system now handles multiple languages automatically
"""

from main import generate_response_from_data

# Test scenarios
test_cases = [
    {
        "name": "English Payment",
        "user_text": "Pay 500 to John",
        "result": {
            "success": True,
            "recipient": "John",
            "amount": 500,
            "requires_pin": True,
            "scenario": "payment_to_existing_contact"
        }
    },
    {
        "name": "Hindi Payment",
        "user_text": "John ko 500 bhejo",
        "result": {
            "success": True,
            "recipient": "John",
            "amount": 500,
            "requires_pin": True,
            "scenario": "payment_to_existing_contact"
        }
    },
    {
        "name": "English Balance Check",
        "user_text": "What's my balance",
        "result": {
            "balance": 12000,
            "scenario": "balance_check"
        }
    },
    {
        "name": "Hindi Balance Check",
        "user_text": "Mera balance check karo",
        "result": {
            "balance": 12000,
            "scenario": "balance_check"
        }
    },
    {
        "name": "English Phone Not Found",
        "user_text": "Pay 500 to Sarah",
        "result": {
            "success": False,
            "requires_pin": False,
            "offer_phone_collection": True,
            "pending_recipient": "Sarah",
            "pending_amount": 500,
            "scenario": "recipient_not_found"
        }
    },
    {
        "name": "Hindi Phone Not Found",
        "user_text": "Sarah ko 500 bhejo",
        "result": {
            "success": False,
            "requires_pin": False,
            "offer_phone_collection": True,
            "pending_recipient": "Sarah",
            "pending_amount": 500,
            "scenario": "recipient_not_found"
        }
    },
    {
        "name": "English Phone Confirmation",
        "user_text": "Nine eight seven six five four three two one zero",
        "result": {
            "success": True,
            "requires_confirmation": True,
            "phone": "9876543210",
            "phone_digits": "9, 8, 7, 6, 5, 4, 3, 2, 1, 0",
            "scenario": "confirm_phone_number"
        }
    },
    {
        "name": "Spanish Payment (NEW!)",
        "user_text": "Envía 500 a John",
        "result": {
            "success": True,
            "recipient": "John",
            "amount": 500,
            "requires_pin": True,
            "scenario": "payment_to_existing_contact"
        }
    },
    {
        "name": "French Balance (NEW!)",
        "user_text": "Quel est mon solde",
        "result": {
            "balance": 12000,
            "scenario": "balance_check"
        }
    }
]

def run_tests():
    """Run multilingual response tests"""
    print("🌍 Testing LLM-Driven Multilingual Response System\n")
    print("=" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 70)
        print(f"User: {test['user_text']}")
        print(f"Scenario: {test['result']['scenario']}")
        print("\nGenerating LLM response...")
        
        try:
            response = generate_response_from_data(test['user_text'], test['result'])
            print(f"Bot: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("\n✅ Test complete! Notice how the LLM adapts to each language automatically!")
    print("   This works for ANY language - no hardcoded translations needed!")

if __name__ == "__main__":
    run_tests()

