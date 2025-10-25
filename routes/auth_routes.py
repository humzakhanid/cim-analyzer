from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User  
import auth
import logging
import os
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request bodies
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

MAILBOXLAYER_API_KEY = os.getenv("MAILBOXLAYER_API_KEY")

def is_real_email(email):
    # Temporarily disable email validation for testing
    return True
    # url = f"http://apilayer.net/api/check?access_key={MAILBOXLAYER_API_KEY}&email={email}"
    # try:
    #     response = requests.get(url, timeout=5)
    #     data = response.json()
    #     print("MailboxLayer response:", data)
    #     # Only check format validity for now
    #     return data.get("format_valid", False)
    # except Exception as e:
    #     print("MailboxLayer error:", e)
    #     return False

# Register route
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    print(f"Registration attempt for email: {request.email}")

    existing_user = db.query(User).filter(User.email == request.email).first()
    print(f"Existing user found: {existing_user is not None}")

    if existing_user:
        print("Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    if not is_real_email(request.email):
        print("Email is not real or deliverable")
        raise HTTPException(status_code=400, detail="Please enter a real, deliverable email address.")

    hashed_pw = auth.hash_password(request.password)
    new_user = User(email=request.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

# Login route
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {request.email}")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        logger.warning(f"User not found: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not auth.verify_password(request.password, user.hashed_password):
        logger.warning(f"Invalid password for user: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": user.email})
    logger.info(f"User logged in successfully: {request.email}")
    return {"access_token": token, "token_type": "bearer"}
