from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.sql import func
import uuid
from db.database import Base

class User(Base):
    __tablename__ = 'users'

    # Enum for user status
    class Status:
        ACTIVE = 'active'
        DISABLED = 'disabled'
        BANNED = 'banned'
        PENDING = 'pending'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=True)
    user_name = Column(String(255), nullable=True)
    password = Column(Text, nullable=False)
    status = Column(
        Enum('active', 'disabled', 'banned', 'pending'), 
        nullable=False, 
        default=Status.PENDING
    )
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
