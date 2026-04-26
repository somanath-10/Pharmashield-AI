from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.domain import User, RoleEnum
from app.schemas.token import Token

router = APIRouter()
settings = get_settings()

@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    For MVP, username can be an email or a mock username. We will create a user if not exists for easy testing.
    """
    user = await User.find_one(User.email == form_data.username)
    if not user:
        # Auto-provision user for MVP testing if not exists
        role = RoleEnum.PATIENT
        if "admin" in form_data.username:
            role = RoleEnum.ADMIN
        elif "doctor" in form_data.username:
            role = RoleEnum.DOCTOR
        elif "pharmacist" in form_data.username:
            role = RoleEnum.PHARMACIST
            
        user = User(
            name=form_data.username.split("@")[0],
            email=form_data.username,
            role=role
        )
        await user.insert()
        
    access_token = create_access_token(
        subject=user.user_id, role=user.role.value
    )
    return Token(access_token=access_token, token_type="bearer")
