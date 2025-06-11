"""
기본 모델 클래스
모든 모델에서 공통으로 사용하는 필드들
"""
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base
import uuid


class BaseModel(Base):
    """모든 모델의 기본 클래스"""
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    @declared_attr
    def __tablename__(cls):
        """테이블명 자동 생성 (클래스명의 소문자 + s)"""
        return cls.__name__.lower() + 's'