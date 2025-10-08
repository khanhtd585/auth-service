from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from schemas import (LoginRequest, LoginResponse, UserUpdate, 
                     TokenType, UserStatus, UserRead,
                     UserTokenBase, RefreshTokenResponse,
                     UserCreate, RegisterReponse,
                     
                     )
from repo import UserRepo, UserTokenRepo
from utils.hash_utils import verify_password
from utils.jwt_utils import create_jwt_token, verify_jwt_token
from utils.datetime_utils import get_current_datetime
from utils.hash_utils import hash_password
from utils.utils import generate_confirm_token

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def login(db: Session, user_in: LoginRequest) -> LoginResponse:
        # Check email tồn tại chưa
        user = await UserRepo.get_by_email(db, user_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password not correct",
            )

        # Verify password
        if verify_password(password=user_in.password, hash_str=user.password) == False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password not correct",
            )
        
        # Tạo JWT token
        user_data  = {
                        "user_id": user.id,
                        "email": user.email, 
                        "name": user.user_name,
                        "role": "user"
                    }
        access_token, exp, refresh_token = create_jwt_token(user_data)
        
        response = LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=exp,
            token_type="Bearer"
        )
        
        # Update last login
        await UserRepo.update(db, user.id, UserUpdate(id=user.id, last_login_at=get_current_datetime()))
        return response


    @staticmethod
    async def confirm_user(db: Session, user_id: str, token: str) -> UserRead:
        
        check_redis = await UserTokenRepo.verify_token_redis(user_id=user_id)
        if not check_redis:
            # Verify password
            token_db = await UserTokenRepo.verify_token(db, user_id, token, TokenType.confirm)
            
            if not token_db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token is Invalid",
                )
        
        user = await UserRepo.update(db, id=user_id, user_update=UserUpdate(id=user_id, status=UserStatus.active))
        user_rs = UserRead.model_validate(user)
        
        return user_rs
    
    @staticmethod
    async def refresh_confirm(db: Session, user_id: str) -> UserRead:
        # Check email tồn tại chưa
        user = await UserRepo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not incorrect",
            )

        # Create confirm token
        user_token = UserTokenBase(
            user_id=user_id,
            token_type=TokenType.confirm,
            token=generate_confirm_token(6),
        )
        
        confirm_token = await UserTokenRepo.create(db, user_token)
        await UserTokenRepo.push_token_redis(user_id, confirm_token.token)
        
        return RefreshTokenResponse(confirm_token=confirm_token.token)
    
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
    async def login_gg(db: Session, data: dict) -> LoginResponse:
        # Check email tồn tại chưa
        user_db = await UserRepo.get_by_email(db, data['email'])
        if user_db:
            logger.info(f'Email ({user_db.email}) exist and login by google auth')
        else:
            user_in = UserCreate(
                email=data['email'],
                user_name=data['name'],
                password=generate_confirm_token(),
            )

            # Hash password
            user_in.password = hash_password(user_in.password)
            logger.info('Hash password')
            
            # Create new user
            user_db = await UserRepo.create(db, user_in)
            logger.info('Create user')
        
        # Tạo JWT token
        user_data  = {
                        "user_id": user_db.id,
                        "email": user_db.email, 
                        "name": user_db.user_name,
                        "role": "user"
                    }
        access_token, exp, refresh_token = create_jwt_token(user_data)
        
        response = LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=exp,
            token_type="Bearer"
        )
        
        # Update last login
        await UserRepo.update(db, user_db.id, UserUpdate(id=user_db.id, last_login_at=get_current_datetime()))
        return response
