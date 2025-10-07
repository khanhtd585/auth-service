from fastapi import APIRouter
from . import auth_routes, user_routes

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_routes.router, tags=['auth'])
api_v1_router.include_router(user_routes.router, tags=['user'])
