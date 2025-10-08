from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging
from schemas import (ApiResponse, UserCreate, UserRead, 
                     LoginRequest, LoginResponse, 
                     RegisterReponse, RefreshTokenResponse)
from db.database import get_database
from services import AuthService
from common.setting import get_settings
import httpx

router = APIRouter(prefix='/auth')
logger = logging.getLogger(__name__)

db_conn = get_database()
setting = get_settings()


@router.post("/signup", response_model=ApiResponse[RegisterReponse], status_code=status.HTTP_201_CREATED)
async def register_user(user_in : UserCreate, db: Session = Depends(db_conn.get_db)):
    new_user = await AuthService.register_user(db, user_in)
    return ApiResponse[RegisterReponse](success=True, data=new_user)


@router.post("/refresh-confirm/{user_id}", response_model=ApiResponse[RefreshTokenResponse], status_code=status.HTTP_200_OK)
async def refreshconfirm(user_id: str, db: Session = Depends(db_conn.get_db)):
    res = await AuthService.refresh_confirm(db, user_id)
    return ApiResponse[RefreshTokenResponse](success=True, data=res)


@router.get("/confirm/{user_id}", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def confirm_user(user_id: str, token: str, db: Session = Depends(db_conn.get_db)):
    new_user = await AuthService.confirm_user(db, user_id, token)
    return ApiResponse[UserRead](success=True, data=new_user)


@router.post("/signin", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def signin_user(user_in : LoginRequest, db: Session = Depends(db_conn.get_db)):
    response: LoginResponse = await AuthService.login(db, user_in)
    return response

@router.get("/google/login")
def google_login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={setting.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={setting.GOOGLE_REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
    )
    return {"url": google_auth_url}


@router.get("/google/callback")
async def google_callback(request: Request,
                          db: Session = Depends(db_conn.get_db)):
    code = request.query_params.get("code")
    # Gửi mã code này lên Google để lấy access_token + user info
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": setting.GOOGLE_CLIENT_ID,
                "client_secret": setting.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": setting.GOOGLE_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tokens = token_resp.json()
        # Lấy thông tin user
        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        user_info = userinfo_resp.json()
        res: LoginResponse = await AuthService.login_gg(db, user_info)

        FE_URL = f"{setting.FE_URI}/signin/success"  # FE path nhận token
        redirect_url = f"{FE_URL}?token={res.access_token}&refresh_token={res.refresh_token}"
        return RedirectResponse(redirect_url)

