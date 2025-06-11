"""
인증 관련 API 엔드포인트
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, auth_rate_limit
from app.core.config import settings
from app.schemas.auth import (
    Token, 
    SocialLoginRequest, 
    RefreshTokenRequest,
    AuthResponse
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


@router.post("/kakao/login", response_model=AuthResponse)
async def kakao_login(
    request: SocialLoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit)
):
    """카카오 소셜 로그인"""
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.kakao_login(request.access_token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"카카오 로그인 실패: {str(e)}"
        )


@router.post("/naver/login", response_model=AuthResponse)
async def naver_login(
    request: SocialLoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit)
):
    """네이버 소셜 로그인"""
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.naver_login(request.access_token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"네이버 로그인 실패: {str(e)}"
        )


@router.post("/google/login", response_model=AuthResponse)
async def google_login(
    request: SocialLoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit)
):
    """구글 소셜 로그인"""
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.google_login(request.access_token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"구글 로그인 실패: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit)
):
    """토큰 갱신"""
    auth_service = AuthService(db)
    
    try:
        new_tokens = await auth_service.refresh_access_token(request.refresh_token)
        return new_tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 갱신 실패: {str(e)}"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """로그아웃"""
    auth_service = AuthService(db)
    
    try:
        await auth_service.logout_user(current_user.id)
        return {"message": "로그아웃되었습니다"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"로그아웃 실패: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """현재 사용자 정보 조회"""
    return UserResponse.model_validate(current_user)


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """계정 탈퇴"""
    auth_service = AuthService(db)
    
    try:
        await auth_service.delete_user_account(current_user.id)
        return {"message": "계정이 삭제되었습니다"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"계정 삭제 실패: {str(e)}"
        )