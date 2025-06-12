"""
습관 관련 스키마
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from .common import BaseSchema, TimestampMixin, IDMixin
from app.models.habit import (
    FrequencyType, CompletionStatus, DifficultyLevel
)


# =====================================================================
# 습관 카테고리 스키마
# =====================================================================

class HabitCategoryBase(BaseModel):
    """습관 카테고리 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color_code: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")
    parent_category_id: Optional[UUID] = None
    sort_order: int = 0


class HabitCategoryCreate(HabitCategoryBase):
    """습관 카테고리 생성 스키마"""
    pass


class HabitCategoryUpdate(BaseModel):
    """습관 카테고리 업데이트 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color_code: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class HabitCategoryResponse(HabitCategoryBase, IDMixin, TimestampMixin):
    """습관 카테고리 응답 스키마"""
    is_active: bool
    subcategories: List['HabitCategoryResponse'] = []
    
    model_config = {"from_attributes": True}


# =====================================================================
# 습관 템플릿 스키마
# =====================================================================

class HabitTemplateBase(BaseModel):
    """습관 템플릿 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: UUID
    difficulty_level: DifficultyLevel = DifficultyLevel.MODERATE
    estimated_time_minutes: int = Field(default=0, ge=0, le=480)  # 최대 8시간
    recommended_frequency_type: FrequencyType = FrequencyType.DAILY
    recommended_frequency_count: int = Field(default=1, ge=1, le=10)
    success_criteria: Optional[str] = None
    tips: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    ai_coaching_prompts: List[str] = Field(default_factory=list)

    @validator('tips', 'benefits', 'ai_coaching_prompts')
    def validate_lists(cls, v):
        if len(v) > 20:  # 최대 20개
            raise ValueError('리스트는 최대 20개 항목까지 허용됩니다')
        return v


class HabitTemplateCreate(HabitTemplateBase):
    """습관 템플릿 생성 스키마"""
    pass


class HabitTemplateUpdate(BaseModel):
    """습관 템플릿 업데이트 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    difficulty_level: Optional[DifficultyLevel] = None
    estimated_time_minutes: Optional[int] = Field(None, ge=0, le=480)
    recommended_frequency_type: Optional[FrequencyType] = None
    recommended_frequency_count: Optional[int] = Field(None, ge=1, le=10)
    success_criteria: Optional[str] = None
    tips: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    ai_coaching_prompts: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class HabitTemplateResponse(HabitTemplateBase, IDMixin, TimestampMixin):
    """습관 템플릿 응답 스키마"""
    is_active: bool
    is_featured: bool
    usage_count: int
    category: HabitCategoryResponse
    
    model_config = {"from_attributes": True}


class HabitTemplateListResponse(BaseModel):
    """습관 템플릿 목록 응답"""
    habits: List[HabitTemplateResponse]
    total_count: int
    has_next: bool
    page: int
    limit: int


# =====================================================================
# 사용자 습관 스키마
# =====================================================================

class FrequencyConfig(BaseModel):
    """빈도 설정"""
    type: FrequencyType
    count: int = Field(..., ge=1, le=50)
    specific_days: List[int] = Field(default_factory=list)  # 0=월, 6=일
    
    @validator('specific_days')
    def validate_days(cls, v):
        if any(day < 0 or day > 6 for day in v):
            raise ValueError('요일은 0(월요일)부터 6(일요일) 사이여야 합니다')
        return list(set(v))  # 중복 제거


class ReminderConfig(BaseModel):
    """리마인더 설정"""
    enabled: bool = True
    times: List[str] = Field(default_factory=list)
    message: Optional[str] = Field(None, max_length=500)
    
    @validator('times')
    def validate_times(cls, v):
        import re
        time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
        for time_str in v:
            if not time_pattern.match(time_str):
                raise ValueError(f'올바르지 않은 시간 형식: {time_str}')
        return v


class UserHabitBase(BaseModel):
    """사용자 습관 기본 스키마"""
    habit_template_id: UUID
    custom_name: Optional[str] = Field(None, max_length=200)
    custom_description: Optional[str] = None
    target_frequency: FrequencyConfig
    reminder_settings: ReminderConfig = Field(default_factory=ReminderConfig)
    notes: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)


class UserHabitCreate(UserHabitBase):
    """사용자 습관 생성 스키마"""
    pass


class UserHabitUpdate(BaseModel):
    """사용자 습관 업데이트 스키마"""
    custom_name: Optional[str] = Field(None, max_length=200)
    custom_description: Optional[str] = None
    target_frequency: Optional[FrequencyConfig] = None
    reminder_settings: Optional[ReminderConfig] = None
    notes: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None


class UserHabitResponse(IDMixin, TimestampMixin):
    """사용자 습관 응답 스키마"""
    user_id: UUID
    habit_template: HabitTemplateResponse
    custom_name: Optional[str]
    custom_description: Optional[str]
    target_frequency: FrequencyConfig
    reminder_settings: ReminderConfig
    current_streak: int
    longest_streak: int
    total_completions: int
    is_active: bool
    reward_points: int
    notes: Optional[str]
    priority: int
    
    model_config = {"from_attributes": True}


# =====================================================================
# 습관 로그 스키마  
# =====================================================================

class HabitLogBase(BaseModel):
    """습관 로그 기본 스키마"""
    completion_status: CompletionStatus
    completion_percentage: int = Field(default=100, ge=0, le=100)
    duration_minutes: Optional[int] = Field(None, ge=0, le=480)
    intensity_level: Optional[int] = Field(None, ge=1, le=5)
    location: Optional[str] = Field(None, max_length=200)
    mood_before: Optional[int] = Field(None, ge=1, le=10)
    mood_after: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    weather_condition: Optional[str] = Field(None, max_length=50)


class HabitLogCreate(HabitLogBase):
    """습관 로그 생성 스키마"""
    user_habit_id: UUID
    logged_at: Optional[datetime] = None  # None이면 현재 시간 사용


class HabitLogUpdate(BaseModel):
    """습관 로그 업데이트 스키마"""
    completion_status: Optional[CompletionStatus] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    duration_minutes: Optional[int] = Field(None, ge=0, le=480)
    intensity_level: Optional[int] = Field(None, ge=1, le=5)
    location: Optional[str] = Field(None, max_length=200)
    mood_before: Optional[int] = Field(None, ge=1, le=10)
    mood_after: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    weather_condition: Optional[str] = Field(None, max_length=50)


class HabitLogResponse(HabitLogBase, IDMixin, TimestampMixin):
    """습관 로그 응답 스키마"""
    user_habit_id: UUID
    logged_at: datetime
    points_earned: int
    
    model_config = {"from_attributes": True}


# =====================================================================
# 진척도 및 통계 스키마
# =====================================================================

class HabitProgress(BaseModel):
    """습관 진척도"""
    user_habit_id: UUID
    habit_name: str
    completion_rate: float = Field(..., ge=0.0, le=1.0)
    current_streak: int
    longest_streak: int
    total_completions: int
    target_completions: int
    points_earned: int
    last_completed_at: Optional[datetime]


class DailyHabitStatus(BaseModel):
    """일일 습관 현황"""
    date: str  # YYYY-MM-DD
    user_habit_id: UUID
    habit_name: str
    target_count: int
    completed_count: int
    completion_rate: float
    status: str  # completed, in_progress, pending, skipped
    next_reminder: Optional[str]  # HH:MM
    logs: List[HabitLogResponse] = []


class DashboardData(BaseModel):
    """대시보드 데이터"""
    date: str
    overall_completion_rate: float
    total_habits: int
    completed_habits: int
    in_progress_habits: int
    pending_habits: int
    habits: List[DailyHabitStatus]
    mood_average: Optional[float]
    energy_average: Optional[float]
    total_points_today: int


# =====================================================================
# 검색 및 필터 스키마
# =====================================================================

class HabitTemplateSearchParams(BaseModel):
    """습관 템플릿 검색 파라미터"""
    category_id: Optional[UUID] = None
    difficulty_level: Optional[DifficultyLevel] = None
    max_time_minutes: Optional[int] = Field(None, ge=0, le=480)
    frequency_type: Optional[FrequencyType] = None
    search: Optional[str] = Field(None, max_length=100)
    is_featured: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class UserHabitFilterParams(BaseModel):
    """사용자 습관 필터 파라미터"""
    category_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    has_reminder: Optional[bool] = None


# =====================================================================
# 응답 포맷 스키마
# =====================================================================

class StandardResponse(BaseModel):
    """표준 응답 형식"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HabitResponse(StandardResponse):
    """습관 관련 응답"""
    data: Union[
        UserHabitResponse,
        List[UserHabitResponse],
        HabitLogResponse,
        DashboardData,
        Dict[str, Any]
    ]


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
