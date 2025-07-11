"""
보안 관련 유틸리티
JWT 토큰, 비밀번호 해싱 등
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings
import secrets
import string

# 비밀번호 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 알고리즘
ALGORITHM = "HS256"


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Access Token 생성
    
    Args:
        data: 토큰에 포함할 데이터 ({"sub": user_id})
        expires_delta: 만료 시간 (기본값: 설정값 사용)
    
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            hours=settings.ACCESS_TOKEN_EXPIRE_HOURS
        )
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Refresh Token 생성
    
    Args:
        data: 토큰에 포함할 데이터 ({"sub": user_id})
        expires_delta: 만료 시간 (기본값: 설정값 사용)
    
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 검증
    
    Args:
        token: JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")
    
    Returns:
        토큰 페이로드 또는 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            return None
            
        return payload
        
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
    
    Returns:
        검증 결과
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱
    
    Args:
        password: 평문 비밀번호
    
    Returns:
        해시된 비밀번호
    """
    return pwd_context.hash(password)


def generate_random_string(length: int = 32) -> str:
    """
    랜덤 문자열 생성 (API 키, 토큰 등에 사용)
    
    Args:
        length: 문자열 길이
    
    Returns:
        랜덤 문자열
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_token_pair(user_id: Union[str, int]) -> Dict[str, Any]:
    """
    Access Token과 Refresh Token 쌍 생성
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        토큰 쌍 딕셔너리
    """
    data = {"sub": str(user_id)}
    
    access_token = create_access_token(data=data)
    refresh_token = create_refresh_token(data=data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    }
