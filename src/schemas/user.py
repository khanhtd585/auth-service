from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


# Enum cho status
class UserStatus(str, Enum):
    active = "active"
    disabled = "disabled"
    banned = "banned"
    pending = "pending"


# Base model (common)
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    user_name: Optional[str] = None
    status: UserStatus = UserStatus.pending


# Model khi đọc từ DB hoặc trả về response
class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True   # cho phép convert từ SQLAlchemy object
        json_schema_extra = {
            "example": {
                "id": str(uuid.uuid4()),
                "email": "user@example.com",
                "user_name": "user name",
                "status": "active",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-05T12:00:00Z",
                "last_login_at": "2025-01-10T08:30:00Z",
            }
        }


# Model khi tạo mới user (request body)
class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str


# Model khi update user
class UserUpdate(BaseModel):
    id: str
    status: Optional[UserStatus] = None
    last_login_at: Optional[datetime] = None
