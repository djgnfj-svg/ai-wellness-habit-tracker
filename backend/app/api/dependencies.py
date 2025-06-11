"""
공통 의존성 함수들
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.core.exceptions import authentication_exception
from app.models.user import User
from app.services.user_service import UserService

# Security scheme
security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """현재 사용자 토큰 검증"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise authentication_exception("유효하지 않은 토큰입니다")
    except JWTError:
        raise authentication_exception("토큰 검증에 실패했습니다")
    
    return user_id


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_token)
) -> User:
    """현재 로그인된 사용자 조회"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise authentication_exception("사용자를 찾을 수 없습니다")
    
    if not user.is_active:
        raise authentication_exception("비활성화된 계정입니다")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """활성화된 현재 사용자"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다"
        )
    return current_user


# 옵셔널 인증 (토큰이 있으면 사용자 정보를 가져오고, 없으면 None)
async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """선택적 사용자 인증 (토큰이 없어도 오류가 발생하지 않음)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        return user if user and user.is_active else None
        
    except JWTError:
        return None


class RateLimitDependency:
    """Rate Limiting 의존성"""
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def __call__(self, request) -> None:
        # TODO: Redis를 사용한 Rate Limiting 구현
        # 현재는 단순히 pass하고 나중에 구현
        pass


# 공통 Rate Limiting 인스턴스들
standard_rate_limit = RateLimitDependency(max_requests=60, window_seconds=60)
auth_rate_limit = RateLimitDependency(max_requests=10, window_seconds=60)