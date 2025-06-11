"""
공통 의존성 함수들
FastAPI 의존성 주입을 위한 함수들을 정의합니다.
- 데이터베이스 세션 관리
- 사용자 인증 및 권한 확인
- Rate Limiting (추후 구현)
"""
from typing import Generator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.core.exceptions import authentication_exception, authorization_exception
from app.models.user import User
from app.services.user_service import UserService

# HTTP Bearer 토큰 스키마 정의
security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    데이터베이스 세션 의존성
    
    FastAPI 의존성 주입을 통해 데이터베이스 세션을 제공합니다.
    각 요청마다 새로운 세션을 생성하고, 요청 완료 후 자동으로 정리합니다.
    
    Yields:
        AsyncSession: 비동기 데이터베이스 세션
        
    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # 데이터베이스 작업 수행
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    현재 사용자의 JWT 토큰을 검증하고 사용자 ID를 반환
    
    HTTP Authorization 헤더에서 Bearer 토큰을 추출하고 검증합니다.
    토큰이 유효하지 않거나 만료된 경우 401 예외를 발생시킵니다.
    
    Args:
        credentials: HTTP Bearer 토큰 자격증명
        
    Returns:
        str: 토큰에서 추출한 사용자 ID (UUID 문자열)
        
    Raises:
        HTTPException: 토큰이 유효하지 않거나 만료된 경우 (401)
        
    Example:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user_token)):
            # user_id를 사용한 작업
            pass
    """
    token = credentials.credentials
    
    # verify_token 함수를 사용하여 토큰 검증
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        raise authentication_exception("유효하지 않거나 만료된 토큰입니다")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise authentication_exception("토큰에 사용자 정보가 없습니다")
    
    return user_id


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_token)
) -> User:
    """
    현재 로그인된 사용자 정보를 조회
    
    토큰에서 추출한 사용자 ID로 데이터베이스에서 사용자 정보를 조회합니다.
    사용자가 존재하지 않거나 비활성화된 경우 401 예외를 발생시킵니다.
    
    Args:
        db: 데이터베이스 세션
        user_id: 토큰에서 추출한 사용자 ID
        
    Returns:
        User: 현재 로그인된 사용자 모델 인스턴스
        
    Raises:
        HTTPException: 사용자를 찾을 수 없거나 비활성화된 경우 (401)
        
    Example:
        @app.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id, "email": current_user.email}
    """
    try:
        # 문자열 user_id를 UUID로 변환
        user_uuid = UUID(user_id)
    except ValueError:
        raise authentication_exception("올바르지 않은 사용자 ID 형식입니다")
    
    # 사용자 서비스를 통해 사용자 조회
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_uuid)
    
    if not user:
        raise authentication_exception("사용자를 찾을 수 없습니다")
    
    if not user.is_active:
        raise authentication_exception("비활성화된 계정입니다")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    활성화된 현재 사용자 확인 (추가 검증)
    
    이미 get_current_user에서 활성화 상태를 확인하지만,
    추가적인 보안 검증이 필요한 경우 사용할 수 있습니다.
    
    Args:
        current_user: 현재 로그인된 사용자
        
    Returns:
        User: 활성화된 사용자 모델 인스턴스
        
    Raises:
        HTTPException: 비활성화된 사용자인 경우 (400)
        
    Note:
        현재는 get_current_user와 동일한 검증을 수행하므로 중복이지만,
        향후 추가적인 권한 검증이 필요한 경우를 위해 유지합니다.
    """
    if not current_user.is_active:
        raise authorization_exception("비활성화된 사용자입니다")
    return current_user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    """
    선택적 사용자 인증 (토큰이 없어도 오류가 발생하지 않음)
    
    토큰이 제공된 경우에만 사용자를 인증하고, 토큰이 없거나 
    유효하지 않은 경우에는 None을 반환합니다. 
    공개 API 중에서 로그인된 사용자에게는 추가 정보를 제공하고 싶을 때 사용합니다.
    
    Args:
        db: 데이터베이스 세션
        credentials: 선택적 HTTP Bearer 토큰 자격증명
        
    Returns:
        Optional[User]: 인증된 사용자 또는 None
        
    Example:
        @app.get("/public-content")
        async def public_content(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # 로그인된 사용자에게 추가 정보 제공
                return {"content": "...", "personalized": True}
            else:
                # 공개 내용만 제공
                return {"content": "...", "personalized": False}
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        
        if payload is None:
            return None
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        
        # UUID 변환 시도
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None
            
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        # 사용자가 존재하고 활성화된 경우에만 반환
        return user if user and user.is_active else None
        
    except Exception:
        # 모든 예외는 None을 반환 (선택적 인증이므로)
        return None


class RateLimitDependency:
    """
    Rate Limiting 의존성 클래스
    
    API 요청 빈도를 제한하여 서비스 남용을 방지합니다.
    현재는 기본 구조만 구현되어 있고, 실제 제한 로직은 추후 Redis를 통해 구현 예정입니다.
    
    Attributes:
        max_requests (int): 시간 윈도우 내 최대 허용 요청 수
        window_seconds (int): 시간 윈도우 크기 (초)
        
    Example:
        # 분당 30회로 제한
        strict_limit = RateLimitDependency(max_requests=30, window_seconds=60)
        
        @app.post("/sensitive-action")
        async def sensitive_action(_: None = Depends(strict_limit)):
            # 민감한 작업 수행
            pass
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        Rate Limiter 초기화
        
        Args:
            max_requests: 시간 윈도우 내 최대 허용 요청 수 (기본값: 60)
            window_seconds: 시간 윈도우 크기 초 단위 (기본값: 60)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def __call__(self, request: Request) -> None:
        """
        Rate Limiting 검사 수행
        
        현재는 placeholder로 항상 통과시키지만, 
        추후 Redis를 사용한 실제 Rate Limiting 로직으로 대체 예정입니다.
        
        Args:
            request: FastAPI Request 객체 (클라이언트 IP 추출용)
            
        Raises:
            HTTPException: Rate limit 초과 시 (429) - 추후 구현
            
        TODO:
            - Redis를 사용한 분산 Rate Limiting 구현
            - IP별, 사용자별 Rate Limiting 분리
            - 다양한 제한 정책 지원 (burst, sliding window 등)
        """
        # TODO: Redis를 사용한 Rate Limiting 구현
        # 
        # 구현 예시:
        # client_ip = request.client.host
        # redis_key = f"rate_limit:{client_ip}:{self.window_seconds}"
        # current_requests = await redis.incr(redis_key)
        # if current_requests == 1:
        #     await redis.expire(redis_key, self.window_seconds)
        # if current_requests > self.max_requests:
        #     raise HTTPException(
        #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        #         detail="Rate limit exceeded"
        #     )
        pass


# 공통 Rate Limiting 인스턴스들
# 다양한 엔드포인트에서 재사용할 수 있는 사전 정의된 Rate Limiter들

# 일반적인 API 요청용 (분당 60회)
standard_rate_limit = RateLimitDependency(max_requests=60, window_seconds=60)

# 인증 관련 API용 (보안상 더 엄격하게 제한 - 분당 10회)  
auth_rate_limit = RateLimitDependency(max_requests=10, window_seconds=60)

# 민감한 작업용 (시간당 5회)
strict_rate_limit = RateLimitDependency(max_requests=5, window_seconds=3600)
