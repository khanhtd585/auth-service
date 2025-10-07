from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_, delete, desc
from typing import Optional
import logging
import datetime
import json

from common.setting import get_settings
from db.redis_client import get_redis
from models import UserToken
from schemas import (UserUpdate, 
                     TokenType, UserTokenBase)
from utils.datetime_utils import get_current_datetime

logger = logging.getLogger(__name__)
setting = get_settings()
redis_cache = get_redis()

class UserTokenRepo:
    
    @staticmethod
    async def create(db: Session, user_token: UserTokenBase) -> UserToken:
        created_at = get_current_datetime()
        expire_at = created_at + datetime.timedelta(minutes=setting.TOKEN_TTL_SEC)
        new_token = UserToken(
            user_id=user_token.user_id,
            token_type=user_token.token_type,
            token=user_token.token,
            created_at=created_at,
            expire_at=expire_at,
        )
        db.add(new_token)
        
        try:
            await db.flush()  # flush để bắt lỗi unique sớm
        except IntegrityError as e:
            await db.rollback()
            logger.error(f'Error: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User could not be created due to DB constraint",
            )
        
        return new_token

    
    @staticmethod
    async def verify_token(db: Session, user_id: str, token: str, token_type: TokenType) -> Optional[UserToken]:
        stmt = (select(UserToken).where(
                and_(UserToken.user_id == user_id,
                     UserToken.token == token,
                     UserToken.token_type == token_type,
                     UserToken.expire_at >= get_current_datetime()
                     )).order_by(desc(UserToken.expire_at)))
        try:
            result = await db.execute(stmt)
            token_obj = result.scalar_one_or_none()
            if token_obj:
                await UserTokenRepo.delete(db, user_id, token, TokenType.confirm)
                return token_obj
        except Exception as e:
            raise e

    @staticmethod
    async def update(db, id: str, user_update: UserUpdate) -> None:
        pass
    
    async def delete(db: Session, user_id: str, token: str, token_type: TokenType) -> bool:
        stmt = (delete(UserToken).where(
                and_(UserToken.user_id == user_id,
                     UserToken.token == token,
                     UserToken.token_type == token_type,
                )))
        try:
            await db.execute(stmt)
            await db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f'ERROR: {e}')
            raise e

    @staticmethod
    async def push_token_redis(user_id: str, token: str) -> bool:
        """
        Push token vào Redis với user_id làm key (async)
        
        Args:
            user_id: ID của user
            token: Token cần cache
            metadata: Thông tin bổ sung (optional)
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Kiểm tra kết nối
            if not await redis_cache.ping():
                logger.info("❌ Không thể kết nối đến Redis!")
                return False
            
            logger.info("✅ Đã kết nối Redis thành công!")
            
            # Chuẩn bị data để lưu
            cache_data = {
                "token": token,
                "user_id": user_id,
                "created_at": get_current_datetime().isoformat(),
            }
            
            # Tạo key cho Redis
            redis_key = f"token_{TokenType.confirm.value}:{user_id}"
            
            # Lưu vào Redis với TTL
            redis_client = await redis_cache.get_client()
            await redis_client.setex(
                redis_key,
                setting.TOKEN_TTL_SEC,
                json.dumps(cache_data)
            )
            
            # Kiểm tra TTL
            ttl = await redis_client.ttl(redis_key)
            
            logger.info(f"✅ Đã lưu token cho user_id: {user_id}")
            logger.info(f"   Key: {redis_key}")
            logger.info(f"   TTL: {ttl} giây (~{ttl//60} phút)")
            logger.info(f"   Token: {token[:20]}..." if len(token) > 20 else f"   Token: {token}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi push token: {str(e)}")
            return False
        
    @staticmethod
    async def verify_token_redis(user_id: str) -> bool:
        """
        Lấy token từ Redis theo user_id (async)
        
        Args:
            user_id: ID của user
        
        Returns:
            dict: Thông tin token hoặc None nếu không tìm thấy
        """
        try:
            # Kiểm tra kết nối
            if not await redis_cache.ping():
                logger.info("❌ Không thể kết nối đến Redis!")
                return None
            
            logger.info("✅ Đã kết nối Redis thành công!")
            
            # Tạo key cho Redis
            redis_key = f"token_{TokenType.confirm.value}:{user_id}"
            
            # Lấy data từ Redis
            redis_client = await redis_cache.get_client()
            cached_data = await redis_client.get(redis_key)
            
            if not cached_data:
                logger.info(f"❌ Không tìm thấy token cho user_id: {user_id}")
                logger.info(f"   Key: {redis_key}")
                logger.info(f"   (Token có thể đã hết hạn hoặc chưa được tạo)")
                return None
            
            # Parse JSON
            token_data = json.loads(cached_data)
            
            # Lấy TTL còn lại
            ttl = await redis_client.ttl(redis_key)
            
            logger.info(f"✅ Đã tìm thấy token cho user_id: {user_id}")
            logger.info(f"   Key: {redis_key}")
            logger.info(f"   TTL còn lại: {ttl} giây (~{ttl//60} phút {ttl%60} giây)")
            logger.info(f"   Token: {token_data['token'][:30]}..." if len(token_data['token']) > 30 else f"   Token: {token_data['token']}")
            logger.info(f"   Created at: {token_data['created_at']}")
            
            await redis_client.delete(redis_key)
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Lỗi khi parse JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi get token: {str(e)}")
            return None
