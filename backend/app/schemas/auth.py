"""
인증 관련 스키마
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from .common import BaseSchema


class DeviceInfo(BaseModel):
    """디바이스 정보"""
    device_id: str = Field(..., description="고유 디바이스 ID")
    device_type: str = Field(..., description="디바이스 타입 (ios/android)")
    os_version: Optional[str] = Field(None, description="OS 버전")
    app_version: Optional[str] = Field(None, description="앱 버전")


class SocialLoginRequest(BaseModel):
    """소셜 로그인 요청"""
    access_token: str = Field(..., description="소셜 플랫폼 액세스 토큰")
    device_info: DeviceInfo


class KakaoLoginRequest(SocialLoginRequest):
    """카카오 로그인 요청"""
    pass


class NaverLoginRequest(SocialLoginRequest):
    """네이버 로그인 요청"""
    pass


class GoogleLoginRequest(SocialLoginRequest):
    """구글 로그인 요청"""
    pass


class TokenResponse(BaseSchema):
    """토큰 응답"""
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="만료 시간 (초)")


class UserBasicInfo(BaseSchema):
    """사용자 기본 정보 (로그인 응답용)"""
    id: str = Field(..., description="사용자 ID")
    email: EmailStr = Field(..., description="이메일")
    nickname: str = Field(..., description="닉네임")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    is_new_user: bool = Field(..., description="신규 사용자 여부")


class LoginResponse(BaseSchema):
    """로그인 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserBasicInfo


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str = Field(..., description="리프레시 토큰")


class LogoutRequest(BaseModel):
    """로그아웃 요청"""
    device_id: str = Field(..., description="디바이스 ID")


class TokenVerifyResponse(BaseSchema):
    """토큰 검증 응답"""
    user_id: str = Field(..., description="사용자 ID")
    email: EmailStr = Field(..., description="이메일")
    is_active: bool = Field(..., description="계정 활성 상태")


# OAuth 콜백 관련
class OAuthCallbackData(BaseModel):
    """오에이언스 콜백 데이터"""
    code: str = Field(..., description="인증 코드")
    state: Optional[str] = Field(None, description="상태값")


class SocialUserInfo(BaseModel):
    """소셜 플랫폼 사용자 정보"""
    provider: str = Field(..., description="제공자 (kakao/naver/google)")
    provider_user_id: str = Field(..., description="제공자 사용자 ID")
    email: EmailStr = Field(..., description="이메일")
    nickname: str = Field(..., description="닉네임")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지")
    additional_info: Optional[Dict[str, Any]] = Field(default_factory=dict)