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
import random
import logging

from app.models.habit import (
    HabitCategory, HabitTemplate, UserHabit, HabitLog, HabitStreak,
    FrequencyType, CompletionStatus, DifficultyLevel
)
from app.models.user import User
from app.schemas.habit import (
    HabitCategoryCreate, HabitCategoryUpdate,
    HabitTemplateCreate, HabitTemplateUpdate, HabitTemplateSearchParams,
    UserHabitCreate, UserHabitUpdate, UserHabitFilterParams,
    HabitLogCreate, HabitLogUpdate,
    HabitProgress, DailyHabitStatus, DashboardData
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError

logger = logging.getLogger(__name__)

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
            log_data: 로그 생성 데이터
            
        Returns:
            HabitLog: 생성된 로그
            
        Raises:
            NotFoundError: 습관을 찾을 수 없는 경우
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
            
            # 자동 축하 알림 발송 (비동기)
            try:
                from app.services.notification_service import NotificationService
                notification_service = NotificationService(self.db)
                
                # 새로운 스트릭 계산
                new_streak = await self._calculate_streak(habit.id, log.logged_at.date())
                habit_name = habit.custom_name or habit.habit_template.name
                
                # 축하 알림 발송 (백그라운드)
                import asyncio
                asyncio.create_task(
                    notification_service.send_habit_completion_celebration(
                        user_id, habit_name, new_streak
                    )
                )
            except Exception as e:
                # 알림 실패해도 로그 생성은 계속 진행
                logger.warning(f"축하 알림 발송 실패: {str(e)}")
        
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

    # =================================================================
    # 습관 추천 엔진
    # =================================================================

    async def recommend_habits_for_user(self, user: User, limit: int = 5) -> List[HabitTemplate]:
        """
        사용자 맞춤 습관 추천
        
        Args:
            user: 사용자 객체
            limit: 추천할 습관 개수
            
        Returns:
            List[HabitTemplate]: 추천 습관 템플릿 목록
        """
        # 1. 이미 등록된 습관 템플릿 ID 수집
        user_habits = await self.get_user_habits(user.id)
        existing_template_ids = {habit.habit_template_id for habit in user_habits}
        
        # 2. 사용자 웰니스 프로필 기반 필터링
        candidates = await self._get_recommendation_candidates(user, existing_template_ids)
        
        # 3. 추천 점수 계산 및 정렬
        scored_habits = []
        for template in candidates:
            score = await self._calculate_recommendation_score(user, template, user_habits)
            scored_habits.append((template, score))
        
        # 점수 순으로 정렬
        scored_habits.sort(key=lambda x: x[1], reverse=True)
        
        # 4. 상위 추천 습관 반환 (다양성 고려)
        recommendations = self._diversify_recommendations(scored_habits, limit)
        
        return recommendations

    async def _get_recommendation_candidates(
        self, 
        user: User, 
        existing_template_ids: set
    ) -> List[HabitTemplate]:
        """추천 후보 습관 템플릿 조회"""
        stmt = select(HabitTemplate).options(
            joinedload(HabitTemplate.category)
        ).where(
            and_(
                HabitTemplate.is_active == True,
                ~HabitTemplate.id.in_(existing_template_ids)
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def _calculate_recommendation_score(
        self, 
        user: User, 
        template: HabitTemplate, 
        user_habits: List[UserHabit]
    ) -> float:
        """
        습관 추천 점수 계산
        
        점수 구성 요소:
        - 사용자 목표 일치도 (30%)
        - 난이도 적합성 (25%)
        - 시간 가용성 (20%)
        - 카테고리 균형 (15%)
        - 인기도/추천도 (10%)
        """
        score = 0.0
        
        # 1. 사용자 목표 일치도 (30점)
        goal_score = self._calculate_goal_alignment_score(user, template)
        score += goal_score * 0.3
        
        # 2. 난이도 적합성 (25점)
        difficulty_score = self._calculate_difficulty_score(user, template, user_habits)
        score += difficulty_score * 0.25
        
        # 3. 시간 가용성 (20점)
        time_score = self._calculate_time_compatibility_score(user, template)
        score += time_score * 0.2
        
        # 4. 카테고리 균형 (15점)
        balance_score = self._calculate_category_balance_score(template, user_habits)
        score += balance_score * 0.15
        
        # 5. 인기도/추천도 (10점)
        popularity_score = self._calculate_popularity_score(template)
        score += popularity_score * 0.1
        
        return min(score, 100.0)  # 최대 100점

    def _calculate_goal_alignment_score(self, user: User, template: HabitTemplate) -> float:
        """사용자 목표와 습관의 일치도 점수"""
        # 웰니스 프로필이 없으면 기본 점수
        if not hasattr(user, 'wellness_profile') or not user.wellness_profile:
            return 50.0
        
        # 사용자 목표와 습관 카테고리 매칭
        user_goals = getattr(user.wellness_profile, 'primary_goals', [])
        if not user_goals:
            return 50.0
        
        # 카테고리별 목표 매핑 (간단한 예시)
        category_goal_mapping = {
            '운동': ['체중관리', '근력증진', '체력향상'],
            '영양': ['체중관리', '건강관리', '에너지증진'],
            '정신건강': ['스트레스관리', '수면개선', '집중력향상'],
            '수면': ['수면개선', '스트레스관리'],
            '생산성': ['집중력향상', '시간관리']
        }
        
        category_name = template.category.name if template.category else ''
        category_goals = category_goal_mapping.get(category_name, [])
        
        # 목표 일치 개수에 따른 점수
        matches = len(set(user_goals) & set(category_goals))
        if matches >= 2:
            return 90.0
        elif matches == 1:
            return 70.0
        else:
            return 30.0

    def _calculate_difficulty_score(
        self, 
        user: User, 
        template: HabitTemplate, 
        user_habits: List[UserHabit]
    ) -> float:
        """난이도 적합성 점수"""
        # 사용자의 현재 습관 개수에 따른 적정 난이도
        habit_count = len([h for h in user_habits if h.is_active])
        
        if habit_count == 0:  # 초보자
            ideal_difficulty = DifficultyLevel.EASY
        elif habit_count <= 3:  # 중급자
            ideal_difficulty = DifficultyLevel.MODERATE
        else:  # 고급자
            ideal_difficulty = DifficultyLevel.HARD
        
        # 난이도 차이에 따른 점수
        difficulty_diff = abs(template.difficulty_level.value - ideal_difficulty.value)
        
        if difficulty_diff == 0:
            return 100.0
        elif difficulty_diff == 1:
            return 70.0
        else:
            return 40.0

    def _calculate_time_compatibility_score(self, user: User, template: HabitTemplate) -> float:
        """시간 가용성 점수"""
        # 웰니스 프로필의 가용 시간대 정보 활용
        if not hasattr(user, 'wellness_profile') or not user.wellness_profile:
            return 60.0
        
        # 간단한 시간 호환성 계산 (실제로는 더 복잡한 로직 필요)
        estimated_time = template.estimated_time_minutes
        
        if estimated_time <= 15:  # 15분 이하
            return 90.0
        elif estimated_time <= 30:  # 30분 이하
            return 75.0
        elif estimated_time <= 60:  # 1시간 이하
            return 60.0
        else:
            return 40.0

    def _calculate_category_balance_score(
        self, 
        template: HabitTemplate, 
        user_habits: List[UserHabit]
    ) -> float:
        """카테고리 균형 점수 (다양성 장려)"""
        if not user_habits:
            return 80.0
        
        # 현재 사용자가 가진 카테고리들
        existing_categories = {habit.habit_template.category_id for habit in user_habits}
        
        # 새로운 카테고리면 높은 점수
        if template.category_id not in existing_categories:
            return 90.0
        else:
            # 이미 있는 카테고리면 낮은 점수
            return 40.0

    def _calculate_popularity_score(self, template: HabitTemplate) -> float:
        """인기도/추천도 점수"""
        # 추천 템플릿이면 높은 점수
        if template.is_featured:
            return 90.0
        
        # 사용량에 따른 점수
        usage_count = template.usage_count
        if usage_count >= 100:
            return 80.0
        elif usage_count >= 50:
            return 70.0
        elif usage_count >= 10:
            return 60.0
        else:
            return 50.0

    def _diversify_recommendations(
        self, 
        scored_habits: List[Tuple[HabitTemplate, float]], 
        limit: int
    ) -> List[HabitTemplate]:
        """추천 결과 다양성 보장"""
        if len(scored_habits) <= limit:
            return [habit for habit, _ in scored_habits]
        
        recommendations = []
        used_categories = set()
        
        # 1차: 카테고리별로 최고 점수 1개씩
        for habit, score in scored_habits:
            if len(recommendations) >= limit:
                break
            
            category_id = habit.category_id
            if category_id not in used_categories:
                recommendations.append(habit)
                used_categories.add(category_id)
        
        # 2차: 남은 자리를 점수 순으로 채움
        for habit, score in scored_habits:
            if len(recommendations) >= limit:
                break
            
            if habit not in recommendations:
                recommendations.append(habit)
        
        return recommendations[:limit]

    # =================================================================
    # AI 코칭 메시지
    # =================================================================

    async def get_ai_coaching_message(
        self, 
        user_habit_id: UUID, 
        context: str = "general"
    ) -> Optional[str]:
        """
        습관별 AI 코칭 메시지 제공
        
        Args:
            user_habit_id: 사용자 습관 ID
            context: 메시지 컨텍스트 (general, motivation, tip, reminder)
            
        Returns:
            Optional[str]: AI 코칭 메시지
        """
        # 사용자 습관 조회
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(UserHabit.id == user_habit_id)
        
        result = await self.db.execute(stmt)
        user_habit = result.scalar_one_or_none()
        
        if not user_habit or not user_habit.habit_template:
            return None
        
        # 템플릿의 AI 코칭 프롬프트에서 랜덤 선택
        ai_prompts = user_habit.habit_template.ai_coaching_prompts
        if not ai_prompts:
            return self._get_default_coaching_message(context)
        
        # 컨텍스트별 필터링 (간단한 키워드 매칭)
        context_prompts = []
        for prompt in ai_prompts:
            if context == "motivation" and any(word in prompt.lower() for word in ["동기", "격려", "화이팅", "할 수 있어"]):
                context_prompts.append(prompt)
            elif context == "tip" and any(word in prompt.lower() for word in ["팁", "방법", "어떻게", "효과적"]):
                context_prompts.append(prompt)
            elif context == "reminder" and any(word in prompt.lower() for word in ["시간", "잊지", "기억", "알림"]):
                context_prompts.append(prompt)
            else:
                context_prompts.append(prompt)
        
        # 적절한 메시지가 없으면 전체에서 랜덤 선택
        if not context_prompts:
            context_prompts = ai_prompts
        
        return random.choice(context_prompts)

    def _get_default_coaching_message(self, context: str) -> str:
        """기본 코칭 메시지"""
        default_messages = {
            "general": [
                "오늘도 좋은 습관을 실천해보세요! 💪",
                "작은 변화가 큰 결과를 만듭니다! ✨",
                "꾸준함이 가장 큰 힘입니다! 🌟"
            ],
            "motivation": [
                "당신은 할 수 있습니다! 화이팅! 🔥",
                "매일 조금씩 발전하고 있어요! 👏",
                "포기하지 마세요, 거의 다 왔어요! 🎯"
            ],
            "tip": [
                "작은 목표부터 시작해보세요! 📝",
                "같은 시간에 하면 습관이 더 쉽게 만들어져요! ⏰",
                "완벽하지 않아도 괜찮아요, 시작이 중요해요! 🌱"
            ],
            "reminder": [
                "습관 실천 시간이에요! ⏰",
                "오늘의 목표를 잊지 마세요! 📋",
                "지금이 바로 그 시간입니다! ✨"
            ]
        }
        
        messages = default_messages.get(context, default_messages["general"])
        return random.choice(messages)

    # =================================================================
    # 고급 통계 및 분석
    # =================================================================

    async def get_habit_statistics_summary(self, user_id: UUID) -> Dict[str, Any]:
        """
        사용자 습관 통계 요약
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict: 통계 요약 데이터
        """
        # 기본 통계
        user_habits = await self.get_user_habits(user_id)
        active_habits = [h for h in user_habits if h.is_active]
        
        # 전체 완료율 계산
        total_completions = sum(h.total_completions for h in active_habits)
        total_possible = len(active_habits) * 30  # 30일 기준
        overall_completion_rate = (total_completions / total_possible * 100) if total_possible > 0 else 0
        
        # 최고 스트릭
        best_streak = max((h.longest_streak for h in active_habits), default=0)
        
        # 현재 활성 스트릭
        current_streaks = [h.current_streak for h in active_habits if h.current_streak > 0]
        active_streaks_count = len(current_streaks)
        
        # 카테고리별 분포
        category_stats = await self._get_category_distribution(user_id)
        
        # 주간 트렌드
        weekly_trend = await self._get_weekly_completion_trend(user_id)
        
        # 시간대별 활동
        time_distribution = await self._get_time_distribution(user_id)
        
        return {
            "summary": {
                "total_habits": len(user_habits),
                "active_habits": len(active_habits),
                "overall_completion_rate": round(overall_completion_rate, 1),
                "total_completions": total_completions,
                "best_streak": best_streak,
                "active_streaks": active_streaks_count,
                "total_points": sum(h.reward_points for h in active_habits)
            },
            "category_distribution": category_stats,
            "weekly_trend": weekly_trend,
            "time_distribution": time_distribution,
            "insights": await self._generate_insights(user_id, active_habits)
        }

    async def _get_category_distribution(self, user_id: UUID) -> List[Dict[str, Any]]:
        """카테고리별 습관 분포"""
        stmt = select(
            HabitCategory.name,
            func.count(UserHabit.id).label('habit_count'),
            func.avg(UserHabit.total_completions).label('avg_completions'),
            func.sum(UserHabit.reward_points).label('total_points')
        ).select_from(
            UserHabit
        ).join(
            HabitTemplate, UserHabit.habit_template_id == HabitTemplate.id
        ).join(
            HabitCategory, HabitTemplate.category_id == HabitCategory.id
        ).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.is_active == True
            )
        ).group_by(HabitCategory.name)
        
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        
        return [
            {
                "category": row.name,
                "habit_count": row.habit_count,
                "avg_completions": round(float(row.avg_completions or 0), 1),
                "total_points": int(row.total_points or 0)
            }
            for row in rows
        ]

    async def _get_weekly_completion_trend(self, user_id: UUID) -> List[Dict[str, Any]]:
        """주간 완료율 트렌드 (최근 4주)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=4)
        
        weekly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            # 해당 주의 완료 로그 조회
            stmt = select(
                func.count(HabitLog.id).label('completions'),
                func.count(func.distinct(HabitLog.user_habit_id)).label('active_habits')
            ).select_from(
                HabitLog
            ).join(
                UserHabit, HabitLog.user_habit_id == UserHabit.id
            ).where(
                and_(
                    UserHabit.user_id == user_id,
                    HabitLog.completion_status == CompletionStatus.COMPLETED,
                    func.date(HabitLog.logged_at) >= current_date,
                    func.date(HabitLog.logged_at) <= week_end
                )
            )
            
            result = await self.db.execute(stmt)
            row = result.fetchone()
            
            weekly_data.append({
                "week_start": current_date.isoformat(),
                "week_end": week_end.isoformat(),
                "completions": row.completions or 0,
                "active_habits": row.active_habits or 0,
                "completion_rate": round((row.completions or 0) / max((row.active_habits or 1) * 7, 1) * 100, 1)
            })
            
            current_date = week_end + timedelta(days=1)
        
        return weekly_data

    async def _get_time_distribution(self, user_id: UUID) -> Dict[str, int]:
        """시간대별 습관 실행 분포"""
        stmt = select(
            func.extract('hour', HabitLog.logged_at).label('hour'),
            func.count(HabitLog.id).label('count')
        ).select_from(
            HabitLog
        ).join(
            UserHabit, HabitLog.user_habit_id == UserHabit.id
        ).where(
            and_(
                UserHabit.user_id == user_id,
                HabitLog.completion_status == CompletionStatus.COMPLETED,
                HabitLog.logged_at >= datetime.now() - timedelta(days=30)  # 최근 30일
            )
        ).group_by(
            func.extract('hour', HabitLog.logged_at)
        )
        
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        
        # 시간대별 분류
        time_slots = {
            "morning": 0,    # 6-12시
            "afternoon": 0,  # 12-18시
            "evening": 0,    # 18-22시
            "night": 0       # 22-6시
        }
        
        for row in rows:
            hour = int(row.hour)
            count = row.count
            
            if 6 <= hour < 12:
                time_slots["morning"] += count
            elif 12 <= hour < 18:
                time_slots["afternoon"] += count
            elif 18 <= hour < 22:
                time_slots["evening"] += count
            else:
                time_slots["night"] += count
        
        return time_slots

    async def _generate_insights(self, user_id: UUID, active_habits: List[UserHabit]) -> List[str]:
        """AI 기반 인사이트 생성"""
        insights = []
        
        if not active_habits:
            insights.append("아직 활성 습관이 없습니다. 새로운 습관을 시작해보세요! 🌱")
            return insights
        
        # 스트릭 관련 인사이트
        best_habit = max(active_habits, key=lambda h: h.current_streak)
        if best_habit.current_streak >= 7:
            insights.append(f"🔥 '{best_habit.custom_name or best_habit.habit_template.name}' 습관이 {best_habit.current_streak}일 연속 달성 중입니다! 대단해요!")
        
        # 완료율 관련 인사이트
        avg_completion_rate = sum(h.total_completions for h in active_habits) / len(active_habits)
        if avg_completion_rate >= 20:
            insights.append("💪 전반적으로 습관 실천을 잘 하고 계시네요! 꾸준함이 빛나고 있어요.")
        elif avg_completion_rate < 5:
            insights.append("🌱 습관 형성 초기 단계입니다. 작은 목표부터 차근차근 시작해보세요!")
        
        # 카테고리 다양성 인사이트
        categories = set(h.habit_template.category_id for h in active_habits)
        if len(categories) >= 3:
            insights.append("🌈 다양한 영역의 습관을 균형있게 실천하고 계시네요!")
        elif len(categories) == 1:
            insights.append("💡 현재 한 분야에 집중하고 계시네요. 다른 영역의 습관도 고려해보세요!")
        
        # 포인트 관련 인사이트
        total_points = sum(h.reward_points for h in active_habits)
        if total_points >= 1000:
            insights.append(f"🏆 총 {total_points}포인트를 획득하셨습니다! 정말 대단한 성과예요!")
        
        return insights[:3]  # 최대 3개 인사이트
