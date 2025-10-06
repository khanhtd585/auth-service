from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import logging
from schemas import (ApiResponse, UserCreate, UserRead, 
                     LoginRequest, LoginResponse, 
                     RegisterReponse, RefreshTokenResponse)
from db.database import get_database
from services import UserService, AuthService

router = APIRouter(prefix='/auth')
logger = logging.getLogger(__name__)

db_conn = get_database()


@router.post("/register", response_model=ApiResponse[RegisterReponse], status_code=status.HTTP_201_CREATED)
async def register_user(user_in : UserCreate, db: Session = Depends(db_conn.get_db)):
    new_user = await UserService.register_user(db, user_in)
    return ApiResponse[RegisterReponse](success=True, data=new_user)


@router.post("/refresh-confirm/{user_id}", response_model=ApiResponse[RefreshTokenResponse], status_code=status.HTTP_200_OK)
async def refreshconfirm(user_id: str, db: Session = Depends(db_conn.get_db)):
    res = await AuthService.refresh_confirm(db, user_id)
    return ApiResponse[RefreshTokenResponse](success=True, data=res)


@router.get("/confirm/{user_id}", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def confirm_user(user_id: str, token: str, db: Session = Depends(db_conn.get_db)):
    new_user = await AuthService.confirm_user(db, user_id, token)
    return ApiResponse[UserRead](success=True, data=new_user)


@router.post("/login", response_model=ApiResponse[LoginResponse], status_code=status.HTTP_200_OK)
async def register_user(user_in : LoginRequest, db: Session = Depends(db_conn.get_db)):
    response = await AuthService.login(db, user_in)
    return ApiResponse[LoginResponse](success=True, data=response)
