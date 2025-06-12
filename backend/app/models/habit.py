"""
습관 관련 모델
"""
from sqlalchemy import (
    Column, String, Boolean, Integer, Text, JSON, 
    DateTime, Enum, ForeignKey, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class FrequencyType(str, enum.Enum):
    """빈도 타입"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class CompletionStatus(str, enum.Enum):
    """완료 상태"""
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    PENDING = "pending"


class DifficultyLevel(int, enum.Enum):
    """난이도 레벨"""
    VERY_EASY = 1
    EASY = 2
    MODERATE = 3
    HARD = 4
    VERY_HARD = 5


class HabitCategory(BaseModel):
    """습관 카테고리"""
    __tablename__ = "habit_categories"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(10), nullable=True)  # 이모지
    color_code = Column(String(7), nullable=True)  # #RRGGBB
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("habit_categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # 관계 설정
    parent_category = relationship("HabitCategory", remote_side="HabitCategory.id")
    subcategories = relationship("HabitCategory", cascade="all, delete-orphan")
    habit_templates = relationship("HabitTemplate", back_populates="category")
    
    def __repr__(self):
        return f"<HabitCategory(name='{self.name}')>"


class HabitTemplate(BaseModel):
    """습관 템플릿"""
    __tablename__ = "habit_templates"
    
    # 기본 정보
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 카테고리 연결
    category_id = Column(UUID(as_uuid=True), ForeignKey("habit_categories.id"), nullable=False)
    
    # 난이도 및 시간
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MODERATE)
    estimated_time_minutes = Column(Integer, default=0)  # 예상 소요 시간
    
    # 권장 빈도
    recommended_frequency_type = Column(Enum(FrequencyType), default=FrequencyType.DAILY)
    recommended_frequency_count = Column(Integer, default=1)  # 하루 1회, 주 3회 등
    
    # 메타데이터
    success_criteria = Column(Text, nullable=True)  # 성공 기준
    tips = Column(JSON, default=list)  # List[str] - 팁들
    benefits = Column(JSON, default=list)  # List[str] - 효과들
    ai_coaching_prompts = Column(JSON, default=list)  # List[str] - AI 코칭 메시지
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # 추천 습관 여부
    usage_count = Column(Integer, default=0)  # 사용 횟수
    
    # 관계 설정
    category = relationship("HabitCategory", back_populates="habit_templates")
    user_habits = relationship("UserHabit", back_populates="habit_template")
    
    def __repr__(self):
        return f"<HabitTemplate(name='{self.name}', difficulty={self.difficulty_level})>"


class UserHabit(BaseModel):
    """사용자별 습관"""
    __tablename__ = "user_habits"
    
    # 연결 정보
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    habit_template_id = Column(UUID(as_uuid=True), ForeignKey("habit_templates.id"), nullable=False)
    
    # 커스터마이징
    custom_name = Column(String(200), nullable=True)  # 사용자가 변경한 이름
    custom_description = Column(Text, nullable=True)
    
    # 목표 설정
    target_frequency_type = Column(Enum(FrequencyType), nullable=False)
    target_frequency_count = Column(Integer, nullable=False)
    specific_days = Column(JSON, default=list)  # List[int] - 0=월요일, 6=일요일
    target_time_slots = Column(JSON, default=list)  # List[str] - ["09:00", "12:00"]
    
    # 리마인더 설정
    reminder_enabled = Column(Boolean, default=True)
    reminder_times = Column(JSON, default=list)  # List[str] - 알림 시간
    reminder_message = Column(String(500), nullable=True)  # 커스텀 리마인더 메시지
    
    # 통계 및 상태
    current_streak = Column(Integer, default=0)  # 현재 연속 달성 일수
    longest_streak = Column(Integer, default=0)  # 최장 연속 달성 기록
    total_completions = Column(Integer, default=0)  # 총 완료 횟수
    is_active = Column(Boolean, default=True)
    
    # 보상 시스템
    reward_points = Column(Integer, default=0)  # 획득한 포인트
    
    # 메타데이터
    notes = Column(Text, nullable=True)  # 사용자 메모
    priority = Column(Integer, default=1)  # 우선순위 (1=높음, 5=낮음)
    
    # 관계 설정
    user = relationship("User")
    habit_template = relationship("HabitTemplate", back_populates="user_habits")
    habit_logs = relationship("HabitLog", back_populates="user_habit", cascade="all, delete-orphan")
    
    def __repr__(self):
        display_name = self.custom_name or (self.habit_template.name if self.habit_template else "Unknown")
        return f"<UserHabit(user_id='{self.user_id}', habit='{display_name}')>"


class HabitLog(BaseModel):
    """습관 실행 로그"""
    __tablename__ = "habit_logs"
    
    # 연결 정보
    user_habit_id = Column(UUID(as_uuid=True), ForeignKey("user_habits.id"), nullable=False)
    
    # 실행 정보
    logged_at = Column(DateTime(timezone=True), nullable=False)  # 실행 시간
    completion_status = Column(Enum(CompletionStatus), nullable=False)
    completion_percentage = Column(Integer, default=100)  # 0-100
    
    # 상세 정보
    duration_minutes = Column(Integer, nullable=True)  # 실제 소요 시간
    intensity_level = Column(Integer, nullable=True)  # 강도 1-5
    location = Column(String(200), nullable=True)  # 실행 장소
    
    # 기분 및 감정
    mood_before = Column(Integer, nullable=True)  # 실행 전 기분 1-10
    mood_after = Column(Integer, nullable=True)   # 실행 후 기분 1-10
    energy_level = Column(Integer, nullable=True)  # 에너지 레벨 1-5
    
    # 메모 및 추가 정보
    notes = Column(Text, nullable=True)
    weather_condition = Column(String(50), nullable=True)  # 날씨
    
    # 보상
    points_earned = Column(Integer, default=0)
    
    # 관계 설정
    user_habit = relationship("UserHabit", back_populates="habit_logs")
    evidences = relationship("HabitEvidence", back_populates="habit_log", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HabitLog(user_habit_id='{self.user_habit_id}', status='{self.completion_status}')>"


class HabitEvidence(BaseModel):
    """습관 실행 증거 (사진, 비디오 등)"""
    __tablename__ = "habit_evidences"
    
    habit_log_id = Column(UUID(as_uuid=True), ForeignKey("habit_logs.id"), nullable=False)
    
    # 파일 정보
    file_type = Column(String(20), nullable=False)  # photo, video, audio
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    
    # 메타데이터
    metadata = Column(JSON, default=dict)  # Dict[str, Any] - EXIF, GPS 등
    description = Column(String(500), nullable=True)
    
    # 관계 설정
    habit_log = relationship("HabitLog", back_populates="evidences")
    
    def __repr__(self):
        return f"<HabitEvidence(habit_log_id='{self.habit_log_id}', type='{self.file_type}')>"


class HabitStreak(BaseModel):
    """습관 스트릭 기록"""
    __tablename__ = "habit_streaks"
    
    user_habit_id = Column(UUID(as_uuid=True), ForeignKey("user_habits.id"), nullable=False)
    
    # 스트릭 정보
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)  # None이면 진행중
    streak_length = Column(Integer, nullable=False)
    
    # 스트릭 타입
    is_current = Column(Boolean, default=False)  # 현재 진행 중인 스트릭
    is_best = Column(Boolean, default=False)     # 최고 기록
    
    # 관계 설정
    user_habit = relationship("UserHabit")
    
    def __repr__(self):
        return f"<HabitStreak(user_habit_id='{self.user_habit_id}', length={self.streak_length})>"
