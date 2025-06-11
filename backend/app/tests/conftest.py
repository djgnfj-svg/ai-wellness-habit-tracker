"""
pytest 설정 및 픽스처
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.base import BaseModel
from app.core.config import settings

# 테스트용 인메모리 데이터베이스
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 테스트용 비동기 엔진
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False,
)

# 테스트용 세션메이커
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """테스트용 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 데이터베이스 세션"""
    # 테스트 시작 전 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    # 세션 생성
    async with TestSessionLocal() as session:
        yield session
    
    # 테스트 후 테이블 정리
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture
def override_get_db(db: AsyncSession):
    """데이터베이스 의존성 오버라이드"""
    async def _override_get_db():
        yield db
    return _override_get_db


@pytest.fixture
def client(override_get_db) -> TestClient:
    """테스트 클라이언트"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트"""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_social_user_data():
    """소셜 로그인 테스트용 데이터"""
    return {
        "kakao": {
            "id": 12345678,
            "kakao_account": {
                "email": "test@kakao.com",
                "profile": {
                    "nickname": "테스트사용자",
                    "profile_image_url": "https://example.com/profile.jpg"
                }
            }
        },
        "naver": {
            "response": {
                "id": "naver123",
                "email": "test@naver.com",
                "nickname": "네이버사용자",
                "profile_image": "https://example.com/naver.jpg"
            }
        },
        "google": {
            "id": "google123",
            "email": "test@gmail.com",
            "name": "구글사용자",
            "picture": "https://example.com/google.jpg"
        }
    }