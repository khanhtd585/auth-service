import datetime
from jose import JWTError, jwt
from common.setting import get_settings
from utils.datetime_utils import get_current_datetime
import logging

setting = get_settings()
logger = logging.getLogger(__name__)


def create_jwt_token(data: dict, secret_key=setting.JWT_SECRET):
    expires_dt = get_current_datetime() + datetime.timedelta(seconds=setting.ACCESS_TOKEN_EXPIRES_SECONDS)
    expires_st = int(expires_dt.timestamp())
    
    access_payload = {
        "user_id": str(data["user_id"]),
        "email": data["email"],
        "name": data["name"],
        "role": data["role"],
        "exp": expires_st,
        "expires_iso": expires_dt.isoformat() + "Z",
    }
    
    # Refresh token - 7 ngày
    refresh_expires =  get_current_datetime() + datetime.timedelta(days=setting.REFRESH_TOKEN_EXPIRES_DAY)
    refresh_payload = {
        "user_id": str(data["user_id"]),
        "exp": int(refresh_expires.timestamp()),
        "type": "refresh"
    }
    
    access_token = jwt.encode(access_payload, secret_key, setting.JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, secret_key, setting.JWT_ALGORITHM)
    
    return access_token, expires_st, refresh_token

def verify_jwt_token(token: str, secret_key=setting.JWT_SECRET):
    """
    Verify JWT token using PyJWT built-in validation
    
    Returns:
        dict: Token payload if valid
        None: If token is invalid or expired
    """
    try:
        # PyJWT sẽ tự động check exp field nếu có trong payload
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=["HS256"],
            options={"verify_exp": True}  # Verify expiration
        )
        return payload
        
    except JWTError as e:
        logger.error(e)
        return None
