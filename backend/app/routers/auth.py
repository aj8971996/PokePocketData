# app/routers/auth.py
import sys
from pathlib import Path
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent

# Get the project root directory (three levels up from current file)
project_root = current_dir.parent.parent

# Add paths to Python path
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt

from app.database import get_db, User
from app.models.pydantic_models import UserCreate, UserResponse, TokenResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")  #This will be set if the project ever moves to a production enviornment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/google/callback", response_model=TokenResponse)
async def google_auth_callback(token: str, db: Session = Depends(get_db)):
    try:
        logger.info("Processing Google authentication callback")
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.warning("Invalid token issuer")
            raise ValueError('Wrong issuer.')
        
        # Get or create user
        user = db.query(User).filter(User.google_id == idinfo['sub']).first()
        if not user:
            logger.info("Creating new user")
            user = User(
                email=idinfo['email'],
                full_name=idinfo['name'],
                picture=idinfo.get('picture'),
                google_id=idinfo['sub']
            )
            db.add(user)
        else:
            logger.info("Existing user found")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.user_id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info("Authentication successful")
        return TokenResponse(access_token=access_token)
    
    except ValueError as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )