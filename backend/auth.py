"""
Authentication module for VoicePay
Handles Google OAuth and JWT tokens
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
import database as db

# Load environment variables from parent directory
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Debug: Check if GOOGLE_CLIENT_ID is loaded
if not GOOGLE_CLIENT_ID:
    print("⚠️  WARNING: GOOGLE_CLIENT_ID not found in .env file!")
    print("   Google OAuth will not work. Set GOOGLE_CLIENT_ID in backend/.env")
else:
    print(f"✅ GOOGLE_CLIENT_ID loaded: {GOOGLE_CLIENT_ID[:20]}...")

# Security scheme
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def verify_google_token(token: str) -> dict:
    """Verify Google OAuth token and return user info"""
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Token is valid, return user info
        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "google_id": idinfo.get("sub")
        }
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )

def get_or_create_user_from_google(google_user_info: dict) -> dict:
    """Get existing user or create new user from Google OAuth info"""
    email = google_user_info["email"]
    
    # Check if user exists by email
    user = db.get_user_by_email(email)
    
    if user:
        # Update user info if needed
        if user.get("name") != google_user_info["name"]:
            db.update_user_info(user["id"], google_user_info["name"], google_user_info.get("picture"))
        return user
    
    # Create new user
    name = google_user_info["name"]
    picture = google_user_info.get("picture")
    google_id = google_user_info["google_id"]
    
    user_id = db.create_user(
        name=name,
        email=email,
        google_id=google_id,
        picture=picture
    )
    
    return db.get_user_by_id(user_id)
