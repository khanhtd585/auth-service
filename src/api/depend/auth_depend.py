from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.database import get_database
from repo import UserRepo
from schemas import UserRead
from utils.jwt_utils import verify_jwt_token
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/signin")
db_conn = get_database()

async def get_current_user(token: str = Depends(oauth2_scheme), 
                           db: Session = Depends(db_conn.get_db)) -> UserRead:
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(payload)
    user_id: str = payload.get("user_id")
    logger.info(f"user_id: {user_id}")
    user = await UserRepo.get_by_id(db, user_id)
    logger.info(f"email: {user.email}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)

