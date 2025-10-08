from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from schemas import UserRead
from repo import UserRepo


logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def get_user_by_id(db: Session, id: str) -> UserRead:
        # Check email tồn tại chưa
        user = await UserRepo.get_by_id(db, id)
        if not user:
            logger.error(f'User ID ({id}) not exist')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not exist",
            )
        # Response user
        user_rs = UserRead.model_validate(user)
        return user_rs
