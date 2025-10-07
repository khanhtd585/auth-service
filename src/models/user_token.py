from sqlalchemy import Column, String, DateTime, Enum, Text
import uuid
from db.database import Base

    
class UserToken(Base):
    __tablename__ = 'user_tokens'
    class Status:
        ACCESS = 'access'
        REFRESH = 'refresh'
        CONFIRM = 'confirm'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid1()))
    user_id = Column(String(36))
    token =  Column(Text)
    token_type =  Column(
        Enum('access', 'refresh', 'confirm'), 
        nullable=False, 
    )
    created_at = Column(DateTime(timezone=True), nullable=False)
    expire_at = Column(DateTime(timezone=True), nullable=False)
