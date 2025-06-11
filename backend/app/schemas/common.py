"""
공통 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime
from uuid import UUID


class ResponseBase(BaseModel):
    """기본 응답 스키마"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(ResponseBase):
    """성공 응답 스키마"""
    data: Optional[Any] = None


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(ResponseBase):
    """에러 응답 스키마"""
    success: bool = False
    error: ErrorDetail


class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""
    total_count: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(SuccessResponse):
    """페이지네이션된 응답"""
    data: List[Any]
    meta: PaginationMeta


class BaseSchema(BaseModel):
    """기본 스키마 클래스"""
    model_config = {"from_attributes": True}


class TimestampMixin(BaseModel):
    """타임스탬프 믹스인"""
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """ID 믹스인"""
    id: UUID