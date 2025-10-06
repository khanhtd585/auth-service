from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

from . import UserRead

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    
class RegisterReponse(UserRead):
    confirm_token: str
    
class RefreshTokenResponse(BaseModel):
    confirm_token: str

class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"
    confirm = "confirm"
    
class UserTokenBase(BaseModel):
    user_id: Optional[str]
    token_type: Optional[TokenType]
    token: Optional[str]
    created_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None