from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import UserCreate, UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.db.database import get_db
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create new user
    password_hash = AuthService.hash_password(user_data.password)
    user = {
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": password_hash,
        "skills": [],
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user)
    user_id = str(result.inserted_id)
    
    # Generate token
    token = AuthService.create_access_token(user_id)
    
    return TokenResponse(
        accessToken=token,
        user={
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "skills": []
        }
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db=Depends(get_db)):
    """Login user."""
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not AuthService.verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_id = str(user["_id"])
    token = AuthService.create_access_token(user_id)
    
    return TokenResponse(
        accessToken=token,
        user={
            "id": user_id,
            "email": user["email"],
            "name": user["name"],
            "skills": user.get("skills", [])
        }
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    """Refresh authentication token."""
    user_id = AuthService.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    token = AuthService.create_access_token(user_id)
    
    return TokenResponse(
        accessToken=token,
        user={
            "id": user_id,
            "email": user["email"],
            "name": user["name"],
            "skills": user.get("skills", [])
        }
    )

from datetime import datetime
