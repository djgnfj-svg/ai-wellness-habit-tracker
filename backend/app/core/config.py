"""
WellnessAI 애플리케이션 설정

이 모듈은 애플리케이션의 모든 설정을 관리합니다.
환경별 설정, 보안 설정, 데이터베이스 설정 등을 포함합니다.
"""
import logging
import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    
    모든 설정은 환경변수 또는 .env 파일에서 로드됩니다.
    운영환경에서는 환경변수를 사용하는 것을 권장합니다.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid"  # 정의되지 않은 설정은 허용하지 않음
    )
    
    # ===== 기본 애플리케이션 설정 =====
    APP_NAME: str = "WellnessAI"
    APP_DESCRIPTION: str = "AI 기반 웰니스 습관 추적 API"
    APP_VERSION: str = "1.0.0"
    
    # 환경 설정 (development, staging, production)
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = Field(default=True)
    
    # ===== 보안 설정 =====
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT 토큰 서명에 사용되는 비밀키. 운영환경에서는 반드시 변경해야 함"
    )
    
    # 비밀번호 정책
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=6, le=128)
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # JWT 토큰 설정
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, ge=5, le=60 * 24 * 7)  # 1일, 최대 7일
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, ge=1, le=365)  # 30일, 최대 1년
    TOKEN_ALGORITHM: str = "HS256"
    
    # Rate Limiting 설정
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    RATE_LIMIT_BURST: int = Field(default=100, ge=1, le=1000)
    
    # ===== API 설정 =====
    API_V1_STR: str = "/api/v1"
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000, ge=1, le=65535)
    
    # API 문서화 설정
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: Optional[str] = "/openapi.json"
    
    # ===== 데이터베이스 설정 =====
    # PostgreSQL 설정
    DATABASE_URL: str = Field(
        default="postgresql://username:password@localhost:5432/wellnessai_dev",
        description="PostgreSQL 데이터베이스 연결 URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=0, ge=0, le=20)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=5, le=300)
    DATABASE_POOL_RECYCLE: int = Field(default=3600, ge=300, le=86400)  # 1시간
    
    # 테스트 데이터베이스 설정
    DATABASE_TEST_URL: Optional[str] = Field(
        default="sqlite:///./test.db",
        description="테스트용 데이터베이스 URL"
    )
    
    # ===== Redis 설정 =====
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis 서버 연결 URL"
    )
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = Field(default=10, ge=1, le=100)
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(default=30, ge=10, le=300)
    
    # ===== CORS 설정 =====
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=[
            "http://localhost:3000",      # React 개발 서버
            "http://localhost:19006",     # Expo 개발 서버
            "http://127.0.0.1:3000",     # 로컬호스트 대안
        ]
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """CORS origins 설정을 검증하고 변환합니다."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError("CORS origins must be a string or list")
    
    # ===== 소셜 로그인 설정 =====
    # 카카오 로그인
    KAKAO_CLIENT_ID: Optional[str] = Field(default=None, description="카카오 앱 클라이언트 ID")
    KAKAO_CLIENT_SECRET: Optional[str] = Field(default=None, description="카카오 앱 클라이언트 시크릿")
    KAKAO_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/kakao/callback")
    
    # 네이버 로그인
    NAVER_CLIENT_ID: Optional[str] = Field(default=None, description="네이버 앱 클라이언트 ID")
    NAVER_CLIENT_SECRET: Optional[str] = Field(default=None, description="네이버 앱 클라이언트 시크릿")
    NAVER_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/naver/callback")
    
    # 구글 로그인
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="구글 앱 클라이언트 ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, description="구글 앱 클라이언트 시크릿")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/google/callback")
    
    # ===== 외부 API 설정 =====
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API 키")
    OPENAI_MODEL: str = Field(default="gpt-4", description="사용할 OpenAI 모델")
    OPENAI_MAX_TOKENS: int = Field(default=500, ge=1, le=4000)
    OPENAI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # ===== 알림 설정 =====
    # Firebase FCM
    FIREBASE_PROJECT_ID: Optional[str] = Field(default=None, description="Firebase 프로젝트 ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = Field(default=None, description="Firebase 서비스 계정 키")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(default=None, description="Firebase 서비스 계정 이메일")
    
    # SendGrid (이메일)
    SENDGRID_API_KEY: Optional[str] = Field(default=None, description="SendGrid API 키")
    SENDGRID_FROM_EMAIL: str = Field(default="noreply@wellnessai.co.kr", description="발신자 이메일")
    
    # ===== 로깅 설정 =====
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="로그 출력 형식"
    )
    LOG_FILE_PATH: Optional[str] = Field(default=None, description="로그 파일 경로")
    LOG_ROTATION: str = Field(default="1 day", description="로그 파일 순환 주기")
    LOG_RETENTION: str = Field(default="30 days", description="로그 파일 보존 기간")
    
    # ===== 모니터링 설정 =====
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, ge=0.0, le=1.0)
    
    # ===== 파일 업로드 설정 =====
    MAX_UPLOAD_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="최대 업로드 파일 크기 (바이트)")  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "webp"])
    UPLOAD_PATH: str = Field(default="./uploads", description="파일 업로드 저장 경로")
    
    # ===== 비즈니스 로직 설정 =====
    # 웰니스 점수 계산 가중치
    WELLNESS_SCORE_WEIGHTS: Dict[str, float] = Field(
        default={
            "habit_completion": 0.4,
            "consistency": 0.3,
            "improvement": 0.3
        }
    )
    
    # AI 코칭 설정
    MAX_AI_MESSAGES_PER_DAY: Dict[str, int] = Field(
        default={
            "free": 5,
            "premium": 50,
            "pro": -1  # 무제한
        }
    )
    
    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        """설정 간 일관성을 검증합니다."""
        
        # 운영 환경에서는 DEBUG 모드 비활성화
        if self.ENVIRONMENT == "production" and self.DEBUG:
            raise ValueError("DEBUG는 운영 환경에서 False여야 합니다")
        
        # 운영 환경에서는 기본 SECRET_KEY 사용 금지
        if (self.ENVIRONMENT == "production" and 
            self.SECRET_KEY == "your-super-secret-key-change-in-production"):
            raise ValueError("운영 환경에서는 SECRET_KEY를 변경해야 합니다")
        
        # 운영 환경에서는 API 문서 비활성화
        if self.ENVIRONMENT == "production":
            self.DOCS_URL = None
            self.REDOC_URL = None
            self.OPENAPI_URL = None
        
        return self
    
    @property
    def database_url_sync(self) -> str:
        """동기 SQLAlchemy용 데이터베이스 URL을 반환합니다."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    
    @property
    def database_url_async(self) -> str:
        """비동기 SQLAlchemy용 데이터베이스 URL을 반환합니다."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부를 반환합니다."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """운영 환경 여부를 반환합니다."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        """테스트 환경 여부를 반환합니다."""
        return self.ENVIRONMENT == "testing"
    
    def configure_logging(self) -> None:
        """로깅 설정을 구성합니다."""
        log_level = getattr(logging, self.LOG_LEVEL.upper())
        
        logging.basicConfig(
            level=log_level,
            format=self.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
            ]
        )
        
        # 운영 환경에서는 파일 로깅도 활성화
        if self.LOG_FILE_PATH and self.is_production:
            file_handler = logging.FileHandler(self.LOG_FILE_PATH)
            file_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
            logging.getLogger().addHandler(file_handler)
    
    def get_oauth_config(self, provider: str) -> Dict[str, Any]:
        """소셜 로그인 제공자의 OAuth 설정을 반환합니다."""
        configs = {
            "kakao": {
                "client_id": self.KAKAO_CLIENT_ID,
                "client_secret": self.KAKAO_CLIENT_SECRET,
                "redirect_uri": self.KAKAO_REDIRECT_URI,
                "authorization_url": "https://kauth.kakao.com/oauth/authorize",
                "token_url": "https://kauth.kakao.com/oauth/token",
                "userinfo_url": "https://kapi.kakao.com/v2/user/me"
            },
            "naver": {
                "client_id": self.NAVER_CLIENT_ID,
                "client_secret": self.NAVER_CLIENT_SECRET,
                "redirect_uri": self.NAVER_REDIRECT_URI,
                "authorization_url": "https://nid.naver.com/oauth2.0/authorize",
                "token_url": "https://nid.naver.com/oauth2.0/token",
                "userinfo_url": "https://openapi.naver.com/v1/nid/me"
            },
            "google": {
                "client_id": self.GOOGLE_CLIENT_ID,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "redirect_uri": self.GOOGLE_REDIRECT_URI,
                "authorization_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo"
            }
        }
        
        if provider not in configs:
            raise ValueError(f"지원하지 않는 OAuth 제공자: {provider}")
        
        return configs[provider]


@lru_cache()
def get_settings() -> Settings:
    """
    설정 인스턴스를 반환합니다.
    
    @lru_cache 데코레이터를 사용하여 단일 인스턴스를 보장합니다.
    """
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
