from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import logging
from schemas import (ApiResponse, UserCreate, UserRead)
from db.database import get_database
from services import UserService
from api.depend.auth_depend import get_current_user 

router = APIRouter(prefix='/user')
logger = logging.getLogger(__name__)

db_conn = get_database()

@router.get("/", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    db: Session = Depends(db_conn.get_db),
    _: UserRead = Depends(get_current_user)
    ):
    user = await UserService.get_user_by_id(db, user_id)
    return ApiResponse[UserRead](success=True, data=user)

@router.get("/profile", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def get_own_profile(
    db: Session = Depends(db_conn.get_db),
    current_user: UserRead = Depends(get_current_user)
    ):
    return ApiResponse[UserRead](success=True, data=current_user)

