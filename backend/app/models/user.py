"""
사용자 관련 모델
"""
from sqlalchemy import (
    Column, String, Boolean, Integer, Text, JSON, 
    DateTime, Enum, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class Gender(str, enum.Enum):
    """성별 열거형"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class FitnessLevel(str, enum.Enum):
    """피트니스 레벨"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MotivationStyle(str, enum.Enum):
    """동기부여 스타일"""
    COMPETITIVE = "competitive"     # 경쟁형
    ACHIEVEMENT = "achievement"     # 성취형
    SOCIAL = "social"              # 관계형


class CommunicationStyle(str, enum.Enum):
    """커뮤니케이션 스타일"""
    FRIENDLY = "friendly"          # 친근함
    PROFESSIONAL = "professional"  # 전문적
    CASUAL = "casual"             # 간결함


class SocialProvider(str, enum.Enum):
    """소셜 로그인 제공자"""
    KAKAO = "kakao"
    NAVER = "naver"
    GOOGLE = "google"


class User(BaseModel):
    """사용자 기본 정보"""
    __tablename__ = "users"
    
    # 기본 정보
    email = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(50), nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    
    # 개인 정보
    birth_year = Column(Integer, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    timezone = Column(String(50), default="Asia/Seoul")
    
    # 계정 상태
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # 소셜 로그인 정보
    social_accounts = relationship(
        "SocialAccount", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 웰니스 프로필
    wellness_profile = relationship(
        "WellnessProfile", 
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # 개인화 데이터
    personalization_data = relationship(
        "PersonalizationData",
        back_populates="user", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(email='{self.email}', nickname='{self.nickname}')>"


class SocialAccount(BaseModel):
    """소셜 계정 정보"""
    __tablename__ = "social_accounts"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(SocialProvider), nullable=False)
    provider_user_id = Column(String(100), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # 관계 설정
    user = relationship("User", back_populates="social_accounts")
    
    def __repr__(self):
        return f"<SocialAccount(provider='{self.provider}', user_id='{self.user_id}')>"


class WellnessProfile(BaseModel):
    """웰니스 프로필"""
    __tablename__ = "wellness_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 피트니스 정보
    fitness_level = Column(Enum(FitnessLevel), default=FitnessLevel.BEGINNER)
    primary_goals = Column(JSON, default=list)  # List[str]
    
    # 시간 관련 설정
    available_time_slots = Column(JSON, default=list)  # List[Dict]
    preferred_workout_times = Column(JSON, default=list)  # List[str]
    
    # 운동 선호도
    preferred_workout_types = Column(JSON, default=list)  # List[str]
    
    # 건강 상태
    health_conditions = Column(JSON, default=list)  # List[str]
    
    # 생활 패턴
    wake_up_time = Column(String(5), nullable=True)  # "08:00"
    sleep_time = Column(String(5), nullable=True)    # "23:00"
    work_schedule = Column(JSON, default=dict)       # Dict
    
    # 관계 설정
    user = relationship("User", back_populates="wellness_profile")
    
    def __repr__(self):
        return f"<WellnessProfile(user_id='{self.user_id}', fitness_level='{self.fitness_level}')>"


class PersonalizationData(BaseModel):
    """개인화 데이터"""
    __tablename__ = "personalization_data"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 성격 및 선호도
    personality_type = Column(String(10), nullable=True)  # MBTI 등
    motivation_style = Column(Enum(MotivationStyle), nullable=True)
    communication_preference = Column(Enum(CommunicationStyle), default=CommunicationStyle.FRIENDLY)
    
    # AI 코칭 설정
    coaching_frequency = Column(String(10), default="normal")  # low, normal, high
    preferred_message_times = Column(JSON, default=list)       # List[str]
    
    # 언어 및 지역 설정
    language = Column(String(5), default="ko")
    country = Column(String(2), default="KR")
    
    # 앱 사용 패턴 (분석용)
    usage_patterns = Column(JSON, default=dict)  # Dict[str, Any]
    
    # 관계 설정
    user = relationship("User", back_populates="personalization_data")
    
    def __repr__(self):
        return f"<PersonalizationData(user_id='{self.user_id}', motivation_style='{self.motivation_style}')>"


class DeviceToken(BaseModel):
    """디바이스 토큰 (푸시 알림용)"""
    __tablename__ = "device_tokens"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(String(100), nullable=False)
    token = Column(String(500), nullable=False)
    platform = Column(String(10), nullable=False)  # ios, android
    is_active = Column(Boolean, default=True)
    
    # 관계 설정
    user = relationship("User")
    
    def __repr__(self):
        return f"<DeviceToken(user_id='{self.user_id}', platform='{self.platform}')>"