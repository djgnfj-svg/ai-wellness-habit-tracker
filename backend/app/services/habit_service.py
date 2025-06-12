"""
습관 관리 서비스
습관 카테고리, 템플릿, 사용자 습관, 로그 관리를 담당합니다.

주요 기능:
- 습관 카테고리 관리
- 습관 템플릿 관리 및 추천
- 사용자별 습관 CRUD
- 습관 실행 로그 관리
- 진척도 분석 및 통계
- 스트릭 계산 및 관리
"""
from typing import Optional, List, Dict, Tuple, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload, joinedload

from app.models.habit import (
    HabitCategory, HabitTemplate, UserHabit, HabitLog, HabitStreak,
    FrequencyType, CompletionStatus, DifficultyLevel
)
from app.schemas.habit import (
    HabitCategoryCreate, HabitCategoryUpdate,
    HabitTemplateCreate, HabitTemplateUpdate, HabitTemplateSearchParams,
    UserHabitCreate, UserHabitUpdate, UserHabitFilterParams,
    HabitLogCreate, HabitLogUpdate,
    HabitProgress, DailyHabitStatus, DashboardData
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError


class HabitService:
    """
    습관 관리 서비스 클래스
    
    습관과 관련된 모든 비즈니스 로직을 처리합니다.
    카테고리, 템플릿, 사용자 습관, 로그 관리를 담당하며,
    진척도 분석과 스트릭 계산 등의 고급 기능도 제공합니다.
    
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
    # 습관 카테고리 관리
    # =================================================================

    async def get_categories(self, include_inactive: bool = False) -> List[HabitCategory]:
        """
        습관 카테고리 목록 조회 (계층 구조 포함)
        
        Args:
            include_inactive: 비활성 카테고리 포함 여부
            
        Returns:
            List[HabitCategory]: 카테고리 목록 (부모-자식 관계 포함)
        """
        stmt = select(HabitCategory).options(
            selectinload(HabitCategory.subcategories)
        ).where(HabitCategory.parent_category_id.is_(None))
        
        if not include_inactive:
            stmt = stmt.where(HabitCategory.is_active == True)
        
        stmt = stmt.order_by(HabitCategory.sort_order, HabitCategory.name)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: UUID) -> Optional[HabitCategory]:
        """카테고리 ID로 조회"""
        stmt = select(HabitCategory).options(
            selectinload(HabitCategory.subcategories),
            selectinload(HabitCategory.parent_category)
        ).where(HabitCategory.id == category_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_category(self, category_data: HabitCategoryCreate) -> HabitCategory:
        """
        새로운 습관 카테고리 생성
        
        Args:
            category_data: 카테고리 생성 데이터
            
        Returns:
            HabitCategory: 생성된 카테고리
            
        Raises:
            ConflictError: 동일한 이름의 카테고리가 이미 존재하는 경우
            ValidationError: 부모 카테고리가 존재하지 않는 경우
        """
        # 이름 중복 검사
        stmt = select(HabitCategory).where(HabitCategory.name == category_data.name)
        existing = await self.db.execute(stmt)
        if existing.scalar_one_or_none():
            raise ConflictError(f"'{category_data.name}' 카테고리가 이미 존재합니다")
        
        # 부모 카테고리 존재 확인
        if category_data.parent_category_id:
            parent = await self.get_category_by_id(category_data.parent_category_id)
            if not parent:
                raise ValidationError("존재하지 않는 부모 카테고리입니다")
        
        category = HabitCategory(**category_data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    # =================================================================
    # 습관 템플릿 관리
    # =================================================================

    async def get_habit_templates(
        self, 
        search_params: HabitTemplateSearchParams
    ) -> Tuple[List[HabitTemplate], int]:
        """
        습관 템플릿 검색 및 목록 조회
        
        Args:
            search_params: 검색 조건
            
        Returns:
            Tuple[List[HabitTemplate], int]: (템플릿 목록, 전체 개수)
        """
        # 기본 쿼리
        stmt = select(HabitTemplate).options(
            joinedload(HabitTemplate.category)
        ).where(HabitTemplate.is_active == True)
        
        count_stmt = select(func.count(HabitTemplate.id)).where(HabitTemplate.is_active == True)
        
        # 필터 적용
        if search_params.category_id:
            stmt = stmt.where(HabitTemplate.category_id == search_params.category_id)
            count_stmt = count_stmt.where(HabitTemplate.category_id == search_params.category_id)
        
        if search_params.difficulty_level:
            stmt = stmt.where(HabitTemplate.difficulty_level == search_params.difficulty_level)
            count_stmt = count_stmt.where(HabitTemplate.difficulty_level == search_params.difficulty_level)
        
        if search_params.max_time_minutes:
            stmt = stmt.where(HabitTemplate.estimated_time_minutes <= search_params.max_time_minutes)
            count_stmt = count_stmt.where(HabitTemplate.estimated_time_minutes <= search_params.max_time_minutes)
        
        if search_params.frequency_type:
            stmt = stmt.where(HabitTemplate.recommended_frequency_type == search_params.frequency_type)
            count_stmt = count_stmt.where(HabitTemplate.recommended_frequency_type == search_params.frequency_type)
        
        if search_params.search:
            search_term = f"%{search_params.search}%"
            stmt = stmt.where(or_(
                HabitTemplate.name.ilike(search_term),
                HabitTemplate.description.ilike(search_term)
            ))
            count_stmt = count_stmt.where(or_(
                HabitTemplate.name.ilike(search_term),
                HabitTemplate.description.ilike(search_term)
            ))
        
        if search_params.is_featured is not None:
            stmt = stmt.where(HabitTemplate.is_featured == search_params.is_featured)
            count_stmt = count_stmt.where(HabitTemplate.is_featured == search_params.is_featured)
        
        # 정렬 (추천 템플릿 우선, 사용량 순)
        stmt = stmt.order_by(
            desc(HabitTemplate.is_featured),
            desc(HabitTemplate.usage_count),
            HabitTemplate.name
        )
        
        # 페이징
        offset = (search_params.page - 1) * search_params.limit
        stmt = stmt.offset(offset).limit(search_params.limit)
        
        # 실행
        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)
        
        templates = result.scalars().all()
        total_count = count_result.scalar()
        
        return templates, total_count

    async def get_habit_template_by_id(self, template_id: UUID) -> Optional[HabitTemplate]:
        """습관 템플릿 ID로 조회"""
        stmt = select(HabitTemplate).options(
            joinedload(HabitTemplate.category)
        ).where(HabitTemplate.id == template_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_habit_template(self, template_data: HabitTemplateCreate) -> HabitTemplate:
        """
        새로운 습관 템플릿 생성
        
        Args:
            template_data: 템플릿 생성 데이터
            
        Returns:
            HabitTemplate: 생성된 템플릿
        """
        # 카테고리 존재 확인
        category = await self.get_category_by_id(template_data.category_id)
        if not category:
            raise ValidationError("존재하지 않는 카테고리입니다")
        
        template = HabitTemplate(**template_data.model_dump())
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    # =================================================================
    # 사용자 습관 관리
    # =================================================================

    async def get_user_habits(
        self, 
        user_id: UUID, 
        filter_params: Optional[UserHabitFilterParams] = None
    ) -> List[UserHabit]:
        """
        사용자의 습관 목록 조회
        
        Args:
            user_id: 사용자 ID
            filter_params: 필터 조건
            
        Returns:
            List[UserHabit]: 사용자 습관 목록
        """
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template).joinedload(HabitTemplate.category)
        ).where(UserHabit.user_id == user_id)
        
        if filter_params:
            if filter_params.category_id:
                stmt = stmt.join(HabitTemplate).where(
                    HabitTemplate.category_id == filter_params.category_id
                )
            
            if filter_params.is_active is not None:
                stmt = stmt.where(UserHabit.is_active == filter_params.is_active)
            
            if filter_params.priority:
                stmt = stmt.where(UserHabit.priority == filter_params.priority)
            
            if filter_params.has_reminder is not None:
                stmt = stmt.where(UserHabit.reminder_enabled == filter_params.has_reminder)
        
        # 우선순위 순 정렬
        stmt = stmt.order_by(UserHabit.priority, UserHabit.created_at)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user_habit_by_id(self, user_id: UUID, habit_id: UUID) -> Optional[UserHabit]:
        """사용자 습관 ID로 조회"""
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template).joinedload(HabitTemplate.category)
        ).where(
            and_(UserHabit.id == habit_id, UserHabit.user_id == user_id)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user_habit(self, user_id: UUID, habit_data: UserHabitCreate) -> UserHabit:
        """
        사용자 습관 생성
        
        Args:
            user_id: 사용자 ID
            habit_data: 습관 생성 데이터
            
        Returns:
            UserHabit: 생성된 사용자 습관
        """
        # 템플릿 존재 확인
        template = await self.get_habit_template_by_id(habit_data.habit_template_id)
        if not template:
            raise ValidationError("존재하지 않는 습관 템플릿입니다")
        
        # 중복 습관 확인 (같은 템플릿으로 활성 습관이 이미 있는지)
        existing_stmt = select(UserHabit).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.habit_template_id == habit_data.habit_template_id,
                UserHabit.is_active == True
            )
        )
        existing = await self.db.execute(existing_stmt)
        if existing.scalar_one_or_none():
            raise ConflictError("이미 동일한 습관이 활성화되어 있습니다")
        
        # 사용자 습관 생성
        user_habit = UserHabit(
            user_id=user_id,
            **habit_data.model_dump()
        )
        
        self.db.add(user_habit)
        
        # 템플릿 사용량 증가
        await self.db.execute(
            update(HabitTemplate)
            .where(HabitTemplate.id == habit_data.habit_template_id)
            .values(usage_count=HabitTemplate.usage_count + 1)
        )
        
        await self.db.commit()
        await self.db.refresh(user_habit)
        return user_habit

    async def update_user_habit(
        self, 
        user_id: UUID, 
        habit_id: UUID, 
        habit_update: UserHabitUpdate
    ) -> UserHabit:
        """사용자 습관 업데이트"""
        habit = await self.get_user_habit_by_id(user_id, habit_id)
        if not habit:
            raise NotFoundError("습관을 찾을 수 없습니다")
        
        update_data = habit_update.model_dump(exclude_unset=True)
        if not update_data:
            return habit
        
        await self.db.execute(
            update(UserHabit)
            .where(UserHabit.id == habit_id)
            .values(**update_data)
        )
        
        await self.db.commit()
        await self.db.refresh(habit)
        return habit

    async def delete_user_habit(self, user_id: UUID, habit_id: UUID) -> bool:
        """사용자 습관 삭제 (비활성화)"""
        habit = await self.get_user_habit_by_id(user_id, habit_id)
        if not habit:
            raise NotFoundError("습관을 찾을 수 없습니다")
        
        await self.db.execute(
            update(UserHabit)
            .where(UserHabit.id == habit_id)
            .values(is_active=False)
        )
        
        await self.db.commit()
        return True

    # =================================================================
    # 습관 실행 로그 관리
    # =================================================================

    async def create_habit_log(self, user_id: UUID, log_data: HabitLogCreate) -> HabitLog:
        """
        습관 실행 로그 생성
        
        Args:
            user_id: 사용자 ID
            log_data: 로그 데이터
            
        Returns:
            HabitLog: 생성된 로그
        """
        # 사용자 습관 확인
        habit = await self.get_user_habit_by_id(user_id, log_data.user_habit_id)
        if not habit:
            raise NotFoundError("습관을 찾을 수 없습니다")
        
        # 로그 생성
        log = HabitLog(
            **log_data.model_dump(exclude={'logged_at'}),
            logged_at=log_data.logged_at or datetime.utcnow()
        )
        
        # 포인트 계산
        points = self._calculate_points(log_data.completion_status, log_data.completion_percentage)
        log.points_earned = points
        
        self.db.add(log)
        
        # 습관 통계 업데이트
        if log_data.completion_status == CompletionStatus.COMPLETED:
            await self._update_habit_statistics(habit, log)
        
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_habit_logs(
        self, 
        user_id: UUID, 
        habit_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50
    ) -> List[HabitLog]:
        """습관 실행 로그 조회"""
        stmt = select(HabitLog).join(UserHabit).where(UserHabit.user_id == user_id)
        
        if habit_id:
            stmt = stmt.where(HabitLog.user_habit_id == habit_id)
        
        if start_date:
            stmt = stmt.where(func.date(HabitLog.logged_at) >= start_date)
        
        if end_date:
            stmt = stmt.where(func.date(HabitLog.logged_at) <= end_date)
        
        stmt = stmt.order_by(desc(HabitLog.logged_at)).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =================================================================
    # 진척도 및 대시보드 데이터
    # =================================================================

    async def get_daily_dashboard(self, user_id: UUID, target_date: date) -> DashboardData:
        """
        일일 대시보드 데이터 조회
        
        Args:
            user_id: 사용자 ID
            target_date: 조회할 날짜
            
        Returns:
            DashboardData: 대시보드 데이터
        """
        # 사용자의 활성 습관 조회
        user_habits = await self.get_user_habits(
            user_id, 
            UserHabitFilterParams(is_active=True)
        )
        
        if not user_habits:
            return DashboardData(
                date=target_date.isoformat(),
                overall_completion_rate=0.0,
                total_habits=0,
                completed_habits=0,
                in_progress_habits=0,
                pending_habits=0,
                habits=[],
                mood_average=None,
                energy_average=None,
                total_points_today=0
            )
        
        habit_statuses = []
        total_points = 0
        mood_values = []
        energy_values = []
        
        for habit in user_habits:
            # 해당 날짜의 로그 조회
            logs = await self._get_habit_logs_for_date(habit.id, target_date)
            
            # 목표 완료 횟수 계산
            target_count = self._calculate_daily_target(habit.target_frequency)
            completed_count = len([log for log in logs if log.completion_status == CompletionStatus.COMPLETED])
            
            # 상태 결정
            if completed_count >= target_count:
                status = "completed"
            elif completed_count > 0:
                status = "in_progress"
            elif any(log.completion_status == CompletionStatus.SKIPPED for log in logs):
                status = "skipped"
            else:
                status = "pending"
            
            # 다음 리마인더 시간 계산
            next_reminder = self._get_next_reminder_time(habit, completed_count, target_count)
            
            habit_status = DailyHabitStatus(
                date=target_date.isoformat(),
                user_habit_id=habit.id,
                habit_name=habit.custom_name or habit.habit_template.name,
                target_count=target_count,
                completed_count=completed_count,
                completion_rate=completed_count / target_count if target_count > 0 else 0.0,
                status=status,
                next_reminder=next_reminder,
                logs=logs
            )
            
            habit_statuses.append(habit_status)
            
            # 통계 누적
            total_points += sum(log.points_earned for log in logs)
            mood_values.extend([log.mood_after for log in logs if log.mood_after])
            energy_values.extend([log.energy_level for log in logs if log.energy_level])
        
        # 전체 완료율 계산
        completed_habits = len([h for h in habit_statuses if h.status == "completed"])
        in_progress_habits = len([h for h in habit_statuses if h.status == "in_progress"])
        pending_habits = len([h for h in habit_statuses if h.status == "pending"])
        
        overall_completion = sum(h.completion_rate for h in habit_statuses) / len(habit_statuses)
        
        return DashboardData(
            date=target_date.isoformat(),
            overall_completion_rate=overall_completion,
            total_habits=len(user_habits),
            completed_habits=completed_habits,
            in_progress_habits=in_progress_habits,
            pending_habits=pending_habits,
            habits=habit_statuses,
            mood_average=sum(mood_values) / len(mood_values) if mood_values else None,
            energy_average=sum(energy_values) / len(energy_values) if energy_values else None,
            total_points_today=total_points
        )

    # =================================================================
    # 유틸리티 메서드
    # =================================================================

    def _calculate_points(self, status: CompletionStatus, percentage: int) -> int:
        """포인트 계산"""
        if status == CompletionStatus.COMPLETED:
            return max(10, int(percentage / 10))  # 10-100 포인트
        elif status == CompletionStatus.PARTIAL:
            return max(5, int(percentage / 20))   # 5-50 포인트
        return 0

    async def _update_habit_statistics(self, habit: UserHabit, log: HabitLog):
        """습관 통계 업데이트"""
        # 총 완료 횟수 증가
        new_total = habit.total_completions + 1
        
        # 스트릭 계산
        new_streak = await self._calculate_streak(habit.id, log.logged_at.date())
        new_longest = max(habit.longest_streak, new_streak)
        
        # 포인트 추가
        new_points = habit.reward_points + log.points_earned
        
        await self.db.execute(
            update(UserHabit)
            .where(UserHabit.id == habit.id)
            .values(
                total_completions=new_total,
                current_streak=new_streak,
                longest_streak=new_longest,
                reward_points=new_points
            )
        )

    async def _calculate_streak(self, habit_id: UUID, log_date: date) -> int:
        """연속 달성 일수 계산"""
        stmt = select(func.date(HabitLog.logged_at)).join(UserHabit).where(
            and_(
                UserHabit.id == habit_id,
                HabitLog.completion_status == CompletionStatus.COMPLETED,
                func.date(HabitLog.logged_at) <= log_date
            )
        ).distinct().order_by(desc(func.date(HabitLog.logged_at)))
        
        result = await self.db.execute(stmt)
        completion_dates = [row[0] for row in result.fetchall()]
        
        if not completion_dates:
            return 1
        
        # 연속 날짜 확인
        streak = 1
        current_date = log_date
        
        for completion_date in completion_dates[1:]:  # 첫 번째는 오늘
            expected_date = current_date - timedelta(days=1)
            if completion_date == expected_date:
                streak += 1
                current_date = completion_date
            else:
                break
        
        return streak

    async def _get_habit_logs_for_date(self, habit_id: UUID, target_date: date) -> List[HabitLog]:
        """특정 날짜의 습관 로그 조회"""
        stmt = select(HabitLog).where(
            and_(
                HabitLog.user_habit_id == habit_id,
                func.date(HabitLog.logged_at) == target_date
            )
        ).order_by(HabitLog.logged_at)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    def _calculate_daily_target(self, frequency_config: dict) -> int:
        """일일 목표 횟수 계산"""
        freq_type = frequency_config.get("type", "daily")
        freq_count = frequency_config.get("count", 1)
        
        if freq_type == "daily":
            return freq_count
        elif freq_type == "weekly":
            return 1 if freq_count >= 7 else 0  # 주 7회 이상이면 매일 1회
        else:
            return 1  # 기본값

    def _get_next_reminder_time(self, habit: UserHabit, completed: int, target: int) -> Optional[str]:
        """다음 리마인더 시간 계산"""
        if completed >= target or not habit.reminder_enabled:
            return None
        
        reminder_times = habit.reminder_times or []
        if not reminder_times:
            return None
        
        now = datetime.now().time()
        
        # 오늘 남은 리마인더 시간 찾기
        for time_str in reminder_times:
            try:
                hour, minute = map(int, time_str.split(':'))
                reminder_time = datetime.now().replace(hour=hour, minute=minute, second=0).time()
                if reminder_time > now:
                    return time_str
            except ValueError:
                continue
        
        return None
