"""
사용자 관리 서비스
사용자 프로필, 웰니스 설정, 개인화 데이터 관리를 담당합니다.

주요 기능:
- 사용자 CRUD 작업
- 웰니스 프로필 관리 (운동 선호도, 목표 등)
- 개인화 데이터 관리 (성격, 동기부여 스타일 등)
- 계정 상태 관리 (활성화/비활성화)
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User, WellnessProfile, PersonalizationData
from app.schemas.user import UserProfileUpdate, WellnessProfileUpdate, PersonalizationDataUpdate
from app.core.exceptions import NotFoundError, ValidationError, ConflictError


class UserService:
    """
    사용자 관리 서비스 클래스
    
    사용자와 관련된 모든 비즈니스 로직을 처리합니다.
    데이터베이스 작업과 비즈니스 규칙 검증을 담당하며,
    API 계층과 데이터 계층 사이의 중간 역할을 수행합니다.
    
    Attributes:
        db (AsyncSession): 데이터베이스 세션
    """
    
    def __init__(self, db: AsyncSession):
        """
        서비스 초기화
        
        Args:
            db: 비동기 데이터베이스 세션
        """
        self.db = db

    # =================================================================
    # 사용자 기본 정보 관리
    # =================================================================

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        사용자 ID로 사용자 정보 조회
        
        Args:
            user_id: 조회할 사용자의 UUID
            
        Returns:
            User 또는 None: 사용자 정보 (존재하지 않으면 None)
            
        Example:
            user = await user_service.get_user_by_id(user_id)
            if user:
                print(f"사용자: {user.nickname}")
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 정보 조회
        
        소셜 로그인 시 중복 계정 확인용으로 주로 사용됩니다.
        이메일은 시스템에서 고유한 식별자 역할을 합니다.
        
        Args:
            email: 조회할 이메일 주소
            
        Returns:
            User 또는 None: 사용자 정보 (존재하지 않으면 None)
            
        Note:
            이메일은 대소문자를 구분하지 않으므로 소문자로 변환하여 검색합니다.
        """
        # 이메일 정규화 (소문자 변환)
        normalized_email = email.lower().strip()
        
        stmt = select(User).where(User.email == normalized_email)
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
        """
        새로운 사용자 생성
        
        소셜 로그인을 통해 신규 사용자가 가입할 때 호출됩니다.
        이메일 중복 검사와 기본값 설정을 수행합니다.
        
        Args:
            email: 사용자 이메일 (필수, 고유값)
            nickname: 사용자 닉네임 (필수)
            profile_image_url: 프로필 이미지 URL (선택)
            birth_year: 출생년도 (선택)
            gender: 성별 (선택)
            
        Returns:
            User: 생성된 사용자 객체
            
        Raises:
            ValidationError: 이메일이 이미 존재하는 경우
            ValidationError: 필수 필드가 비어있는 경우
            
        Example:
            user = await user_service.create_user(
                email="user@example.com",
                nickname="테스트사용자",
                birth_year=1990
            )
        """
        # 입력값 검증
        if not email or not email.strip():
            raise ValidationError("이메일은 필수 입력값입니다")
        
        if not nickname or not nickname.strip():
            raise ValidationError("닉네임은 필수 입력값입니다")
        
        # 이메일 정규화
        normalized_email = email.lower().strip()
        normalized_nickname = nickname.strip()
        
        # 이메일 중복 검사
        existing_user = await self.get_user_by_email(normalized_email)
        if existing_user:
            raise ConflictError("이미 가입된 이메일입니다")
        
        # 출생년도 유효성 검사
        if birth_year is not None:
            current_year = datetime.now().year
            if birth_year < 1900 or birth_year > current_year:
                raise ValidationError("올바르지 않은 출생년도입니다")
        
        # 새 사용자 생성
        user = User(
            email=normalized_email,
            nickname=normalized_nickname,
            profile_image_url=profile_image_url,
            birth_year=birth_year,
            gender=gender,
            is_active=True,
            is_verified=True,  # 소셜 로그인은 자동 인증 처리
            timezone="Asia/Seoul"  # 기본 한국 시간대
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
        """
        사용자 기본 프로필 정보 업데이트
        
        사용자가 설정에서 기본 정보를 수정할 때 사용됩니다.
        변경된 필드만 업데이트하고 나머지는 그대로 유지합니다.
        
        Args:
            user_id: 업데이트할 사용자 ID
            profile_update: 업데이트할 프로필 정보
            
        Returns:
            User: 업데이트된 사용자 객체
            
        Raises:
            NotFoundError: 사용자를 찾을 수 없는 경우
            ValidationError: 입력값이 올바르지 않은 경우
            
        Example:
            update_data = UserProfileUpdate(
                nickname="새로운닉네임",
                birth_year=1995
            )
            updated_user = await user_service.update_user_profile(user_id, update_data)
        """
        # 사용자 존재 확인
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        # 업데이트할 필드만 추출 (None이 아닌 값들만)
        update_data = profile_update.model_dump(exclude_unset=True)
        
        if not update_data:
            # 업데이트할 내용이 없으면 기존 사용자 반환
            return user
        
        # 개별 필드 검증
        if "nickname" in update_data:
            nickname = update_data["nickname"].strip()
            if not nickname:
                raise ValidationError("닉네임은 비어있을 수 없습니다")
            if len(nickname) < 2 or len(nickname) > 50:
                raise ValidationError("닉네임은 2-50자 사이여야 합니다")
            update_data["nickname"] = nickname
        
        if "birth_year" in update_data:
            birth_year = update_data["birth_year"]
            if birth_year is not None:
                current_year = datetime.now().year
                if birth_year < 1900 or birth_year > current_year:
                    raise ValidationError("올바르지 않은 출생년도입니다")
        
        # 데이터베이스 업데이트
        stmt = update(User).where(User.id == user_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()
        
        # 업데이트된 사용자 정보 다시 조회
        await self.db.refresh(user)
        return user

    # =================================================================
    # 웰니스 프로필 관리  
    # =================================================================

    async def get_wellness_profile(self, user_id: UUID) -> Optional[WellnessProfile]:
        """
        사용자의 웰니스 프로필 조회
        
        운동 레벨, 목표, 선호도 등의 웰니스 관련 설정을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            WellnessProfile 또는 None: 웰니스 프로필 (없으면 None)
        """
        stmt = select(WellnessProfile).where(WellnessProfile.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_wellness_profile(
        self,
        user_id: UUID,
        wellness_data: WellnessProfileUpdate
    ) -> WellnessProfile:
        """
        새로운 웰니스 프로필 생성
        
        Args:
            user_id: 사용자 ID
            wellness_data: 웰니스 프로필 데이터
            
        Returns:
            WellnessProfile: 생성된 웰니스 프로필
            
        Raises:
            NotFoundError: 사용자를 찾을 수 없는 경우
            ConflictError: 이미 웰니스 프로필이 존재하는 경우
        """
        # 사용자 존재 확인
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")
        
        # 기존 프로필 존재 확인
        existing_profile = await self.get_wellness_profile(user_id)
        if existing_profile:
            raise ConflictError("이미 웰니스 프로필이 존재합니다")
        
        # 입력 데이터 검증 및 정리
        profile_data = wellness_data.model_dump(exclude_unset=True)
        
        # 시간 형식 검증 (wake_up_time, sleep_time)
        for time_field in ["wake_up_time", "sleep_time"]:
            if time_field in profile_data and profile_data[time_field]:
                time_value = profile_data[time_field]
                if not self._validate_time_format(time_value):
                    raise ValidationError(f"{time_field}은 HH:MM 형식이어야 합니다")
        
        # 웰니스 프로필 생성
        profile = WellnessProfile(
            user_id=user_id,
            **profile_data
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
        """
        웰니스 프로필 업데이트 또는 생성
        
        기존 프로필이 있으면 업데이트하고, 없으면 새로 생성합니다.
        
        Args:
            user_id: 사용자 ID
            wellness_update: 업데이트할 웰니스 데이터
            
        Returns:
            WellnessProfile: 업데이트된 웰니스 프로필
            
        Raises:
            NotFoundError: 사용자를 찾을 수 없는 경우
            ValidationError: 입력값이 올바르지 않은 경우
        """
        profile = await self.get_wellness_profile(user_id)
        
        if not profile:
            # 프로필이 없으면 새로 생성
            return await self.create_wellness_profile(user_id, wellness_update)
        
        # 업데이트할 데이터 추출
        update_data = wellness_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return profile
        
        # 시간 형식 검증
        for time_field in ["wake_up_time", "sleep_time"]:
            if time_field in update_data and update_data[time_field]:
                time_value = update_data[time_field]
                if not self._validate_time_format(time_value):
                    raise ValidationError(f"{time_field}은 HH:MM 형식이어야 합니다")
        
        # 목표 및 선호도 리스트 검증
        if "primary_goals" in update_data:
            goals = update_data["primary_goals"]
            if goals and len(goals) > 10:
                raise ValidationError("주요 목표는 최대 10개까지 설정 가능합니다")
        
        if "preferred_workout_types" in update_data:
            workout_types = update_data["preferred_workout_types"]
            if workout_types and len(workout_types) > 15:
                raise ValidationError("선호 운동 유형은 최대 15개까지 설정 가능합니다")
        
        # 데이터베이스 업데이트
        stmt = update(WellnessProfile).where(
            WellnessProfile.user_id == user_id
        ).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile

    # =================================================================
    # 개인화 데이터 관리
    # =================================================================

    async def get_personalization_data(self, user_id: UUID) -> Optional[PersonalizationData]:
        """
        사용자의 개인화 데이터 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            PersonalizationData 또는 None: 개인화 데이터 (없으면 None)
        """
        stmt = select(PersonalizationData).where(PersonalizationData.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_personalization_data(
        self,
        user_id: UUID,
        personalization_data: PersonalizationDataUpdate
    ) -> PersonalizationData:
        """
        새로운 개인화 데이터 생성
        
        Args:
            user_id: 사용자 ID
            personalization_data: 개인화 데이터
            
        Returns:
            PersonalizationData: 생성된 개인화 데이터
        """
        # 사용자 존재 확인
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")
        
        # 기존 데이터 존재 확인
        existing_data = await self.get_personalization_data(user_id)
        if existing_data:
            raise ConflictError("이미 개인화 데이터가 존재합니다")
        
        data = PersonalizationData(
            user_id=user_id,
            **personalization_data.model_dump(exclude_unset=True)
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
        """
        개인화 데이터 업데이트 또는 생성
        
        Args:
            user_id: 사용자 ID
            personalization_update: 업데이트할 개인화 데이터
            
        Returns:
            PersonalizationData: 업데이트된 개인화 데이터
        """
        data = await self.get_personalization_data(user_id)
        
        if not data:
            # 데이터가 없으면 새로 생성
            return await self.create_personalization_data(user_id, personalization_update)
        
        update_fields = personalization_update.model_dump(exclude_unset=True)
        
        if not update_fields:
            return data
        
        # 메시지 시간 검증
        if "preferred_message_times" in update_fields:
            message_times = update_fields["preferred_message_times"]
            if message_times:
                for time_str in message_times:
                    if not self._validate_time_format(time_str):
                        raise ValidationError(f"올바르지 않은 시간 형식: {time_str}")
                
                if len(message_times) > 10:
                    raise ValidationError("선호 메시지 시간은 최대 10개까지 설정 가능합니다")
        
        # 데이터베이스 업데이트
        stmt = update(PersonalizationData).where(
            PersonalizationData.user_id == user_id
        ).values(**update_fields)
        await self.db.execute(stmt)
        await self.db.commit()
        await self.db.refresh(data)
        
        return data

    # =================================================================
    # 계정 관리
    # =================================================================

    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        사용자 계정 비활성화 (탈퇴 처리)
        
        사용자 데이터를 완전히 삭제하지 않고 비활성화 상태로 변경합니다.
        이는 실수로 탈퇴한 경우 복구 가능성을 위한 조치입니다.
        
        Args:
            user_id: 비활성화할 사용자 ID
            
        Returns:
            bool: 비활성화 성공 여부
            
        Raises:
            NotFoundError: 사용자를 찾을 수 없는 경우
            
        Note:
            실제 데이터 삭제는 별도의 배치 작업으로 진행됩니다.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다")

        # 계정 비활성화
        stmt = update(User).where(User.id == user_id).values(
            is_active=False,
            # 탈퇴 시점 기록을 위해 updated_at은 자동으로 갱신됨
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def update_last_login(self, user_id: UUID) -> None:
        """
        사용자 마지막 로그인 시간 업데이트
        
        로그인 성공 시 호출되어 사용자의 활동 기록을 갱신합니다.
        
        Args:
            user_id: 사용자 ID
            
        Note:
            실패해도 로그인 프로세스에 영향을 주지 않도록 예외를 발생시키지 않습니다.
        """
        try:
            stmt = update(User).where(User.id == user_id).values(
                last_login_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
        except Exception:
            # 로그인 기록 업데이트 실패는 전체 로그인 프로세스에 영향을 주지 않음
            pass

    # =================================================================
    # 유틸리티 메서드
    # =================================================================

    def _validate_time_format(self, time_str: str) -> bool:
        """
        시간 형식 검증 (HH:MM)
        
        Args:
            time_str: 검증할 시간 문자열
            
        Returns:
            bool: 유효한 형식인지 여부
        """
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    async def get_user_with_profiles(self, user_id: UUID) -> Optional[User]:
        """
        사용자와 관련 프로필을 모두 포함하여 조회
        
        웰니스 프로필과 개인화 데이터를 함께 로드하여 
        여러 번의 쿼리를 방지합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            User 또는 None: 프로필이 포함된 사용자 정보
        """
        stmt = select(User).options(
            selectinload(User.wellness_profile),
            selectinload(User.personalization_data)
        ).where(User.id == user_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
