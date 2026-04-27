from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import get_settings
from app.schemas.token import TokenPayload
from app.models.domain import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await User.find_one(User.user_id == token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    # In a real app we might check if user is active here
    return current_user

def require_role(role: str):
    async def role_checker(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker

get_current_patient = require_role("PATIENT")
get_current_pharmacist = require_role("PHARMACIST")
get_current_doctor = require_role("DOCTOR")
get_current_admin = require_role("ADMIN")
