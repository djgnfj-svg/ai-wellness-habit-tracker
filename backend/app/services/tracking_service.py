"""
습관 추적 시스템 서비스

주요 기능:
- 자동 추적 (웨어러블 연동, GPS, 가속도계)
- 고도화된 스트릭 계산 및 예측
- 진척도 분석 및 패턴 인식
- 스마트 리마인더 타이밍 최적화
- 증거 파일 관리
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import joinedload
import statistics
import logging
from enum import Enum

from app.models.habit import (
    UserHabit, HabitLog, HabitEvidence, HabitStreak,
    CompletionStatus, FrequencyType
)
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    """증거 타입"""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    TIMER = "timer"
    GPS = "gps"
    SENSOR = "sensor"


class TimePeriod(str, Enum):
    """시간 기간"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ConsistencyPattern(str, Enum):
    """일관성 패턴"""
    VERY_CONSISTENT = "very_consistent"    # 매우 일관적
    CONSISTENT = "consistent"              # 일관적
    MODERATE = "moderate"                  # 보통
    INCONSISTENT = "inconsistent"          # 비일관적
    VERY_INCONSISTENT = "very_inconsistent" # 매우 비일관적


class AutoTrackingService:
    """
    자동 추적 서비스
    
    웨어러블 기기, GPS, 센서 데이터를 활용한 자동 습관 추적
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def integrate_health_data(self, user_id: UUID, health_data: Dict[str, Any]) -> bool:
        """
        헬스 데이터 통합 (Apple Health, Google Fit 등)
        
        Args:
            user_id: 사용자 ID
            health_data: 헬스 데이터
            
        Returns:
            bool: 통합 성공 여부
        """
        try:
            # 사용자의 활성 습관 중 자동 추적 가능한 것들 조회
            trackable_habits = await self._get_auto_trackable_habits(user_id)
            
            auto_logs = []
            for habit in trackable_habits:
                # 습관 유형에 따른 자동 감지
                if await self._detect_activity_completion(habit, health_data):
                    log_data = await self._create_auto_log(habit, health_data)
                    auto_logs.append(log_data)
            
            # 자동 로그 저장
            for log_data in auto_logs:
                await self._save_auto_log(log_data)
            
            logger.info(f"자동 추적 완료: 사용자 {user_id}, {len(auto_logs)}개 습관 감지")
            return True
            
        except Exception as e:
            logger.error(f"헬스 데이터 통합 실패: {str(e)}")
            return False

    async def detect_activity_completion(
        self, 
        user_id: UUID, 
        habit_id: UUID,
        sensor_data: Dict[str, Any]
    ) -> bool:
        """
        센서 데이터 기반 활동 완료 감지
        
        Args:
            user_id: 사용자 ID
            habit_id: 습관 ID
            sensor_data: 센서 데이터 (GPS, 가속도계 등)
            
        Returns:
            bool: 활동 완료 여부
        """
        # 습관 정보 조회
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(
            and_(
                UserHabit.id == habit_id,
                UserHabit.user_id == user_id
            )
        )
        
        result = await self.db.execute(stmt)
        habit = result.scalar_one_or_none()
        
        if not habit:
            return False
        
        return await self._detect_activity_completion(habit, sensor_data)

    async def smart_reminder_timing(self, user_habit: UserHabit) -> Optional[datetime]:
        """
        스마트 리마인더 타이밍 계산
        
        사용자의 과거 실행 패턴을 분석하여 최적의 리마인더 시간을 계산
        
        Args:
            user_habit: 사용자 습관
            
        Returns:
            Optional[datetime]: 최적 리마인더 시간
        """
        # 과거 30일간의 실행 로그 분석
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        stmt = select(HabitLog).where(
            and_(
                HabitLog.user_habit_id == user_habit.id,
                func.date(HabitLog.logged_at) >= start_date,
                func.date(HabitLog.logged_at) <= end_date,
                HabitLog.completion_status == CompletionStatus.COMPLETED
            )
        ).order_by(HabitLog.logged_at)
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            # 기본 리마인더 시간 반환
            return self._get_default_reminder_time(user_habit)
        
        # 실행 시간 패턴 분석
        execution_hours = [log.logged_at.hour for log in logs]
        
        # 가장 빈번한 실행 시간대 계산
        hour_counts = {}
        for hour in execution_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # 최빈 시간대 찾기
        optimal_hour = max(hour_counts, key=hour_counts.get)
        
        # 리마인더는 실행 시간 30분 전으로 설정
        reminder_hour = max(0, optimal_hour - 1)
        reminder_minute = 30 if optimal_hour > 0 else 0
        
        # 다음 리마인더 시간 계산
        now = datetime.now()
        reminder_time = now.replace(
            hour=reminder_hour,
            minute=reminder_minute,
            second=0,
            microsecond=0
        )
        
        # 이미 지난 시간이면 다음날로
        if reminder_time <= now:
            reminder_time += timedelta(days=1)
        
        return reminder_time

    async def _get_auto_trackable_habits(self, user_id: UUID) -> List[UserHabit]:
        """자동 추적 가능한 습관들 조회"""
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.is_active == True
            )
        )
        
        result = await self.db.execute(stmt)
        all_habits = result.scalars().all()
        
        # 자동 추적 가능한 습관 필터링 (운동, 수면, 걸음 수 등)
        trackable_categories = ['운동', '수면', '걷기', '달리기', '사이클링']
        trackable_habits = []
        
        for habit in all_habits:
            if habit.habit_template and habit.habit_template.category:
                category_name = habit.habit_template.category.name
                if any(cat in category_name for cat in trackable_categories):
                    trackable_habits.append(habit)
        
        return trackable_habits

    async def _detect_activity_completion(
        self, 
        habit: UserHabit, 
        data: Dict[str, Any]
    ) -> bool:
        """활동 완료 감지 로직"""
        category_name = habit.habit_template.category.name if habit.habit_template.category else ""
        
        # 운동 관련 습관
        if '운동' in category_name or '달리기' in category_name:
            # 운동 시간이 목표 시간 이상인지 확인
            workout_duration = data.get('workout_duration_minutes', 0)
            target_duration = habit.habit_template.estimated_time_minutes
            return workout_duration >= target_duration * 0.8  # 80% 이상 완료
        
        # 걸음 수 관련 습관
        elif '걷기' in category_name or '걸음' in category_name:
            steps = data.get('steps', 0)
            target_steps = data.get('target_steps', 8000)
            return steps >= target_steps
        
        # 수면 관련 습관
        elif '수면' in category_name:
            sleep_hours = data.get('sleep_hours', 0)
            target_sleep = 7.0  # 기본 목표 수면 시간
            return sleep_hours >= target_sleep * 0.9  # 90% 이상
        
        return False

    async def _create_auto_log(self, habit: UserHabit, data: Dict[str, Any]) -> Dict[str, Any]:
        """자동 로그 데이터 생성"""
        return {
            'user_habit_id': habit.id,
            'logged_at': datetime.now(),
            'completion_status': CompletionStatus.COMPLETED,
            'completion_percentage': 100,
            'duration_minutes': data.get('workout_duration_minutes'),
            'notes': f"자동 감지됨 - {data.get('source', 'Unknown')}",
            'auto_tracked': True
        }

    async def _save_auto_log(self, log_data: Dict[str, Any]):
        """자동 로그 저장"""
        # 실제 구현에서는 HabitService의 create_habit_log 메서드 활용
        pass

    def _get_default_reminder_time(self, user_habit: UserHabit) -> datetime:
        """기본 리마인더 시간"""
        now = datetime.now()
        # 기본적으로 오전 9시로 설정
        default_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        if default_time <= now:
            default_time += timedelta(days=1)
        
        return default_time


class StreakCalculator:
    """
    고도화된 스트릭 계산기
    
    연속 달성 일수 계산, 예측, 회복 제안 등
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_current_streak(self, user_habit_id: UUID) -> int:
        """
        현재 연속 달성 일수 계산
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            int: 현재 스트릭
        """
        # 최근 로그들을 날짜 역순으로 조회
        stmt = select(HabitLog).where(
            HabitLog.user_habit_id == user_habit_id
        ).order_by(desc(func.date(HabitLog.logged_at)))
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            return 0
        
        # 날짜별로 그룹화
        daily_completions = {}
        for log in logs:
            log_date = log.logged_at.date()
            if log_date not in daily_completions:
                daily_completions[log_date] = []
            daily_completions[log_date].append(log)
        
        # 연속 달성 일수 계산
        streak = 0
        current_date = datetime.now().date()
        
        while current_date in daily_completions:
            # 해당 날짜에 완료된 로그가 있는지 확인
            day_logs = daily_completions[current_date]
            completed = any(
                log.completion_status == CompletionStatus.COMPLETED 
                for log in day_logs
            )
            
            if completed:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak

    async def calculate_longest_streak(self, user_habit_id: UUID) -> int:
        """
        최장 연속 달성 기록 계산
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            int: 최장 스트릭
        """
        # 모든 로그 조회
        stmt = select(HabitLog).where(
            HabitLog.user_habit_id == user_habit_id
        ).order_by(func.date(HabitLog.logged_at))
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            return 0
        
        # 날짜별 완료 여부 계산
        daily_completions = {}
        for log in logs:
            log_date = log.logged_at.date()
            if log_date not in daily_completions:
                daily_completions[log_date] = False
            
            if log.completion_status == CompletionStatus.COMPLETED:
                daily_completions[log_date] = True
        
        # 최장 연속 기록 계산
        max_streak = 0
        current_streak = 0
        
        # 첫 번째 로그 날짜부터 오늘까지 순회
        start_date = min(daily_completions.keys())
        end_date = datetime.now().date()
        current_date = start_date
        
        while current_date <= end_date:
            if daily_completions.get(current_date, False):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
            
            current_date += timedelta(days=1)
        
        return max_streak

    async def predict_streak_risk(self, user_habit_id: UUID) -> float:
        """
        스트릭 중단 위험도 예측
        
        최근 실행 패턴, 완료율, 시간 간격 등을 분석하여 위험도 계산
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            float: 위험도 (0.0 ~ 1.0, 높을수록 위험)
        """
        # 최근 7일간의 로그 분석
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        stmt = select(HabitLog).where(
            and_(
                HabitLog.user_habit_id == user_habit_id,
                func.date(HabitLog.logged_at) >= start_date,
                func.date(HabitLog.logged_at) <= end_date
            )
        ).order_by(HabitLog.logged_at)
        
        result = await self.db.execute(stmt)
        recent_logs = result.scalars().all()
        
        if not recent_logs:
            return 0.8  # 로그가 없으면 높은 위험도
        
        # 위험 요소들 계산
        risk_factors = []
        
        # 1. 최근 완료율
        completed_count = sum(
            1 for log in recent_logs 
            if log.completion_status == CompletionStatus.COMPLETED
        )
        completion_rate = completed_count / 7  # 7일 기준
        risk_factors.append(1.0 - completion_rate)
        
        # 2. 마지막 완료 이후 경과 시간
        last_completion = None
        for log in reversed(recent_logs):
            if log.completion_status == CompletionStatus.COMPLETED:
                last_completion = log.logged_at.date()
                break
        
        if last_completion:
            days_since_completion = (end_date - last_completion).days
            time_risk = min(days_since_completion / 3.0, 1.0)  # 3일 이상이면 최대 위험
            risk_factors.append(time_risk)
        else:
            risk_factors.append(1.0)  # 최근에 완료한 적이 없음
        
        # 3. 완료 패턴의 일관성
        daily_completions = {}
        for log in recent_logs:
            log_date = log.logged_at.date()
            if log_date not in daily_completions:
                daily_completions[log_date] = False
            if log.completion_status == CompletionStatus.COMPLETED:
                daily_completions[log_date] = True
        
        # 연속성 체크
        consecutive_days = 0
        for i in range(7):
            check_date = end_date - timedelta(days=i)
            if daily_completions.get(check_date, False):
                consecutive_days += 1
            else:
                break
        
        consistency_risk = 1.0 - (consecutive_days / 7.0)
        risk_factors.append(consistency_risk)
        
        # 전체 위험도 계산 (평균)
        overall_risk = sum(risk_factors) / len(risk_factors)
        
        return min(max(overall_risk, 0.0), 1.0)

    async def get_streak_recovery_suggestions(self, user_habit_id: UUID) -> List[str]:
        """
        스트릭 회복을 위한 제안
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            List[str]: 회복 제안 목록
        """
        # 습관 정보 조회
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(UserHabit.id == user_habit_id)
        
        result = await self.db.execute(stmt)
        habit = result.scalar_one_or_none()
        
        if not habit:
            return []
        
        suggestions = []
        
        # 위험도에 따른 제안
        risk = await self.predict_streak_risk(user_habit_id)
        
        if risk > 0.7:  # 높은 위험
            suggestions.extend([
                "🚨 스트릭이 위험해요! 오늘 꼭 실천해보세요",
                "💡 목표를 절반으로 줄여서라도 실천해보세요",
                "⏰ 리마인더 시간을 조정해보는 것은 어떨까요?",
                "👥 가족이나 친구에게 도움을 요청해보세요"
            ])
        elif risk > 0.4:  # 중간 위험
            suggestions.extend([
                "⚠️ 스트릭 유지에 주의가 필요해요",
                "📅 내일 계획을 미리 세워보세요",
                "🎯 작은 목표부터 다시 시작해보세요"
            ])
        else:  # 낮은 위험
            suggestions.extend([
                "✨ 좋은 페이스를 유지하고 있어요!",
                "🔥 이 기세로 계속 이어가세요",
                "🏆 새로운 목표에 도전해보는 것은 어떨까요?"
            ])
        
        # 습관별 맞춤 제안
        if habit.habit_template and habit.habit_template.category:
            category_name = habit.habit_template.category.name
            
            if '운동' in category_name:
                suggestions.append("🏃‍♂️ 짧은 산책부터 시작해보세요")
            elif '독서' in category_name:
                suggestions.append("📖 한 페이지라도 읽어보세요")
            elif '명상' in category_name:
                suggestions.append("🧘‍♀️ 1분 호흡 명상부터 시작해보세요")
        
        return suggestions[:5]  # 최대 5개 제안


class ProgressAnalyzer:
    """
    진척도 분석기
    
    완료율, 일관성 패턴, 최적 타이밍, 난이도 조정 등을 분석
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_completion_rate(
        self, 
        user_habit_id: UUID, 
        period: TimePeriod
    ) -> float:
        """
        기간별 완료율 계산
        
        Args:
            user_habit_id: 사용자 습관 ID
            period: 분석 기간
            
        Returns:
            float: 완료율 (0.0 ~ 1.0)
        """
        end_date = datetime.now().date()
        
        # 기간별 시작 날짜 계산
        if period == TimePeriod.DAILY:
            start_date = end_date
            total_days = 1
        elif period == TimePeriod.WEEKLY:
            start_date = end_date - timedelta(days=7)
            total_days = 7
        elif period == TimePeriod.MONTHLY:
            start_date = end_date - timedelta(days=30)
            total_days = 30
        else:  # YEARLY
            start_date = end_date - timedelta(days=365)
            total_days = 365
        
        # 해당 기간의 로그 조회
        stmt = select(HabitLog).where(
            and_(
                HabitLog.user_habit_id == user_habit_id,
                func.date(HabitLog.logged_at) >= start_date,
                func.date(HabitLog.logged_at) <= end_date
            )
        )
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        # 날짜별 완료 여부 계산
        daily_completions = {}
        for log in logs:
            log_date = log.logged_at.date()
            if log_date not in daily_completions:
                daily_completions[log_date] = False
            
            if log.completion_status == CompletionStatus.COMPLETED:
                daily_completions[log_date] = True
        
        # 완료된 날짜 수 계산
        completed_days = sum(1 for completed in daily_completions.values() if completed)
        
        return completed_days / total_days if total_days > 0 else 0.0

    async def analyze_consistency_pattern(self, user_habit_id: UUID) -> ConsistencyPattern:
        """
        일관성 패턴 분석
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            ConsistencyPattern: 일관성 패턴
        """
        # 최근 30일간의 완료율 계산
        completion_rate = await self.calculate_completion_rate(
            user_habit_id, 
            TimePeriod.MONTHLY
        )
        
        # 일관성 점수 계산 (완료율 + 연속성)
        current_streak = await StreakCalculator(self.db).calculate_current_streak(user_habit_id)
        longest_streak = await StreakCalculator(self.db).calculate_longest_streak(user_habit_id)
        
        # 연속성 점수 (현재 스트릭 / 최장 스트릭)
        consistency_score = current_streak / max(longest_streak, 1)
        
        # 전체 일관성 점수 (완료율 70% + 연속성 30%)
        overall_consistency = (completion_rate * 0.7) + (consistency_score * 0.3)
        
        # 패턴 분류
        if overall_consistency >= 0.9:
            return ConsistencyPattern.VERY_CONSISTENT
        elif overall_consistency >= 0.7:
            return ConsistencyPattern.CONSISTENT
        elif overall_consistency >= 0.5:
            return ConsistencyPattern.MODERATE
        elif overall_consistency >= 0.3:
            return ConsistencyPattern.INCONSISTENT
        else:
            return ConsistencyPattern.VERY_INCONSISTENT

    async def identify_optimal_timing(self, user_habit_id: UUID) -> List[Tuple[int, int]]:
        """
        최적 실행 시간대 분석
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            List[Tuple[int, int]]: 최적 시간대 목록 [(시, 분), ...]
        """
        # 최근 60일간의 완료 로그 조회
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=60)
        
        stmt = select(HabitLog).where(
            and_(
                HabitLog.user_habit_id == user_habit_id,
                func.date(HabitLog.logged_at) >= start_date,
                func.date(HabitLog.logged_at) <= end_date,
                HabitLog.completion_status == CompletionStatus.COMPLETED
            )
        )
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            return [(9, 0)]  # 기본값: 오전 9시
        
        # 시간대별 완료 빈도 계산
        hour_counts = {}
        for log in logs:
            hour = log.logged_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # 상위 3개 시간대 반환
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        optimal_times = [(hour, 0) for hour, _ in sorted_hours[:3]]
        
        return optimal_times if optimal_times else [(9, 0)]

    async def calculate_difficulty_adjustment(self, user_habit_id: UUID) -> int:
        """
        난이도 조정 제안 계산
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            int: 조정 제안 (-2: 많이 쉽게, -1: 쉽게, 0: 유지, 1: 어렵게, 2: 많이 어렵게)
        """
        # 최근 2주간의 성과 분석
        completion_rate = await self.calculate_completion_rate(
            user_habit_id, 
            TimePeriod.WEEKLY
        )
        
        # 일관성 패턴 분석
        consistency = await self.analyze_consistency_pattern(user_habit_id)
        
        # 조정 로직
        if completion_rate >= 0.9 and consistency in [
            ConsistencyPattern.VERY_CONSISTENT, 
            ConsistencyPattern.CONSISTENT
        ]:
            return 1  # 어렵게 조정
        elif completion_rate >= 0.8 and consistency == ConsistencyPattern.VERY_CONSISTENT:
            return 2  # 많이 어렵게 조정
        elif completion_rate < 0.3 or consistency == ConsistencyPattern.VERY_INCONSISTENT:
            return -2  # 많이 쉽게 조정
        elif completion_rate < 0.5 or consistency == ConsistencyPattern.INCONSISTENT:
            return -1  # 쉽게 조정
        else:
            return 0  # 현재 난이도 유지


class TrackingService:
    """
    통합 추적 서비스
    
    자동 추적, 스트릭 계산, 진척도 분석을 통합 관리
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auto_tracking = AutoTrackingService(db)
        self.streak_calculator = StreakCalculator(db)
        self.progress_analyzer = ProgressAnalyzer(db)

    async def get_comprehensive_tracking_data(
        self, 
        user_habit_id: UUID
    ) -> Dict[str, Any]:
        """
        종합 추적 데이터 조회
        
        Args:
            user_habit_id: 사용자 습관 ID
            
        Returns:
            Dict: 종합 추적 데이터
        """
        # 병렬로 모든 분석 실행
        current_streak = await self.streak_calculator.calculate_current_streak(user_habit_id)
        longest_streak = await self.streak_calculator.calculate_longest_streak(user_habit_id)
        streak_risk = await self.streak_calculator.predict_streak_risk(user_habit_id)
        recovery_suggestions = await self.streak_calculator.get_streak_recovery_suggestions(user_habit_id)
        
        weekly_completion = await self.progress_analyzer.calculate_completion_rate(
            user_habit_id, TimePeriod.WEEKLY
        )
        monthly_completion = await self.progress_analyzer.calculate_completion_rate(
            user_habit_id, TimePeriod.MONTHLY
        )
        
        consistency_pattern = await self.progress_analyzer.analyze_consistency_pattern(user_habit_id)
        optimal_times = await self.progress_analyzer.identify_optimal_timing(user_habit_id)
        difficulty_adjustment = await self.progress_analyzer.calculate_difficulty_adjustment(user_habit_id)
        
        return {
            "streak_data": {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "risk_level": streak_risk,
                "recovery_suggestions": recovery_suggestions
            },
            "completion_rates": {
                "weekly": round(weekly_completion * 100, 1),
                "monthly": round(monthly_completion * 100, 1)
            },
            "analysis": {
                "consistency_pattern": consistency_pattern.value,
                "optimal_times": optimal_times,
                "difficulty_adjustment": difficulty_adjustment
            }
        }

    async def process_evidence_upload(
        self, 
        habit_log_id: UUID, 
        evidence_data: Dict[str, Any]
    ) -> bool:
        """
        증거 파일 업로드 처리
        
        Args:
            habit_log_id: 습관 로그 ID
            evidence_data: 증거 데이터
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            # 증거 파일 메타데이터 추출
            file_type = evidence_data.get('type', EvidenceType.PHOTO)
            file_url = evidence_data.get('url')
            metadata = evidence_data.get('metadata', {})
            
            # 증거 레코드 생성
            evidence = HabitEvidence(
                habit_log_id=habit_log_id,
                file_type=file_type,
                file_url=file_url,
                metadata=metadata,
                description=evidence_data.get('description')
            )
            
            self.db.add(evidence)
            await self.db.commit()
            
            logger.info(f"증거 파일 업로드 완료: {habit_log_id}")
            return True
            
        except Exception as e:
            logger.error(f"증거 파일 업로드 실패: {str(e)}")
            await self.db.rollback()
            return False