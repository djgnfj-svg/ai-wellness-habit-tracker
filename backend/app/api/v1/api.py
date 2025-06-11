"""
API v1 라우터 통합
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# 각 엔드포인트 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])