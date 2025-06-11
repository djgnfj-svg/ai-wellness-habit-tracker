"""
WellnessAI 데이터베이스 연결 및 세션 관리

이 모듈은 PostgreSQL과 Redis 연결을 관리하고,
데이터베이스 세션, 트랜잭션, 헬스체크 등의 기능을 제공합니다.
"""
import asyncio
import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional, Type, TypeVar

import redis.asyncio as aioredis
import redis
from sqlalchemy import MetaData, create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .config import settings

logger = logging.getLogger(__name__)

# Type variable for model classes
ModelType = TypeVar("ModelType", bound="Base")

# ===== 메타데이터 설정 =====
# Naming convention for database constraints
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# SQLAlchemy Base 클래스
Base = declarative_base(metadata=metadata)

# ===== PostgreSQL 연결 설정 =====

def create_database_engine(is_async: bool = False):
    """
    데이터베이스 엔진을 생성합니다.
    
    Args:
        is_async: 비동기 엔진 여부
        
    Returns:
        SQLAlchemy engine instance
    """
    database_url = settings.database_url_async if is_async else settings.database_url_sync
    
    engine_kwargs = {
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
        "pool_recycle": settings.DATABASE_POOL_RECYCLE,
        "pool_pre_ping": True,  # 연결 상태 확인
        "echo": settings.DEBUG,  # SQL 쿼리 로깅
        "poolclass": QueuePool,
    }
    
    if is_async:
        return create_async_engine(database_url, **engine_kwargs)
    else:
        return create_engine(database_url, **engine_kwargs)

# 동기 엔진 및 세션
sync_engine = create_database_engine(is_async=False)
SyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=sync_engine,
    expire_on_commit=False
)

# 비동기 엔진 및 세션  
async_engine = create_database_engine(is_async=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# ===== 데이터베이스 이벤트 핸들러 =====

@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """SQLite 연결시 설정을 적용합니다 (테스트용)."""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@event.listens_for(sync_engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 전 로깅."""
    if settings.DEBUG:
        logger.debug(f"Query: {statement}")
        logger.debug(f"Parameters: {parameters}")

# ===== Redis 연결 설정 =====

class RedisManager:
    """Redis 연결을 관리하는 클래스."""
    
    def __init__(self):
        self.sync_client: Optional[redis.Redis] = None
        self.async_client: Optional[aioredis.Redis] = None
        self._connection_pool = None
        self._async_connection_pool = None
    
    def get_sync_client(self) -> redis.Redis:
        """동기 Redis 클라이언트를 반환합니다."""
        if self.sync_client is None:
            try:
                self.sync_client = redis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                    decode_responses=True,
                    health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL
                )
                # 연결 테스트
                self.sync_client.ping()
                logger.info("Redis 동기 클라이언트 연결 성공")
            except Exception as e:
                logger.error(f"Redis 동기 클라이언트 연결 실패: {e}")
                self.sync_client = None
        
        return self.sync_client
    
    async def get_async_client(self) -> aioredis.Redis:
        """비동기 Redis 클라이언트를 반환합니다."""
        if self.async_client is None:
            try:
                self.async_client = aioredis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                    decode_responses=True,
                    health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL
                )
                # 연결 테스트
                await self.async_client.ping()
                logger.info("Redis 비동기 클라이언트 연결 성공")
            except Exception as e:
                logger.error(f"Redis 비동기 클라이언트 연결 실패: {e}")
                self.async_client = None
        
        return self.async_client
    
    def close_sync_client(self):
        """동기 Redis 클라이언트를 종료합니다."""
        if self.sync_client:
            self.sync_client.close()
            self.sync_client = None
    
    async def close_async_client(self):
        """비동기 Redis 클라이언트를 종료합니다."""
        if self.async_client:
            await self.async_client.close()
            self.async_client = None

# Redis 매니저 인스턴스
redis_manager = RedisManager()

# ===== 데이터베이스 세션 관리 =====

def get_db() -> Generator[Session, None, None]:
    """
    동기 데이터베이스 세션 의존성을 제공합니다.
    
    Yields:
        Session: SQLAlchemy 세션 인스턴스
    """
    db = SyncSessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 세션 에러: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션 의존성을 제공합니다.
    
    Yields:
        AsyncSession: 비동기 SQLAlchemy 세션 인스턴스
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception as e:
            logger.error(f"비동기 데이터베이스 세션 에러: {e}")
            await db.rollback()
            raise

def get_redis() -> Optional[redis.Redis]:
    """
    동기 Redis 클라이언트를 반환합니다.
    
    Returns:
        Redis 클라이언트 또는 None (연결 실패시)
    """
    return redis_manager.get_sync_client()

async def get_async_redis() -> Optional[aioredis.Redis]:
    """
    비동기 Redis 클라이언트를 반환합니다.
    
    Returns:
        비동기 Redis 클라이언트 또는 None (연결 실패시)
    """
    return await redis_manager.get_async_client()

# ===== 트랜잭션 관리 =====

@contextmanager
def db_transaction():
    """
    데이터베이스 트랜잭션 컨텍스트 매니저.
    
    Example:
        with db_transaction() as db:
            user = User(email="test@example.com")
            db.add(user)
            # 컨텍스트 종료시 자동 커밋, 에러 발생시 롤백
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
        logger.debug("트랜잭션 커밋 완료")
    except Exception as e:
        logger.error(f"트랜잭션 롤백: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@asynccontextmanager
async def async_db_transaction():
    """
    비동기 데이터베이스 트랜잭션 컨텍스트 매니저.
    
    Example:
        async with async_db_transaction() as db:
            user = User(email="test@example.com")
            db.add(user)
            # 컨텍스트 종료시 자동 커밋, 에러 발생시 롤백
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
            logger.debug("비동기 트랜잭션 커밋 완료")
        except Exception as e:
            logger.error(f"비동기 트랜잭션 롤백: {e}")
            await db.rollback()
            raise

# ===== 헬스체크 기능 =====

class DatabaseHealthCheck:
    """데이터베이스 연결 상태를 확인하는 클래스."""
    
    @staticmethod
    def check_postgres() -> bool:
        """PostgreSQL 연결 상태를 확인합니다."""
        try:
            with SyncSessionLocal() as db:
                result = db.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"PostgreSQL 헬스체크 실패: {e}")
            return False
    
    @staticmethod
    async def check_postgres_async() -> bool:
        """PostgreSQL 비동기 연결 상태를 확인합니다."""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"PostgreSQL 비동기 헬스체크 실패: {e}")
            return False
    
    @staticmethod
    def check_redis() -> bool:
        """Redis 연결 상태를 확인합니다."""
        try:
            client = redis_manager.get_sync_client()
            if client:
                return client.ping()
            return False
        except Exception as e:
            logger.error(f"Redis 헬스체크 실패: {e}")
            return False
    
    @staticmethod
    async def check_redis_async() -> bool:
        """Redis 비동기 연결 상태를 확인합니다."""
        try:
            client = await redis_manager.get_async_client()
            if client:
                return await client.ping()
            return False
        except Exception as e:
            logger.error(f"Redis 비동기 헬스체크 실패: {e}")
            return False
    
    @staticmethod
    def check_all() -> dict:
        """모든 데이터베이스 연결 상태를 확인합니다."""
        return {
            "postgres": DatabaseHealthCheck.check_postgres(),
            "redis": DatabaseHealthCheck.check_redis()
        }
    
    @staticmethod
    async def check_all_async() -> dict:
        """모든 데이터베이스 비동기 연결 상태를 확인합니다."""
        postgres_task = DatabaseHealthCheck.check_postgres_async()
        redis_task = DatabaseHealthCheck.check_redis_async()
        
        postgres_result, redis_result = await asyncio.gather(
            postgres_task, redis_task, return_exceptions=True
        )
        
        return {
            "postgres": postgres_result if isinstance(postgres_result, bool) else False,
            "redis": redis_result if isinstance(redis_result, bool) else False
        }

# ===== 데이터베이스 유틸리티 =====

def create_all_tables():
    """모든 테이블을 생성합니다."""
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"테이블 생성 실패: {e}")
        raise

def drop_all_tables():
    """모든 테이블을 삭제합니다 (주의: 운영환경에서 사용 금지)."""
    if settings.is_production:
        raise RuntimeError("운영환경에서는 테이블 삭제가 금지됩니다")
    
    try:
        Base.metadata.drop_all(bind=sync_engine)
        logger.warning("모든 데이터베이스 테이블이 삭제되었습니다")
    except Exception as e:
        logger.error(f"테이블 삭제 실패: {e}")
        raise

async def init_db():
    """데이터베이스를 초기화합니다."""
    # 테이블 생성
    create_all_tables()
    
    # 초기 데이터 삽입 (필요한 경우)
    logger.info("데이터베이스 초기화 완료")

async def close_db_connections():
    """모든 데이터베이스 연결을 종료합니다."""
    # 엔진 종료
    sync_engine.dispose()
    await async_engine.aclose()
    
    # Redis 연결 종료
    redis_manager.close_sync_client()
    await redis_manager.close_async_client()
    
    logger.info("모든 데이터베이스 연결이 종료되었습니다")

# ===== 데이터베이스 세션 데코레이터 =====

def with_db_session(func):
    """
    함수에 데이터베이스 세션을 자동으로 주입하는 데코레이터.
    
    사용법:
        @with_db_session
        def create_user(db: Session, email: str):
            user = User(email=email)
            db.add(user)
            db.commit()
            return user
    """
    def wrapper(*args, **kwargs):
        with db_transaction() as db:
            return func(db, *args, **kwargs)
    return wrapper

def with_async_db_session(func):
    """
    비동기 함수에 데이터베이스 세션을 자동으로 주입하는 데코레이터.
    
    사용법:
        @with_async_db_session
        async def create_user(db: AsyncSession, email: str):
            user = User(email=email)
            db.add(user)
            await db.commit()
            return user
    """
    async def wrapper(*args, **kwargs):
        async with async_db_transaction() as db:
            return await func(db, *args, **kwargs)
    return wrapper

# ===== 전역 인스턴스 =====

# 헬스체크 인스턴스
health_check = DatabaseHealthCheck()

# 로거 설정
logger.info("데이터베이스 모듈 초기화 완료")
