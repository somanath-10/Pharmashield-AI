from datetime import timedelta
from typing import Annotated
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.domain import User, RoleEnum
from app.schemas.token import Token

router = APIRouter()
settings = get_settings()

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum

@router.post("/register", response_model=Token)
async def register(req: RegisterRequest) -> Token:
    existing = await User.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        name=req.name,
        email=req.email,
        role=req.role,
        hashed_password=get_password_hash(req.password)
    )
    await user.insert()
    
    access_token = create_access_token(
        subject=user.user_id, role=user.role.value
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    # Find user by email (as the username field)
    user = await User.find_one({"email": form_data.username})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    access_token = create_access_token(
        subject=user.user_id, role=user.role.value
    )
    return Token(access_token=access_token, token_type="bearer")
