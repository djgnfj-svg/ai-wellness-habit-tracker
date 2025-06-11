"""
사용자 관련 스키마
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from .common import BaseSchema, TimestampMixin, IDMixin
from app.models.user import Gender, FitnessLevel, MotivationStyle, CommunicationStyle


# 사용자 기본 정보
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    nickname: str = Field(..., min_length=2, max_length=50)
    profile_image_url: Optional[str] = None
    birth_year: Optional[int] = Field(None, ge=1900, le=2020)
    gender: Optional[Gender] = None
    timezone: str = "Asia/Seoul"


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    pass


class UserUpdate(BaseModel):
    """사용자 업데이트 스키마"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    profile_image_url: Optional[str] = None
    birth_year: Optional[int] = Field(None, ge=1900, le=2020)
    gender: Optional[Gender] = None
    timezone: Optional[str] = None


class UserInDB(UserBase, IDMixin, TimestampMixin):
    """데이터베이스에 저장된 사용자"""
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None


class User(UserInDB):
    """사용자 응답 스키마"""
    pass


# 웰니스 프로필
class WellnessProfileBase(BaseModel):
    """웰니스 프로필 기본 스키마"""
    fitness_level: FitnessLevel = FitnessLevel.BEGINNER
    primary_goals: List[str] = Field(default_factory=list)
    available_time_slots: List[Dict[str, Any]] = Field(default_factory=list)
    preferred_workout_times: List[str] = Field(default_factory=list)
    preferred_workout_types: List[str] = Field(default_factory=list)
    health_conditions: List[str] = Field(default_factory=list)
    wake_up_time: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    sleep_time: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    work_schedule: Dict[str, Any] = Field(default_factory=dict)


class WellnessProfileCreate(WellnessProfileBase):
    """웰니스 프로필 생성 스키마"""
    pass


class WellnessProfileUpdate(BaseModel):
    """웰니스 프로필 업데이트 스키마"""
    fitness_level: Optional[FitnessLevel] = None
    primary_goals: Optional[List[str]] = None
    available_time_slots: Optional[List[Dict[str, Any]]] = None
    preferred_workout_times: Optional[List[str]] = None
    preferred_workout_types: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    wake_up_time: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    sleep_time: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    work_schedule: Optional[Dict[str, Any]] = None


class WellnessProfile(WellnessProfileBase, IDMixin, TimestampMixin):
    """웰니스 프로필 응답 스키마"""
    user_id: UUID


# 개인화 데이터
class PersonalizationDataBase(BaseModel):
    """개인화 데이터 기본 스키마"""
    personality_type: Optional[str] = Field(None, max_length=10)
    motivation_style: Optional[MotivationStyle] = None
    communication_preference: CommunicationStyle = CommunicationStyle.FRIENDLY
    coaching_frequency: str = Field(default="normal", regex=r"^(low|normal|high)$")
    preferred_message_times: List[str] = Field(default_factory=list)
    language: str = "ko"
    country: str = "KR"
    usage_patterns: Dict[str, Any] = Field(default_factory=dict)


class PersonalizationDataCreate(PersonalizationDataBase):
    """개인화 데이터 생성 스키마"""
    pass


class PersonalizationDataUpdate(BaseModel):
    """개인화 데이터 업데이트 스키마"""
    personality_type: Optional[str] = Field(None, max_length=10)
    motivation_style: Optional[MotivationStyle] = None
    communication_preference: Optional[CommunicationStyle] = None
    coaching_frequency: Optional[str] = Field(None, regex=r"^(low|normal|high)$")
    preferred_message_times: Optional[List[str]] = None
    language: Optional[str] = None
    country: Optional[str] = None
    usage_patterns: Optional[Dict[str, Any]] = None


class PersonalizationData(PersonalizationDataBase, IDMixin, TimestampMixin):
    """개인화 데이터 응답 스키마"""
    user_id: UUID


# 전체 사용자 프로필 (모든 정보 포함)
class UserProfile(User):
    """전체 사용자 프로필"""
    wellness_profile: Optional[WellnessProfile] = None
    personalization_data: Optional[PersonalizationData] = None


# 디바이스 토큰
class DeviceTokenCreate(BaseModel):
    """디바이스 토큰 생성"""
    device_id: str = Field(..., max_length=100)
    token: str = Field(..., max_length=500)
    platform: str = Field(..., regex=r"^(ios|android)$")


class DeviceTokenUpdate(BaseModel):
    """디바이스 토큰 업데이트"""
    token: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class DeviceToken(BaseSchema, IDMixin, TimestampMixin):
    """디바이스 토큰 응답"""
    user_id: UUID
    device_id: str
    token: str
    platform: str
    is_active: bool