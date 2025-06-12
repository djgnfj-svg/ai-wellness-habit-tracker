"""
AI 코칭 서비스 모듈

개인화된 AI 코칭 메시지 생성 및 스마트 알림 시스템을 제공합니다.
OpenAI GPT-4를 활용하여 사용자의 상황에 맞는 맞춤형 코칭을 제공합니다.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
from enum import Enum
import json
import random
from dataclasses import dataclass, asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import joinedload

from app.models.habit import UserHabit, HabitLog, HabitTemplate, HabitCategory
from app.models.user import User
from app.schemas.habit import CompletionStatus


class MessageType(str, Enum):
    """AI 코칭 메시지 타입"""
    MORNING_MOTIVATION = "morning_motivation"      # 아침 동기부여
    HABIT_REMINDER = "habit_reminder"             # 습관 리마인더  
    ENCOURAGEMENT = "encouragement"               # 격려 메시지
    STREAK_CELEBRATION = "streak_celebration"     # 스트릭 축하
    FAILURE_RECOVERY = "failure_recovery"         # 실패 극복
    WEEKLY_REFLECTION = "weekly_reflection"       # 주간 회고
    GOAL_ADJUSTMENT = "goal_adjustment"           # 목표 조정
    PROGRESS_INSIGHT = "progress_insight"         # 진척도 인사이트


class EnergyLevel(str, Enum):
    """에너지 레벨"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class WeatherCondition(str, Enum):
    """날씨 상태"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"


class NotificationType(str, Enum):
    """알림 타입"""
    HABIT_REMINDER = "habit_reminder"
    STREAK_ALERT = "streak_alert"
    MOTIVATION = "motivation"
    CELEBRATION = "celebration"
    WEEKLY_REPORT = "weekly_report"


@dataclass
class MoodEntry:
    """기분 기록"""
    date: date
    mood_score: int  # 1-10
    energy_level: EnergyLevel
    stress_level: int  # 1-10
    notes: Optional[str] = None


@dataclass
class WeatherInfo:
    """날씨 정보"""
    condition: WeatherCondition
    temperature: float
    humidity: int
    description: str


@dataclass
class CalendarEvent:
    """캘린더 이벤트"""
    title: str
    start_time: datetime
    end_time: datetime
    is_busy: bool = True


@dataclass
class EnergyPattern:
    """에너지 패턴"""
    morning_energy: EnergyLevel
    afternoon_energy: EnergyLevel
    evening_energy: EnergyLevel
    peak_hours: List[int]  # 0-23
    low_hours: List[int]   # 0-23


@dataclass
class CoachingContext:
    """코칭 컨텍스트"""
    user_profile: Dict[str, Any]
    recent_logs: List[Dict[str, Any]]
    streak_status: Dict[str, int]
    mood_trends: List[MoodEntry]
    weather_data: Optional[WeatherInfo]
    calendar_events: List[CalendarEvent]
    energy_patterns: Optional[EnergyPattern]
    current_time: datetime
    day_of_week: str
    time_of_day: str  # morning, afternoon, evening, night


@dataclass
class CoachingOpportunity:
    """코칭 기회"""
    opportunity_type: str
    priority: int  # 1-10
    context: str
    suggested_message_type: MessageType
    urgency: str  # low, medium, high


@dataclass
class CoachingMessage:
    """코칭 메시지"""
    message: str
    message_type: MessageType
    tone: str  # encouraging, motivational, supportive, celebratory
    personalization_score: float  # 0.0-1.0
    context_relevance: float  # 0.0-1.0
    generated_at: datetime


@dataclass
class NotificationSchedule:
    """알림 스케줄"""
    user_id: UUID
    habit_id: Optional[UUID]
    optimal_times: List[str]  # HH:MM format
    frequency: str  # daily, weekly, custom
    enabled: bool = True


@dataclass
class FrequencyConfig:
    """알림 빈도 설정"""
    daily_limit: int
    min_interval_hours: int
    peak_times: List[str]
    avoid_times: List[str]


class ContextAnalyzer:
    """컨텍스트 분석기"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_current_situation(self, user_id: UUID) -> CoachingContext:
        """현재 상황 종합 분석"""
        
        # 사용자 프로필 조회
        user_profile = await self._get_user_profile(user_id)
        
        # 최근 로그 조회 (7일)
        recent_logs = await self._get_recent_logs(user_id, days=7)
        
        # 스트릭 상태 조회
        streak_status = await self._get_streak_status(user_id)
        
        # 기분 트렌드 (모의 데이터)
        mood_trends = self._generate_mock_mood_trends()
        
        # 날씨 데이터 (모의 데이터)
        weather_data = self._generate_mock_weather()
        
        # 캘린더 이벤트 (모의 데이터)
        calendar_events = self._generate_mock_calendar_events()
        
        # 에너지 패턴 (모의 데이터)
        energy_patterns = self._generate_mock_energy_patterns()
        
        # 현재 시간 정보
        now = datetime.now()
        current_time = now
        day_of_week = now.strftime("%A")
        time_of_day = self._get_time_of_day(now.hour)
        
        return CoachingContext(
            user_profile=user_profile,
            recent_logs=recent_logs,
            streak_status=streak_status,
            mood_trends=mood_trends,
            weather_data=weather_data,
            calendar_events=calendar_events,
            energy_patterns=energy_patterns,
            current_time=current_time,
            day_of_week=day_of_week,
            time_of_day=time_of_day
        )
    
    async def identify_coaching_opportunities(self, context: CoachingContext) -> List[CoachingOpportunity]:
        """코칭 필요 상황 감지"""
        opportunities = []
        
        # 스트릭 위험 감지
        for habit_name, streak in context.streak_status.items():
            if streak >= 7:
                opportunities.append(CoachingOpportunity(
                    opportunity_type="streak_celebration",
                    priority=8,
                    context=f"{habit_name} 습관 {streak}일 연속 달성",
                    suggested_message_type=MessageType.STREAK_CELEBRATION,
                    urgency="medium"
                ))
            elif streak == 0:
                opportunities.append(CoachingOpportunity(
                    opportunity_type="failure_recovery",
                    priority=9,
                    context=f"{habit_name} 습관 스트릭 중단",
                    suggested_message_type=MessageType.FAILURE_RECOVERY,
                    urgency="high"
                ))
        
        # 시간대별 기회 감지
        if context.time_of_day == "morning":
            opportunities.append(CoachingOpportunity(
                opportunity_type="morning_motivation",
                priority=7,
                context="아침 동기부여 시간",
                suggested_message_type=MessageType.MORNING_MOTIVATION,
                urgency="medium"
            ))
        
        # 완료율 기반 기회 감지
        recent_completion_rate = self._calculate_recent_completion_rate(context.recent_logs)
        if recent_completion_rate < 0.5:
            opportunities.append(CoachingOpportunity(
                opportunity_type="encouragement",
                priority=8,
                context=f"최근 완료율 {recent_completion_rate:.1%}로 낮음",
                suggested_message_type=MessageType.ENCOURAGEMENT,
                urgency="high"
            ))
        
        # 주간 회고 기회
        if context.day_of_week == "Sunday" and context.time_of_day == "evening":
            opportunities.append(CoachingOpportunity(
                opportunity_type="weekly_reflection",
                priority=6,
                context="주간 회고 시간",
                suggested_message_type=MessageType.WEEKLY_REFLECTION,
                urgency="low"
            ))
        
        # 우선순위 순으로 정렬
        opportunities.sort(key=lambda x: x.priority, reverse=True)
        return opportunities
    
    async def _get_user_profile(self, user_id: UUID) -> Dict[str, Any]:
        """사용자 프로필 조회"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {}
        
        return {
            "name": user.name,
            "email": user.email,
            "timezone": getattr(user, 'timezone', 'UTC'),
            "preferences": getattr(user, 'preferences', {}),
            "goals": getattr(user, 'goals', []),
            "personality_type": getattr(user, 'personality_type', 'balanced')
        }
    
    async def _get_recent_logs(self, user_id: UUID, days: int = 7) -> List[Dict[str, Any]]:
        """최근 로그 조회"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        stmt = select(HabitLog).options(
            joinedload(HabitLog.user_habit).joinedload(UserHabit.habit_template)
        ).join(
            UserHabit, HabitLog.user_habit_id == UserHabit.id
        ).where(
            and_(
                UserHabit.user_id == user_id,
                func.date(HabitLog.logged_at) >= start_date,
                func.date(HabitLog.logged_at) <= end_date
            )
        ).order_by(desc(HabitLog.logged_at))
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        return [
            {
                "habit_name": log.user_habit.habit_template.name,
                "completion_status": log.completion_status.value,
                "completion_percentage": log.completion_percentage,
                "logged_at": log.logged_at,
                "notes": log.notes
            }
            for log in logs
        ]
    
    async def _get_streak_status(self, user_id: UUID) -> Dict[str, int]:
        """스트릭 상태 조회"""
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.is_active == True
            )
        )
        
        result = await self.db.execute(stmt)
        user_habits = result.scalars().all()
        
        return {
            habit.habit_template.name: habit.current_streak
            for habit in user_habits
        }
    
    def _generate_mock_mood_trends(self) -> List[MoodEntry]:
        """모의 기분 트렌드 생성"""
        trends = []
        for i in range(7):
            date_obj = date.today() - timedelta(days=i)
            trends.append(MoodEntry(
                date=date_obj,
                mood_score=random.randint(6, 9),
                energy_level=random.choice(list(EnergyLevel)),
                stress_level=random.randint(3, 7)
            ))
        return trends
    
    def _generate_mock_weather(self) -> WeatherInfo:
        """모의 날씨 데이터 생성"""
        return WeatherInfo(
            condition=random.choice(list(WeatherCondition)),
            temperature=random.uniform(15, 25),
            humidity=random.randint(40, 80),
            description="맑은 날씨"
        )
    
    def _generate_mock_calendar_events(self) -> List[CalendarEvent]:
        """모의 캘린더 이벤트 생성"""
        now = datetime.now()
        return [
            CalendarEvent(
                title="회의",
                start_time=now.replace(hour=14, minute=0),
                end_time=now.replace(hour=15, minute=0),
                is_busy=True
            )
        ]
    
    def _generate_mock_energy_patterns(self) -> EnergyPattern:
        """모의 에너지 패턴 생성"""
        return EnergyPattern(
            morning_energy=EnergyLevel.HIGH,
            afternoon_energy=EnergyLevel.MEDIUM,
            evening_energy=EnergyLevel.LOW,
            peak_hours=[9, 10, 11],
            low_hours=[14, 15, 22, 23]
        )
    
    def _get_time_of_day(self, hour: int) -> str:
        """시간대 구분"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def _calculate_recent_completion_rate(self, recent_logs: List[Dict[str, Any]]) -> float:
        """최근 완료율 계산"""
        if not recent_logs:
            return 0.0
        
        completed = sum(1 for log in recent_logs if log["completion_status"] == "completed")
        return completed / len(recent_logs)


class AICoachingService:
    """AI 코칭 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.context_analyzer = ContextAnalyzer(db)
    
    async def generate_personalized_message(
        self, 
        user_id: UUID,
        message_type: MessageType,
        habit_id: Optional[UUID] = None
    ) -> CoachingMessage:
        """개인화된 코칭 메시지 생성"""
        
        # 컨텍스트 분석
        context = await self.context_analyzer.analyze_current_situation(user_id)
        
        # 습관별 컨텍스트 추가
        habit_context = None
        if habit_id:
            habit_context = await self._get_habit_context(habit_id)
        
        # 프롬프트 생성
        prompt = self._build_coaching_prompt(context, message_type, habit_context)
        
        # OpenAI API 호출 (실제 구현에서는 openai 라이브러리 사용)
        # 현재는 모의 응답 생성
        message_content = await self._generate_mock_ai_response(prompt, message_type, context)
        
        # 개인화 점수 계산
        personalization_score = self._calculate_personalization_score(context, message_content)
        context_relevance = self._calculate_context_relevance(context, message_type)
        
        return CoachingMessage(
            message=message_content,
            message_type=message_type,
            tone=self._determine_tone(message_type),
            personalization_score=personalization_score,
            context_relevance=context_relevance,
            generated_at=datetime.now()
        )
    
    def _build_coaching_prompt(
        self, 
        context: CoachingContext, 
        message_type: MessageType,
        habit_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """상황별 프롬프트 생성"""
        
        base_prompt = f"""
당신은 전문적인 웰니스 코치입니다. 사용자의 상황을 분석하여 개인화된 코칭 메시지를 생성해주세요.

사용자 정보:
- 이름: {context.user_profile.get('name', '사용자')}
- 현재 시간: {context.current_time.strftime('%Y-%m-%d %H:%M')}
- 요일: {context.day_of_week}
- 시간대: {context.time_of_day}

최근 활동:
- 스트릭 상태: {context.streak_status}
- 최근 완료율: {self._calculate_recent_completion_rate_from_context(context)}

메시지 타입: {message_type.value}
"""
        
        # 메시지 타입별 추가 지침
        type_specific_prompts = {
            MessageType.MORNING_MOTIVATION: "아침 시간에 하루를 시작하는 동기부여 메시지를 작성해주세요. 긍정적이고 에너지 넘치는 톤으로.",
            MessageType.HABIT_REMINDER: "습관 실천을 위한 친근한 리마인더 메시지를 작성해주세요.",
            MessageType.ENCOURAGEMENT: "어려움을 겪고 있는 사용자를 격려하는 메시지를 작성해주세요.",
            MessageType.STREAK_CELEBRATION: "스트릭 달성을 축하하는 기쁜 메시지를 작성해주세요.",
            MessageType.FAILURE_RECOVERY: "실패를 극복하고 다시 시작할 수 있도록 돕는 메시지를 작성해주세요.",
            MessageType.WEEKLY_REFLECTION: "한 주를 돌아보고 다음 주를 계획하는 회고 메시지를 작성해주세요.",
            MessageType.GOAL_ADJUSTMENT: "목표 조정이 필요한 상황에서 도움이 되는 메시지를 작성해주세요.",
            MessageType.PROGRESS_INSIGHT: "진척도에 대한 인사이트와 개선 방향을 제시하는 메시지를 작성해주세요."
        }
        
        prompt = base_prompt + "\n" + type_specific_prompts.get(message_type, "")
        
        if habit_context:
            prompt += f"\n\n습관 정보:\n- 습관명: {habit_context.get('name')}\n- 카테고리: {habit_context.get('category')}"
        
        prompt += "\n\n메시지는 한국어로 작성하고, 100자 이내로 간결하게 작성해주세요."
        
        return prompt
    
    async def _generate_mock_ai_response(
        self, 
        prompt: str, 
        message_type: MessageType, 
        context: CoachingContext
    ) -> str:
        """모의 AI 응답 생성 (실제로는 OpenAI API 호출)"""
        
        # 메시지 타입별 템플릿 응답
        templates = {
            MessageType.MORNING_MOTIVATION: [
                f"좋은 아침이에요, {context.user_profile.get('name', '님')}! 오늘도 멋진 하루를 만들어가세요! ☀️",
                f"새로운 하루가 시작됐어요! {context.user_profile.get('name', '님')}의 목표를 향해 한 걸음씩 나아가봐요! 💪",
                f"아침의 신선한 에너지로 오늘의 습관을 실천해보세요! 화이팅! 🌟"
            ],
            MessageType.HABIT_REMINDER: [
                "습관 실천 시간이에요! 작은 실천이 큰 변화를 만들어요 ⏰",
                "오늘의 목표를 잊지 마세요! 지금이 바로 그 시간입니다 ✨",
                "꾸준함이 가장 큰 힘이에요. 오늘도 함께해요! 🎯"
            ],
            MessageType.ENCOURAGEMENT: [
                "완벽하지 않아도 괜찮아요. 시도하는 것만으로도 충분히 대단해요! 💙",
                "어려운 시기일수록 작은 성취에 집중해보세요. 당신은 할 수 있어요! 🌈",
                "포기하지 마세요. 모든 전문가도 처음엔 초보자였어요! 🌱"
            ],
            MessageType.STREAK_CELEBRATION: [
                f"와! 연속 달성 중이시네요! 정말 대단해요! 🎉",
                f"꾸준함의 힘을 보여주고 계시네요! 축하드려요! 🏆",
                f"이 멋진 기록을 계속 이어가세요! 응원합니다! 👏"
            ],
            MessageType.FAILURE_RECOVERY: [
                "괜찮아요. 다시 시작하는 것이 중요해요. 오늘부터 새롭게! 🔄",
                "실패는 성공의 어머니예요. 이번 경험을 발판으로 더 강해져요! 💪",
                "완벽한 사람은 없어요. 다시 일어서는 당신이 진짜 영웅이에요! ⭐"
            ],
            MessageType.WEEKLY_REFLECTION: [
                "이번 주도 수고 많으셨어요! 다음 주는 더 나은 한 주가 될 거예요 📝",
                "한 주를 돌아보며 성장한 모습을 발견해보세요. 분명 있을 거예요! 🔍",
                "작은 변화들이 모여 큰 성장을 만들어요. 이번 주도 의미 있었어요! 📈"
            ],
            MessageType.GOAL_ADJUSTMENT: [
                "목표를 조정하는 것은 현명한 선택이에요. 더 나은 방향으로! 🎯",
                "상황에 맞게 목표를 수정하는 것도 성장의 과정이에요 📊",
                "유연한 목표 설정으로 더 지속 가능한 습관을 만들어봐요! 🌿"
            ],
            MessageType.PROGRESS_INSIGHT: [
                "지금까지의 진척도를 보면 분명한 성장이 보여요! 계속 화이팅! 📈",
                "데이터가 말해주는 당신의 발전 모습, 정말 인상적이에요! 📊",
                "꾸준한 노력의 결과가 수치로 나타나고 있어요. 대단해요! 🎯"
            ]
        }
        
        messages = templates.get(message_type, templates[MessageType.ENCOURAGEMENT])
        return random.choice(messages)
    
    async def _get_habit_context(self, habit_id: UUID) -> Optional[Dict[str, Any]]:
        """습관 컨텍스트 조회"""
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template).joinedload(HabitTemplate.category)
        ).where(UserHabit.id == habit_id)
        
        result = await self.db.execute(stmt)
        habit = result.scalar_one_or_none()
        
        if not habit:
            return None
        
        return {
            "name": habit.habit_template.name,
            "category": habit.habit_template.category.name,
            "difficulty": habit.habit_template.difficulty_level,
            "current_streak": habit.current_streak,
            "total_completions": habit.total_completions
        }
    
    def _calculate_personalization_score(self, context: CoachingContext, message: str) -> float:
        """개인화 점수 계산"""
        score = 0.5  # 기본 점수
        
        # 이름 포함 여부
        if context.user_profile.get('name', '') in message:
            score += 0.2
        
        # 시간대 적절성
        if context.time_of_day in message.lower():
            score += 0.1
        
        # 스트릭 정보 반영
        if any(str(streak) in message for streak in context.streak_status.values()):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_context_relevance(self, context: CoachingContext, message_type: MessageType) -> float:
        """컨텍스트 관련성 계산"""
        relevance = 0.7  # 기본 관련성
        
        # 시간대별 관련성
        time_relevance = {
            "morning": {MessageType.MORNING_MOTIVATION: 1.0, MessageType.HABIT_REMINDER: 0.8},
            "evening": {MessageType.WEEKLY_REFLECTION: 1.0, MessageType.PROGRESS_INSIGHT: 0.9},
            "afternoon": {MessageType.ENCOURAGEMENT: 0.9, MessageType.GOAL_ADJUSTMENT: 0.8}
        }
        
        if context.time_of_day in time_relevance:
            relevance = time_relevance[context.time_of_day].get(message_type, relevance)
        
        return relevance
    
    def _determine_tone(self, message_type: MessageType) -> str:
        """메시지 톤 결정"""
        tone_mapping = {
            MessageType.MORNING_MOTIVATION: "energetic",
            MessageType.HABIT_REMINDER: "friendly",
            MessageType.ENCOURAGEMENT: "supportive",
            MessageType.STREAK_CELEBRATION: "celebratory",
            MessageType.FAILURE_RECOVERY: "compassionate",
            MessageType.WEEKLY_REFLECTION: "reflective",
            MessageType.GOAL_ADJUSTMENT: "advisory",
            MessageType.PROGRESS_INSIGHT: "analytical"
        }
        return tone_mapping.get(message_type, "supportive")
    
    def _calculate_recent_completion_rate_from_context(self, context: CoachingContext) -> str:
        """컨텍스트에서 최근 완료율 계산"""
        if not context.recent_logs:
            return "0%"
        
        completed = sum(1 for log in context.recent_logs if log["completion_status"] == "completed")
        rate = completed / len(context.recent_logs)
        return f"{rate:.0%}"


class SmartNotificationEngine:
    """스마트 알림 엔진"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def optimize_notification_timing(self, user_id: UUID, habit_id: UUID) -> NotificationSchedule:
        """사용자 행동 패턴 기반 최적 시간 계산"""
        
        # 과거 완료 시간 패턴 분석
        completion_times = await self._analyze_completion_patterns(user_id, habit_id)
        
        # 최적 시간대 계산
        optimal_times = self._calculate_optimal_times(completion_times)
        
        return NotificationSchedule(
            user_id=user_id,
            habit_id=habit_id,
            optimal_times=optimal_times,
            frequency="daily",
            enabled=True
        )
    
    async def personalize_notification_content(
        self, 
        user_id: UUID, 
        notification_type: NotificationType,
        habit_id: Optional[UUID] = None
    ) -> str:
        """개인화된 알림 메시지 생성"""
        
        # 사용자 선호도 조회
        preferences = await self._get_user_notification_preferences(user_id)
        
        # 메시지 스타일 결정
        style = preferences.get('message_style', 'friendly')
        
        # 타입별 메시지 생성
        if notification_type == NotificationType.HABIT_REMINDER:
            return self._generate_habit_reminder(style, habit_id)
        elif notification_type == NotificationType.STREAK_ALERT:
            return self._generate_streak_alert(style)
        elif notification_type == NotificationType.MOTIVATION:
            return self._generate_motivation_message(style)
        elif notification_type == NotificationType.CELEBRATION:
            return self._generate_celebration_message(style)
        else:
            return "습관 실천 시간이에요! 💪"
    
    async def calculate_notification_frequency(self, user_id: UUID, habit_id: UUID) -> FrequencyConfig:
        """개인별 최적 알림 빈도 계산"""
        
        # 사용자 응답률 분석
        response_rate = await self._analyze_notification_response_rate(user_id)
        
        # 습관 완료율 분석
        completion_rate = await self._analyze_habit_completion_rate(user_id, habit_id)
        
        # 빈도 계산
        if completion_rate > 0.8:
            daily_limit = 1  # 높은 완료율 = 적은 알림
        elif completion_rate > 0.5:
            daily_limit = 2  # 중간 완료율 = 보통 알림
        else:
            daily_limit = 3  # 낮은 완료율 = 많은 알림
        
        return FrequencyConfig(
            daily_limit=daily_limit,
            min_interval_hours=4,
            peak_times=["09:00", "14:00", "19:00"],
            avoid_times=["23:00", "00:00", "01:00", "02:00", "03:00", "04:00", "05:00"]
        )
    
    async def _analyze_completion_patterns(self, user_id: UUID, habit_id: UUID) -> List[int]:
        """완료 시간 패턴 분석"""
        
        # 최근 30일 완료 로그 조회
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        stmt = select(HabitLog).join(
            UserHabit, HabitLog.user_habit_id == UserHabit.id
        ).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.id == habit_id,
                HabitLog.completion_status == CompletionStatus.COMPLETED,
                func.date(HabitLog.logged_at) >= start_date
            )
        )
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        # 완료 시간 추출 (시간만)
        completion_hours = [log.logged_at.hour for log in logs]
        return completion_hours
    
    def _calculate_optimal_times(self, completion_times: List[int]) -> List[str]:
        """최적 알림 시간 계산"""
        if not completion_times:
            return ["09:00", "14:00", "19:00"]  # 기본값
        
        # 가장 빈번한 완료 시간대 찾기
        from collections import Counter
        time_counts = Counter(completion_times)
        
        # 상위 3개 시간대 선택
        top_times = time_counts.most_common(3)
        
        # 알림은 완료 시간보다 1시간 전에 설정
        optimal_times = []
        for hour, _ in top_times:
            reminder_hour = max(0, hour - 1)
            optimal_times.append(f"{reminder_hour:02d}:00")
        
        return optimal_times
    
    async def _get_user_notification_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """사용자 알림 선호도 조회"""
        # 실제 구현에서는 사용자 설정 테이블에서 조회
        return {
            "message_style": "friendly",
            "frequency": "medium",
            "quiet_hours": ["22:00", "07:00"]
        }
    
    def _generate_habit_reminder(self, style: str, habit_id: Optional[UUID]) -> str:
        """습관 리마인더 생성"""
        if style == "motivational":
            return "목표를 향해 한 걸음 더! 지금이 바로 그 시간이에요! 🎯"
        elif style == "gentle":
            return "습관 실천 시간이에요. 천천히 시작해보세요 😊"
        else:  # friendly
            return "습관 실천 시간이에요! 오늘도 함께해요! 💪"
    
    def _generate_streak_alert(self, style: str) -> str:
        """스트릭 알림 생성"""
        if style == "motivational":
            return "연속 기록이 위험해요! 지금 실천하면 기록을 이어갈 수 있어요! 🔥"
        else:
            return "스트릭을 이어가려면 지금이 기회예요! ⚡"
    
    def _generate_motivation_message(self, style: str) -> str:
        """동기부여 메시지 생성"""
        messages = {
            "motivational": "당신은 할 수 있어요! 포기하지 마세요! 💪",
            "gentle": "작은 걸음도 앞으로 나아가는 거예요 🌱",
            "friendly": "오늘도 좋은 하루 만들어가요! ✨"
        }
        return messages.get(style, messages["friendly"])
    
    def _generate_celebration_message(self, style: str) -> str:
        """축하 메시지 생성"""
        return "축하해요! 정말 대단해요! 🎉"
    
    async def _analyze_notification_response_rate(self, user_id: UUID) -> float:
        """알림 응답률 분석"""
        # 실제 구현에서는 알림 로그 테이블에서 분석
        return 0.7  # 모의 데이터
    
    async def _analyze_habit_completion_rate(self, user_id: UUID, habit_id: UUID) -> float:
        """습관 완료율 분석"""
        # 최근 30일 완료율 계산
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        stmt = select(
            func.count(HabitLog.id).label('total'),
            func.sum(
                func.case(
                    (HabitLog.completion_status == CompletionStatus.COMPLETED, 1),
                    else_=0
                )
            ).label('completed')
        ).select_from(HabitLog).join(
            UserHabit, HabitLog.user_habit_id == UserHabit.id
        ).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.id == habit_id,
                func.date(HabitLog.logged_at) >= start_date
            )
        )
        
        result = await self.db.execute(stmt)
        row = result.fetchone()
        
        if not row or not row.total:
            return 0.0
        
        return float(row.completed or 0) / float(row.total)