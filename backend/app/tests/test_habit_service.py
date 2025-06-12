"""
습관 서비스 테스트
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.habit_service import HabitService
from app.models.habit import (
    HabitCategory, HabitTemplate, UserHabit, HabitLog,
    FrequencyType, CompletionStatus, DifficultyLevel
)
from app.models.user import User
from app.schemas.habit import (
    HabitCategoryCreate, HabitTemplateCreate, HabitTemplateSearchParams,
    UserHabitCreate, UserHabitFilterParams, HabitLogCreate,
    FrequencyConfig, ReminderConfig
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError


class TestHabitService:
    """습관 서비스 테스트 클래스"""
    
    @pytest.fixture
    async def habit_service(self, db_session: AsyncSession):
        """습관 서비스 픽스처"""
        return HabitService(db_session)
    
    @pytest.fixture
    async def sample_user(self, db_session: AsyncSession):
        """테스트용 사용자 생성"""
        user = User(
            email="test@example.com",
            nickname="테스트사용자",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    
    @pytest.fixture
    async def sample_category(self, db_session: AsyncSession):
        """테스트용 카테고리 생성"""
        category = HabitCategory(
            name="운동",
            description="신체 활동 관련 습관",
            icon="💪",
            color_code="#34C759",
            sort_order=1
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category
    
    @pytest.fixture
    async def sample_template(self, db_session: AsyncSession, sample_category: HabitCategory):
        """테스트용 습관 템플릿 생성"""
        template = HabitTemplate(
            name="물 8잔 마시기",
            description="하루 2L 물 섭취로 건강한 수분 보충",
            category_id=sample_category.id,
            difficulty_level=DifficultyLevel.EASY,
            estimated_time_minutes=0,
            recommended_frequency_type=FrequencyType.DAILY,
            recommended_frequency_count=8,
            success_criteria="하루 8잔의 물을 마시기",
            tips=["아침에 물 한 잔으로 시작", "식사 전 물 마시기"],
            benefits=["수분 보충", "신진대사 향상"],
            ai_coaching_prompts=["물 마실 시간이에요! 💧"]
        )
        db_session.add(template)
        await db_session.commit()
        await db_session.refresh(template)
        return template


class TestHabitCategoryService(TestHabitService):
    """습관 카테고리 서비스 테스트"""
    
    async def test_get_categories(self, habit_service: HabitService, sample_category: HabitCategory):
        """카테고리 목록 조회 테스트"""
        categories = await habit_service.get_categories()
        
        assert len(categories) >= 1
        assert any(cat.name == "운동" for cat in categories)
    
    async def test_get_category_by_id(self, habit_service: HabitService, sample_category: HabitCategory):
        """카테고리 ID로 조회 테스트"""
        category = await habit_service.get_category_by_id(sample_category.id)
        
        assert category is not None
        assert category.name == "운동"
        assert category.icon == "💪"
    
    async def test_get_category_by_invalid_id(self, habit_service: HabitService):
        """존재하지 않는 카테고리 조회 테스트"""
        invalid_id = uuid4()
        category = await habit_service.get_category_by_id(invalid_id)
        
        assert category is None
    
    async def test_create_category(self, habit_service: HabitService):
        """카테고리 생성 테스트"""
        category_data = HabitCategoryCreate(
            name="영양",
            description="영양 관리 관련 습관",
            icon="🥗",
            color_code="#FF9500",
            sort_order=2
        )
        
        category = await habit_service.create_category(category_data)
        
        assert category.name == "영양"
        assert category.icon == "🥗"
        assert category.color_code == "#FF9500"
        assert category.is_active is True
    
    async def test_create_duplicate_category(self, habit_service: HabitService, sample_category: HabitCategory):
        """중복 카테고리 생성 테스트"""
        category_data = HabitCategoryCreate(
            name="운동",  # 이미 존재하는 이름
            description="또 다른 운동 카테고리",
            icon="🏃",
            color_code="#FF0000"
        )
        
        with pytest.raises(ConflictError):
            await habit_service.create_category(category_data)


class TestHabitTemplateService(TestHabitService):
    """습관 템플릿 서비스 테스트"""
    
    async def test_get_habit_templates(self, habit_service: HabitService, sample_template: HabitTemplate):
        """습관 템플릿 목록 조회 테스트"""
        search_params = HabitTemplateSearchParams(page=1, limit=20)
        templates, total_count = await habit_service.get_habit_templates(search_params)
        
        assert len(templates) >= 1
        assert total_count >= 1
        assert any(t.name == "물 8잔 마시기" for t in templates)
    
    async def test_get_habit_templates_with_filter(self, habit_service: HabitService, sample_template: HabitTemplate):
        """필터를 적용한 습관 템플릿 조회 테스트"""
        search_params = HabitTemplateSearchParams(
            difficulty_level=DifficultyLevel.EASY,
            page=1,
            limit=20
        )
        templates, total_count = await habit_service.get_habit_templates(search_params)
        
        assert all(t.difficulty_level == DifficultyLevel.EASY for t in templates)
    
    async def test_get_habit_template_by_id(self, habit_service: HabitService, sample_template: HabitTemplate):
        """습관 템플릿 ID로 조회 테스트"""
        template = await habit_service.get_habit_template_by_id(sample_template.id)
        
        assert template is not None
        assert template.name == "물 8잔 마시기"
        assert template.difficulty_level == DifficultyLevel.EASY
    
    async def test_create_habit_template(self, habit_service: HabitService, sample_category: HabitCategory):
        """습관 템플릿 생성 테스트"""
        template_data = HabitTemplateCreate(
            name="15분 스트레칭",
            description="목과 어깨 스트레칭으로 뻐근함 해소",
            category_id=sample_category.id,
            difficulty_level=DifficultyLevel.EASY,
            estimated_time_minutes=15,
            recommended_frequency_type=FrequencyType.DAILY,
            recommended_frequency_count=1,
            success_criteria="15분 동안 스트레칭 완료",
            tips=["천천히 호흡하며 진행", "무리하지 말고 편안하게"],
            benefits=["혈액순환 개선", "스트레스 해소"]
        )
        
        template = await habit_service.create_habit_template(template_data)
        
        assert template.name == "15분 스트레칭"
        assert template.estimated_time_minutes == 15
        assert len(template.tips) == 2
        assert template.is_active is True
    
    async def test_create_template_with_invalid_category(self, habit_service: HabitService):
        """존재하지 않는 카테고리로 템플릿 생성 테스트"""
        invalid_category_id = uuid4()
        template_data = HabitTemplateCreate(
            name="잘못된 템플릿",
            category_id=invalid_category_id,
            difficulty_level=DifficultyLevel.EASY
        )
        
        with pytest.raises(ValidationError):
            await habit_service.create_habit_template(template_data)


class TestUserHabitService(TestHabitService):
    """사용자 습관 서비스 테스트"""
    
    async def test_get_user_habits_empty(self, habit_service: HabitService, sample_user: User):
        """빈 사용자 습관 목록 조회 테스트"""
        habits = await habit_service.get_user_habits(sample_user.id)
        
        assert len(habits) == 0
    
    async def test_create_user_habit(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """사용자 습관 생성 테스트"""
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            custom_name="나만의 물 마시기",
            target_frequency=FrequencyConfig(
                type=FrequencyType.DAILY,
                count=6
            ),
            reminder_settings=ReminderConfig(
                enabled=True,
                times=["09:00", "13:00", "17:00"],
                message="물 마실 시간이에요!"
            ),
            priority=1
        )
        
        habit = await habit_service.create_user_habit(sample_user.id, habit_data)
        
        assert habit.custom_name == "나만의 물 마시기"
        assert habit.target_frequency_type == FrequencyType.DAILY
        assert habit.target_frequency_count == 6
        assert habit.reminder_enabled is True
        assert len(habit.reminder_times) == 3
        assert habit.current_streak == 0
        assert habit.is_active is True
    
    async def test_create_duplicate_user_habit(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """중복 사용자 습관 생성 테스트"""
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=1)
        )
        
        # 첫 번째 습관 생성
        await habit_service.create_user_habit(sample_user.id, habit_data)
        
        # 같은 템플릿으로 두 번째 습관 생성 시도
        with pytest.raises(ConflictError):
            await habit_service.create_user_habit(sample_user.id, habit_data)
    
    async def test_get_user_habits_with_filter(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """필터를 적용한 사용자 습관 조회 테스트"""
        # 습관 생성
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=1),
            priority=1
        )
        await habit_service.create_user_habit(sample_user.id, habit_data)
        
        # 우선순위 필터로 조회
        filter_params = UserHabitFilterParams(priority=1)
        habits = await habit_service.get_user_habits(sample_user.id, filter_params)
        
        assert len(habits) == 1
        assert habits[0].priority == 1
    
    async def test_get_user_habit_by_id(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """사용자 습관 ID로 조회 테스트"""
        # 습관 생성
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=1)
        )
        created_habit = await habit_service.create_user_habit(sample_user.id, habit_data)
        
        # ID로 조회
        habit = await habit_service.get_user_habit_by_id(sample_user.id, created_habit.id)
        
        assert habit is not None
        assert habit.id == created_habit.id
        assert habit.habit_template.name == "물 8잔 마시기"
    
    async def test_delete_user_habit(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """사용자 습관 삭제 테스트"""
        # 습관 생성
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=1)
        )
        created_habit = await habit_service.create_user_habit(sample_user.id, habit_data)
        
        # 습관 삭제
        success = await habit_service.delete_user_habit(sample_user.id, created_habit.id)
        assert success is True
        
        # 삭제 후 조회 - 비활성화된 상태로 변경
        habit = await habit_service.get_user_habit_by_id(sample_user.id, created_habit.id)
        assert habit is not None
        assert habit.is_active is False


class TestHabitLogService(TestHabitService):
    """습관 로그 서비스 테스트"""
    
    @pytest.fixture
    async def sample_user_habit(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """테스트용 사용자 습관 생성"""
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=1)
        )
        return await habit_service.create_user_habit(sample_user.id, habit_data)
    
    async def test_create_habit_log(self, habit_service: HabitService, sample_user: User, sample_user_habit: UserHabit):
        """습관 로그 생성 테스트"""
        log_data = HabitLogCreate(
            user_habit_id=sample_user_habit.id,
            completion_status=CompletionStatus.COMPLETED,
            completion_percentage=100,
            duration_minutes=5,
            intensity_level=3,
            mood_before=6,
            mood_after=8,
            energy_level=4,
            notes="물을 충분히 마셨어요!",
            location="집"
        )
        
        log = await habit_service.create_habit_log(sample_user.id, log_data)
        
        assert log.completion_status == CompletionStatus.COMPLETED
        assert log.completion_percentage == 100
        assert log.mood_after == 8
        assert log.notes == "물을 충분히 마셨어요!"
        assert log.points_earned > 0  # 포인트가 계산되었는지 확인
    
    async def test_create_partial_habit_log(self, habit_service: HabitService, sample_user: User, sample_user_habit: UserHabit):
        """부분 완료 습관 로그 생성 테스트"""
        log_data = HabitLogCreate(
            user_habit_id=sample_user_habit.id,
            completion_status=CompletionStatus.PARTIAL,
            completion_percentage=50,
            notes="절반만 완료"
        )
        
        log = await habit_service.create_habit_log(sample_user.id, log_data)
        
        assert log.completion_status == CompletionStatus.PARTIAL
        assert log.completion_percentage == 50
        assert log.points_earned > 0  # 부분 완료도 포인트 지급
        assert log.points_earned < 10  # 완료보다는 적은 포인트
    
    async def test_create_habit_log_invalid_habit(self, habit_service: HabitService, sample_user: User):
        """존재하지 않는 습관에 로그 생성 테스트"""
        invalid_habit_id = uuid4()
        log_data = HabitLogCreate(
            user_habit_id=invalid_habit_id,
            completion_status=CompletionStatus.COMPLETED
        )
        
        with pytest.raises(NotFoundError):
            await habit_service.create_habit_log(sample_user.id, log_data)
    
    async def test_get_habit_logs(self, habit_service: HabitService, sample_user: User, sample_user_habit: UserHabit):
        """습관 로그 목록 조회 테스트"""
        # 로그 여러 개 생성
        for i in range(3):
            log_data = HabitLogCreate(
                user_habit_id=sample_user_habit.id,
                completion_status=CompletionStatus.COMPLETED,
                notes=f"로그 {i+1}"
            )
            await habit_service.create_habit_log(sample_user.id, log_data)
        
        # 로그 조회
        logs = await habit_service.get_habit_logs(sample_user.id, limit=10)
        
        assert len(logs) == 3
        # 최신 순으로 정렬되는지 확인
        assert logs[0].notes == "로그 3"
        assert logs[2].notes == "로그 1"


class TestDashboardService(TestHabitService):
    """대시보드 서비스 테스트"""
    
    async def test_get_daily_dashboard_empty(self, habit_service: HabitService, sample_user: User):
        """빈 대시보드 데이터 조회 테스트"""
        today = date.today()
        dashboard = await habit_service.get_daily_dashboard(sample_user.id, today)
        
        assert dashboard.date == today.isoformat()
        assert dashboard.total_habits == 0
        assert dashboard.completed_habits == 0
        assert dashboard.overall_completion_rate == 0.0
        assert len(dashboard.habits) == 0
    
    async def test_get_daily_dashboard_with_habits(self, habit_service: HabitService, sample_user: User, sample_template: HabitTemplate):
        """습관이 있는 대시보드 데이터 조회 테스트"""
        # 사용자 습관 생성
        habit_data = UserHabitCreate(
            habit_template_id=sample_template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=2),
            reminder_settings=ReminderConfig(
                enabled=True,
                times=["09:00", "18:00"]
            )
        )
        user_habit = await habit_service.create_user_habit(sample_user.id, habit_data)
        
        # 로그 하나 생성 (2개 중 1개 완료)
        log_data = HabitLogCreate(
            user_habit_id=user_habit.id,
            completion_status=CompletionStatus.COMPLETED,
            mood_after=8,
            energy_level=4
        )
        await habit_service.create_habit_log(sample_user.id, log_data)
        
        # 대시보드 조회
        today = date.today()
        dashboard = await habit_service.get_daily_dashboard(sample_user.id, today)
        
        assert dashboard.total_habits == 1
        assert dashboard.in_progress_habits == 1  # 1/2 완료 상태
        assert dashboard.completed_habits == 0    # 목표 미달성
        assert 0 < dashboard.overall_completion_rate < 1  # 부분 완료
        assert dashboard.mood_average == 8.0
        assert dashboard.energy_average == 4.0
        assert dashboard.total_points_today > 0
        
        # 개별 습관 상태 확인
        habit_status = dashboard.habits[0]
        assert habit_status.habit_name == "물 8잔 마시기"
        assert habit_status.target_count == 2
        assert habit_status.completed_count == 1
        assert habit_status.completion_rate == 0.5
        assert habit_status.status == "in_progress"


@pytest.mark.asyncio
class TestHabitServiceIntegration:
    """습관 서비스 통합 테스트"""
    
    async def test_complete_habit_workflow(self, db_session: AsyncSession):
        """완전한 습관 워크플로우 테스트"""
        habit_service = HabitService(db_session)
        
        # 1. 사용자 생성
        user = User(
            email="workflow@example.com",
            nickname="워크플로우사용자",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 2. 카테고리 생성
        category_data = HabitCategoryCreate(
            name="건강",
            description="건강 관리 습관",
            icon="🏥",
            color_code="#007AFF"
        )
        category = await habit_service.create_category(category_data)
        
        # 3. 템플릿 생성
        template_data = HabitTemplateCreate(
            name="일일 운동",
            description="매일 30분 운동하기",
            category_id=category.id,
            difficulty_level=DifficultyLevel.MODERATE,
            estimated_time_minutes=30,
            recommended_frequency_type=FrequencyType.DAILY,
            recommended_frequency_count=1
        )
        template = await habit_service.create_habit_template(template_data)
        
        # 4. 사용자 습관 생성
        habit_data = UserHabitCreate(
            habit_template_id=template.id,
            target_frequency=FrequencyConfig(type=FrequencyType.DAILY, count=1),
            reminder_settings=ReminderConfig(enabled=True, times=["07:00"])
        )
        user_habit = await habit_service.create_user_habit(user.id, habit_data)
        
        # 5. 습관 실행 로그 생성 (3일간)
        for day_offset in range(3):
            log_date = datetime.now() - timedelta(days=day_offset)
            log_data = HabitLogCreate(
                user_habit_id=user_habit.id,
                completion_status=CompletionStatus.COMPLETED,
                logged_at=log_date,
                mood_after=7 + day_offset,  # 7, 8, 9
                energy_level=4
            )
            await habit_service.create_habit_log(user.id, log_data)
        
        # 6. 대시보드 조회 및 검증
        today = date.today()
        dashboard = await habit_service.get_daily_dashboard(user.id, today)
        
        assert dashboard.total_habits == 1
        assert dashboard.completed_habits == 1  # 오늘 완료됨
        assert dashboard.overall_completion_rate == 1.0
        
        # 7. 로그 조회 및 검증
        logs = await habit_service.get_habit_logs(user.id, limit=5)
        assert len(logs) == 3
        
        # 8. 사용자 습관 조회 및 스트릭 확인
        updated_habit = await habit_service.get_user_habit_by_id(user.id, user_habit.id)
        assert updated_habit.current_streak >= 1  # 스트릭이 계산되었는지 확인
        assert updated_habit.total_completions == 3
        assert updated_habit.reward_points > 0
