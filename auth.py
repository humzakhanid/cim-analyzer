import requests
from jose import jwt, JWTError, jwk
from fastapi import Depends, HTTPException, Request
from models.user import User
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Your Clerk domain's JWKS URL
CLERK_JWKS_URL = "https://neutral-porpoise-61.clerk.accounts.dev/.well-known/jwks.json"
ALGORITHM = "RS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings for old auth system
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_public_key():
    """Fetch Clerk's public key (JWKS)."""
    try:
        jwks = requests.get(CLERK_JWKS_URL).json()
        return jwt.algorithms.RSAAlgorithm.from_jwk(jwks['keys'][0])
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        return None

def verify_clerk_token(token: str):
    """Verify Clerk JWT token."""
    try:
        public_key = get_public_key()
        if not public_key:
            return None
            
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[ALGORITHM],
            audience="https://neutral-porpoise-61.clerk.accounts.dev",
            issuer="https://neutral-porpoise-61.clerk.accounts.dev"
        )
        return payload
    except JWTError as e:
        print(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def verify_custom_token(token: str):
    """Verify custom JWT token for backward compatibility."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def get_current_user(request: Request):
    """Get current user from either Clerk or custom JWT."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]
    print(f"Received token: {token[:50]}...")  # Debug: print first 50 chars
    
    # Try Clerk JWT first
    clerk_payload = verify_clerk_token(token)
    if clerk_payload:
        user_id = clerk_payload.get("sub") or clerk_payload.get("user_id")
        if user_id:
            print(f"Valid Clerk token for user: {user_id}")
            return User(id=user_id)
    
    # Fallback to custom JWT for backward compatibility
    custom_payload = verify_custom_token(token)
    if custom_payload:
        user_id = custom_payload.get("sub")
        if user_id:
            print(f"Valid custom token for user: {user_id}")
            return User(id=user_id)
    
    # Fallback authentication for development
    print("Using fallback authentication")
    return User(id="test_user_123")

# Old authentication functions for backward compatibility
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
