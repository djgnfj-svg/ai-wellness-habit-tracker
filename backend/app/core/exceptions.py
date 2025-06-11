"""
커스텀 예외 클래스들
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class WellnessAIException(Exception):
    """기본 예외 클래스"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(WellnessAIException):
    """인증 오류"""
    pass


class AuthorizationError(WellnessAIException):
    """권한 오류"""
    pass


class ValidationError(WellnessAIException):
    """검증 오류"""
    pass


class NotFoundError(WellnessAIException):
    """리소스를 찾을 수 없음"""
    pass


class ConflictError(WellnessAIException):
    """중복 리소스 오류"""
    pass


class ExternalServiceError(WellnessAIException):
    """외부 서비스 오류 (소셜 로그인 등)"""
    pass


# HTTP 예외 헬퍼 함수들
def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """HTTP 예외 생성 헬퍼"""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {}
        }
    )


def authentication_exception(message: str = "인증이 필요합니다") -> HTTPException:
    """인증 예외"""
    return create_http_exception(status.HTTP_401_UNAUTHORIZED, message)


def authorization_exception(message: str = "권한이 없습니다") -> HTTPException:
    """권한 예외"""
    return create_http_exception(status.HTTP_403_FORBIDDEN, message)


def not_found_exception(message: str = "리소스를 찾을 수 없습니다") -> HTTPException:
    """Not Found 예외"""
    return create_http_exception(status.HTTP_404_NOT_FOUND, message)


def conflict_exception(message: str = "이미 존재하는 리소스입니다") -> HTTPException:
    """Conflict 예외"""
    return create_http_exception(status.HTTP_409_CONFLICT, message)


def validation_exception(message: str = "입력값이 올바르지 않습니다") -> HTTPException:
    """Validation 예외"""
    return create_http_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, message)
