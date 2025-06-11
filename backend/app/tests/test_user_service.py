"""
사용자 서비스 테스트

사용자 관리 기능의 비즈니스 로직을 테스트합니다.
- 사용자 생성/수정/조회
- 웰니스 프로필 관리
- 개인화 데이터 관리
- 데이터 검증 및 예외 처리
"""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, WellnessProfile, PersonalizationData, Gender, FitnessLevel, MotivationStyle
from app.services.user_service import UserService
from app.schemas.user import UserProfileUpdate, WellnessProfileUpdate, PersonalizationDataUpdate
from app.core.exceptions import NotFoundError, ValidationError


class TestUserService:
    """사용자 서비스 테스트 클래스"""

    @pytest.fixture
    async def user_service(self, db: AsyncSession) -> UserService:
        """테스트용 사용자 서비스 인스턴스"""
        return UserService(db)

    @pytest.fixture
    async def sample_user(self, user_service: UserService) -> User:
        """테스트용 샘플 사용자"""
        return await user_service.create_user(
            email="sample@test.com",
            nickname="샘플사용자",
            birth_year=1990,
            gender="male"
        )

    # =================================================================
    # 사용자 생성 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service: UserService):
        """정상적인 사용자 생성 테스트"""
        user = await user_service.create_user(
            email="newuser@example.com",
            nickname="새사용자",
            profile_image_url="https://example.com/image.jpg",
            birth_year=1995,
            gender="female"
        )
        
        assert user.email == "newuser@example.com"
        assert user.nickname == "새사용자"
        assert user.birth_year == 1995
        assert user.gender == Gender.FEMALE
        assert user.is_active is True
        assert user.is_verified is True
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_create_user_minimal_info(self, user_service: UserService):
        """최소 정보로 사용자 생성 테스트"""
        user = await user_service.create_user(
            email="minimal@test.com",
            nickname="최소정보"
        )
        
        assert user.email == "minimal@test.com"
        assert user.nickname == "최소정보"
        assert user.birth_year is None
        assert user.gender is None
        assert user.profile_image_url is None

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service: UserService):
        """중복 이메일로 사용자 생성 시 예외 발생 테스트"""
        # 첫 번째 사용자 생성
        await user_service.create_user(
            email="duplicate@test.com",
            nickname="첫번째"
        )
        
        # 같은 이메일로 두 번째 사용자 생성 시도
        with pytest.raises(ValidationError, match="이미 가입된 이메일입니다"):
            await user_service.create_user(
                email="duplicate@test.com",
                nickname="두번째"
            )

    # =================================================================
    # 사용자 조회 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service: UserService, sample_user: User):
        """ID로 사용자 조회 테스트"""
        found_user = await user_service.get_user_by_id(sample_user.id)
        
        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service: UserService):
        """존재하지 않는 ID로 사용자 조회 테스트"""
        non_existent_id = uuid4()
        user = await user_service.get_user_by_id(non_existent_id)
        
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_service: UserService, sample_user: User):
        """이메일로 사용자 조회 테스트"""
        found_user = await user_service.get_user_by_email(sample_user.email)
        
        assert found_user is not None
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_service: UserService):
        """존재하지 않는 이메일로 사용자 조회 테스트"""
        user = await user_service.get_user_by_email("nonexistent@test.com")
        
        assert user is None

    # =================================================================
    # 사용자 프로필 업데이트 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, user_service: UserService, sample_user: User):
        """사용자 프로필 업데이트 성공 테스트"""
        update_data = UserProfileUpdate(
            nickname="수정된닉네임",
            birth_year=1988,
            gender=Gender.OTHER,
            profile_image_url="https://example.com/new-image.jpg"
        )
        
        updated_user = await user_service.update_user_profile(sample_user.id, update_data)
        
        assert updated_user.nickname == "수정된닉네임"
        assert updated_user.birth_year == 1988
        assert updated_user.gender == Gender.OTHER
        assert updated_user.profile_image_url == "https://example.com/new-image.jpg"
        # 이메일은 변경되지 않아야 함
        assert updated_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_update_user_profile_partial(self, user_service: UserService, sample_user: User):
        """부분적인 사용자 프로필 업데이트 테스트"""
        update_data = UserProfileUpdate(nickname="부분수정만")
        
        updated_user = await user_service.update_user_profile(sample_user.id, update_data)
        
        assert updated_user.nickname == "부분수정만"
        # 다른 필드들은 그대로 유지
        assert updated_user.birth_year == sample_user.birth_year
        assert updated_user.gender == sample_user.gender

    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self, user_service: UserService):
        """존재하지 않는 사용자 프로필 업데이트 테스트"""
        non_existent_id = uuid4()
        update_data = UserProfileUpdate(nickname="존재하지않음")
        
        with pytest.raises(NotFoundError, match="사용자를 찾을 수 없습니다"):
            await user_service.update_user_profile(non_existent_id, update_data)

    # =================================================================
    # 웰니스 프로필 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_create_wellness_profile(self, user_service: UserService, sample_user: User):
        """웰니스 프로필 생성 테스트"""
        wellness_data = WellnessProfileUpdate(
            fitness_level=FitnessLevel.INTERMEDIATE,
            primary_goals=["체중감량", "근력향상"],
            available_time_slots=[{"start": "09:00", "end": "10:00"}],
            preferred_workout_types=["유산소", "근력운동"],
            health_conditions=["없음"],
            wake_up_time="07:00",
            sleep_time="23:00",
            work_schedule={"type": "office", "hours": "09-18"}
        )
        
        profile = await user_service.create_wellness_profile(sample_user.id, wellness_data)
        
        assert profile.user_id == sample_user.id
        assert profile.fitness_level == FitnessLevel.INTERMEDIATE
        assert "체중감량" in profile.primary_goals
        assert profile.wake_up_time == "07:00"
        assert profile.sleep_time == "23:00"

    @pytest.mark.asyncio
    async def test_get_wellness_profile_not_exists(self, user_service: UserService, sample_user: User):
        """존재하지 않는 웰니스 프로필 조회 테스트"""
        profile = await user_service.get_wellness_profile(sample_user.id)
        assert profile is None

    @pytest.mark.asyncio
    async def test_update_wellness_profile_create_if_not_exists(self, user_service: UserService, sample_user: User):
        """웰니스 프로필이 없을 때 업데이트 시 자동 생성 테스트"""
        wellness_data = WellnessProfileUpdate(
            fitness_level=FitnessLevel.ADVANCED,
            primary_goals=["체력향상"]
        )
        
        profile = await user_service.update_wellness_profile(sample_user.id, wellness_data)
        
        assert profile.user_id == sample_user.id
        assert profile.fitness_level == FitnessLevel.ADVANCED
        assert "체력향상" in profile.primary_goals

    # =================================================================
    # 개인화 데이터 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_create_personalization_data(self, user_service: UserService, sample_user: User):
        """개인화 데이터 생성 테스트"""
        personalization_data = PersonalizationDataUpdate(
            personality_type="ENFP",
            motivation_style=MotivationStyle.ACHIEVEMENT,
            coaching_frequency="high",
            preferred_message_times=["09:00", "18:00"],
            language="ko",
            country="KR"
        )
        
        data = await user_service.create_personalization_data(sample_user.id, personalization_data)
        
        assert data.user_id == sample_user.id
        assert data.personality_type == "ENFP"
        assert data.motivation_style == MotivationStyle.ACHIEVEMENT
        assert data.coaching_frequency == "high"
        assert "09:00" in data.preferred_message_times

    @pytest.mark.asyncio
    async def test_update_personalization_data_create_if_not_exists(self, user_service: UserService, sample_user: User):
        """개인화 데이터가 없을 때 업데이트 시 자동 생성 테스트"""
        personalization_data = PersonalizationDataUpdate(
            motivation_style=MotivationStyle.COMPETITIVE
        )
        
        data = await user_service.update_personalization_data(sample_user.id, personalization_data)
        
        assert data.motivation_style == MotivationStyle.COMPETITIVE

    # =================================================================
    # 사용자 비활성화 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_service: UserService, sample_user: User):
        """사용자 비활성화 테스트"""
        result = await user_service.deactivate_user(sample_user.id)
        
        assert result is True
        
        # 사용자가 비활성화되었는지 확인
        updated_user = await user_service.get_user_by_id(sample_user.id)
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, user_service: UserService):
        """존재하지 않는 사용자 비활성화 테스트"""
        non_existent_id = uuid4()
        
        with pytest.raises(NotFoundError, match="사용자를 찾을 수 없습니다"):
            await user_service.deactivate_user(non_existent_id)

    # =================================================================
    # 마지막 로그인 시간 업데이트 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_update_last_login(self, user_service: UserService, sample_user: User):
        """마지막 로그인 시간 업데이트 테스트"""
        # 초기에는 last_login_at이 None
        assert sample_user.last_login_at is None
        
        await user_service.update_last_login(sample_user.id)
        
        # 업데이트 후 확인
        updated_user = await user_service.get_user_by_id(sample_user.id)
        assert updated_user.last_login_at is not None

    # =================================================================
    # 엣지 케이스 및 데이터 무결성 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_wellness_profile_time_validation(self, user_service: UserService, sample_user: User):
        """웰니스 프로필 시간 형식 검증 테스트"""
        # 올바른 시간 형식
        valid_data = WellnessProfileUpdate(
            wake_up_time="07:30",
            sleep_time="23:45"
        )
        
        profile = await user_service.update_wellness_profile(sample_user.id, valid_data)
        assert profile.wake_up_time == "07:30"
        assert profile.sleep_time == "23:45"

    @pytest.mark.asyncio
    async def test_multiple_social_accounts_same_email(self, user_service: UserService):
        """같은 이메일로 여러 소셜 계정 연동 시나리오 테스트"""
        # 이미 카카오로 가입된 사용자가 구글로도 로그인하는 경우
        # 동일한 이메일이면 같은 사용자로 처리되어야 함
        
        user1 = await user_service.create_user(
            email="multi@test.com",
            nickname="멀티사용자"
        )
        
        # 같은 이메일로 다시 조회하면 같은 사용자
        user2 = await user_service.get_user_by_email("multi@test.com")
        
        assert user1.id == user2.id
        assert user1.email == user2.email

    @pytest.mark.asyncio
    async def test_profile_data_consistency(self, user_service: UserService, sample_user: User):
        """프로필 데이터 일관성 테스트"""
        # 웰니스 프로필과 개인화 데이터를 모두 설정
        wellness_data = WellnessProfileUpdate(
            fitness_level=FitnessLevel.BEGINNER,
            primary_goals=["건강관리"]
        )
        
        personalization_data = PersonalizationDataUpdate(
            motivation_style=MotivationStyle.SOCIAL,
            coaching_frequency="normal"
        )
        
        wellness_profile = await user_service.update_wellness_profile(sample_user.id, wellness_data)
        personal_data = await user_service.update_personalization_data(sample_user.id, personalization_data)
        
        # 두 프로필 모두 같은 사용자 ID를 가져야 함
        assert wellness_profile.user_id == sample_user.id
        assert personal_data.user_id == sample_user.id
        assert wellness_profile.user_id == personal_data.user_id

    @pytest.mark.asyncio
    async def test_empty_update_data(self, user_service: UserService, sample_user: User):
        """빈 업데이트 데이터 처리 테스트"""
        original_nickname = sample_user.nickname
        
        # 빈 업데이트 데이터
        empty_update = UserProfileUpdate()
        
        updated_user = await user_service.update_user_profile(sample_user.id, empty_update)
        
        # 기존 데이터가 그대로 유지되어야 함
        assert updated_user.nickname == original_nickname
