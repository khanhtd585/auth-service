from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from schemas import UserCreate, UserRead, RegisterReponse, UserTokenBase, TokenType
from repo import UserRepo, UserTokenRepo
from utils.hash_utils import hash_password
from utils.utils import generate_confirm_token

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def register_user(db: Session, user_in: UserCreate) -> RegisterReponse:
        # Check email tồn tại chưa
        existing = await UserRepo.get_by_email(db, user_in.email)
        if existing:
            logger.error(f'Email ({existing.email}) already registered')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password
        user_in.password = hash_password(user_in.password)
        logger.info('Hash password')
        
        # Create new user
        new_user = await UserRepo.create(db, user_in)
        logger.info('Create user')
        
        # Create confirm token
        user_token = UserTokenBase(
            user_id=new_user.id,
            token_type=TokenType.confirm,
            token=generate_confirm_token(6),
        )
        confirm_token = await UserTokenRepo.create(db, user_token)
        await UserTokenRepo.push_token_redis(new_user.id, confirm_token.token)
        
        # Response user
        user_rs = RegisterReponse(
            id=new_user.id,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
            last_login_at=new_user.last_login_at,
            email=new_user.email,
            user_name=new_user.user_name,
            status=new_user.status,
            confirm_token=confirm_token.token,
        )
        
        logger.info('Response user')
        return user_rs
    

    @staticmethod
    async def get_user_by_id(db: Session, id: str) -> UserRead:
        # Check email tồn tại chưa
        user = await UserRepo.get_by_id(db, id)
        if not user:
            logger.error(f'Email ({user.email}) already registered')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not exist",
            )

        # Response user
        user_rs = UserRead.model_validate(user)
        return user_rs
