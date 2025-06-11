"""
사용자 관리 서비스
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User, WellnessProfile, PersonalizationData
from app.schemas.user import UserProfileUpdate, WellnessProfileUpdate, PersonalizationDataUpdate
from app.core.exceptions import NotFoundError, ValidationError


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        nickname: str,
        profile_image_url: Optional[str] = None,
        birth_year: Optional[int] = None,
        gender: Optional[str] = None
    ) -> User:
        """새 사용자 생성"""
        # 이메일 중복 체크
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValidationError("이미 가입된 이메일입니다")

        user = User(
            email=email,
            nickname=nickname,
            profile_image_url=profile_image_url,
            birth_year=birth_year,
            gender=gender,
            is_active=True,
            is_verified=True  # 소셜 로그인은 자동 인증
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_profile(
        self, 
        user_id: UUID, 
        profile_update: UserProfileUpdate
    ) -> User:
        """사용자 프로필 업데이트"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        # 업데이트할 필드만 변경
        update_data = profile_update.model_dump(exclude_unset=True)
        
        if update_data:
            stmt = update(User).where(User.id == user_id).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(user)
        
        return user

    async def get_wellness_profile(self, user_id: UUID) -> Optional[WellnessProfile]:
        """웰니스 프로필 조회"""
        stmt = select(WellnessProfile).where(WellnessProfile.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_wellness_profile(
        self,
        user_id: UUID,
        wellness_data: WellnessProfileUpdate
    ) -> WellnessProfile:
        """웰니스 프로필 생성"""
        profile = WellnessProfile(
            user_id=user_id,
            **wellness_data.model_dump()
        )
        
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update_wellness_profile(
        self,
        user_id: UUID,
        wellness_update: WellnessProfileUpdate
    ) -> WellnessProfile:
        """웰니스 프로필 업데이트"""
        profile = await self.get_wellness_profile(user_id)
        
        if not profile:
            # 프로필이 없으면 새로 생성
            return await self.create_wellness_profile(user_id, wellness_update)
        
        update_data = wellness_update.model_dump(exclude_unset=True)
        if update_data:
            stmt = update(WellnessProfile).where(
                WellnessProfile.user_id == user_id
            ).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(profile)
        
        return profile

    async def get_personalization_data(self, user_id: UUID) -> Optional[PersonalizationData]:
        """개인화 데이터 조회"""
        stmt = select(PersonalizationData).where(PersonalizationData.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_personalization_data(
        self,
        user_id: UUID,
        personalization_data: PersonalizationDataUpdate
    ) -> PersonalizationData:
        """개인화 데이터 생성"""
        data = PersonalizationData(
            user_id=user_id,
            **personalization_data.model_dump()
        )
        
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data

    async def update_personalization_data(
        self,
        user_id: UUID,
        personalization_update: PersonalizationDataUpdate
    ) -> PersonalizationData:
        """개인화 데이터 업데이트"""
        data = await self.get_personalization_data(user_id)
        
        if not data:
            # 데이터가 없으면 새로 생성
            return await self.create_personalization_data(user_id, personalization_update)
        
        update_fields = personalization_update.model_dump(exclude_unset=True)
        if update_fields:
            stmt = update(PersonalizationData).where(
                PersonalizationData.user_id == user_id
            ).values(**update_fields)
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(data)
        
        return data

    async def deactivate_user(self, user_id: UUID) -> bool:
        """사용자 비활성화 (탈퇴)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        stmt = update(User).where(User.id == user_id).values(is_active=False)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def update_last_login(self, user_id: UUID) -> None:
        """마지막 로그인 시간 업데이트"""
        from datetime import datetime
        stmt = update(User).where(User.id == user_id).values(
            last_login_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()
