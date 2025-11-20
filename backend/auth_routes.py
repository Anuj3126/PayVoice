"""
Authentication routes for VoicePay
Google OAuth and JWT token management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth import (
    verify_google_token, 
    get_or_create_user_from_google, 
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class GoogleAuthRequest(BaseModel):
    token: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google OAuth token
    
    Process:
    1. Client sends Google ID token
    2. Server verifies token with Google
    3. Get or create user in database  
    4. Return JWT token for API access
    """
    try:
        # Verify Google token and get user info
        google_user_info = verify_google_token(request.token)
        
        # Get or create user in database
        user = get_or_create_user_from_google(google_user_info)
        
        # Create JWT token for our API
        access_token = create_access_token(data={"sub": str(user["id"])})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user.get("email"),
                "picture": user.get("picture"),
                "balance": user["balance"]
            }
        }
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user.get("email"),
        "picture": current_user.get("picture"),
        "balance": current_user["balance"],
        "transactions_count": len(current_user.get("transactions", [])) if "transactions" in current_user else 0
    }

@router.post("/logout")
async def logout():
    """
    Logout user
    Note: Since we're using JWT tokens, actual logout is handled client-side
    by removing the token. This endpoint is here for completeness.
    """
    return {"message": "Logged out successfully"}

