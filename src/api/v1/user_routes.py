from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import logging
from schemas import (ApiResponse, UserCreate, UserRead)
from db.database import get_database
from services import UserService

router = APIRouter(prefix='/user')
logger = logging.getLogger(__name__)

db_conn = get_database()

@router.get("/{user_id}", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    db: Session = Depends(db_conn.get_db)):
    
    user = await UserService.get_user_by_id(db, user_id)
    return ApiResponse[UserRead](success=True, data=user)

