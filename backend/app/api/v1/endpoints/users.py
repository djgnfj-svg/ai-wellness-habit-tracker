"""
사용자 관련 API 엔드포인트
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, standard_rate_limit
from app.schemas.user import (
    UserResponse, 
    UserProfileUpdate,
    WellnessProfileUpdate,
    PersonalizationDataUpdate,
    WellnessProfileResponse,
    PersonalizationDataResponse
)
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    _: None = Depends(standard_rate_limit)
):
    """사용자 프로필 조회"""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 프로필 업데이트"""
    user_service = UserService(db)
    
    try:
        updated_user = await user_service.update_user_profile(
            current_user.id, 
            profile_update
        )
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"프로필 업데이트 실패: {str(e)}"
        )


@router.get("/wellness-profile", response_model=WellnessProfileResponse)
async def get_wellness_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """웰니스 프로필 조회"""
    user_service = UserService(db)
    
    wellness_profile = await user_service.get_wellness_profile(current_user.id)
    if not wellness_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="웰니스 프로필을 찾을 수 없습니다"
        )
    
    return WellnessProfileResponse.model_validate(wellness_profile)


@router.put("/wellness-profile", response_model=WellnessProfileResponse)
async def update_wellness_profile(
    wellness_update: WellnessProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """웰니스 프로필 업데이트"""
    user_service = UserService(db)
    
    try:
        updated_profile = await user_service.update_wellness_profile(
            current_user.id,
            wellness_update
        )
        return WellnessProfileResponse.model_validate(updated_profile)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"웰니스 프로필 업데이트 실패: {str(e)}"
        )


@router.get("/personalization", response_model=PersonalizationDataResponse)
async def get_personalization_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """개인화 데이터 조회"""
    user_service = UserService(db)
    
    personalization_data = await user_service.get_personalization_data(current_user.id)
    if not personalization_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="개인화 데이터를 찾을 수 없습니다"
        )
    
    return PersonalizationDataResponse.model_validate(personalization_data)


@router.put("/personalization", response_model=PersonalizationDataResponse)
async def update_personalization_data(
    personalization_update: PersonalizationDataUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """개인화 데이터 업데이트"""
    user_service = UserService(db)
    
    try:
        updated_data = await user_service.update_personalization_data(
            current_user.id,
            personalization_update
        )
        return PersonalizationDataResponse.model_validate(updated_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"개인화 데이터 업데이트 실패: {str(e)}"
        )