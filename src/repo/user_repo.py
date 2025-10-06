from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Optional
import logging

from models import User
from schemas import UserCreate, UserRead, UserStatus, UserUpdate
from utils.datetime_utils import get_current_datetime

import uuid

logger = logging.getLogger(__name__)

class UserRepo:
    
    @staticmethod
    async def create(db: Session, user_in: UserCreate) -> User:
        new_user = User(
            id=str(uuid.uuid4()),
            user_name=user_in.user_name,
            email=user_in.email,
            password=user_in.password,
            status=UserStatus.pending,
            created_at=get_current_datetime(),
            updated_at=get_current_datetime(),
        )
        db.add(new_user)

        try:
            await db.flush()  # flush để bắt lỗi unique sớm
        except IntegrityError as e:
            await db.rollback()
            logger.error(f'Error: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User could not be created due to DB constraint",
            )
        return new_user
    
    @staticmethod
    async def get_by_id(db: Session, id: str) -> Optional[User]:
        stmt = select(User).where(User.id == id) 
        result = await db.execute(stmt) 
        user = result.scalar_one_or_none() 
        return user if user else None

    @staticmethod
    async def get_by_email(db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email) 
        result = await db.execute(stmt) 
        user = result.scalar_one_or_none() 
        return user if user else None

    @staticmethod
    async def update(db, id: str, user_update: UserUpdate) -> Optional[User]:
        # Convert Pydantic object thành dict, loại bỏ None values
        update_data = user_update.model_dump(exclude_none=True, exclude={'id'})
        
        try:
            user = await UserRepo.get_by_id(db, id)
            updated = False
            for field, value in update_data.items():
                setattr(user, field, value)
                updated = True
            
            if updated:
                user.updated_at = get_current_datetime()
                await db.commit()
                await db.refresh(user)
            
            return user
        except Exception as e:
            await db.rollback()
            logger.error(f'ERROR: {e}')
            raise e
    
    def delete(self, id: str) -> None:
        pass