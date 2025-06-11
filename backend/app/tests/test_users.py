"""
사용자 API 테스트
"""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, FitnessLevel, Gender
from app.services.user_service import UserService
from app.core.security import create_token_pair


class TestUsers:
    """사용자 API 테스트 클래스"""

    @pytest.fixture
    async def test_user(self, db: AsyncSession) -> User:
        """테스트용 사용자 생성"""
        user_service = UserService(db)
        user = await user_service.create_user(
            email="testuser@example.com",
            nickname="테스트사용자",
            birth_year=1990,
            gender="male"
        )
        return user

    @pytest.fixture
    def auth_headers(self, test_user: User) -> dict:
        """인증 헤더 생성"""
        tokens = create_token_pair(test_user.id)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @pytest.mark.asyncio
    async def test_get_user_profile_without_auth(self, async_client: AsyncClient):
        """인증 없이 프로필 조회 테스트"""
        response = await async_client.get("/api/v1/users/profile")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_user_profile(
        self, 
        async_client: AsyncClient, 
        test_user: User,
        auth_headers: dict
    ):
        """사용자 프로필 조회 테스트"""
        response = await async_client.get(
            "/api/v1/users/profile", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["nickname"] == "테스트사용자"
        assert data["birth_year"] == 1990

    @pytest.mark.asyncio
    async def test_update_user_profile(
        self, 
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """사용자 프로필 업데이트 테스트"""
        update_data = {
            "nickname": "수정된닉네임",
            "birth_year": 1995
        }
        
        response = await async_client.put(
            "/api/v1/users/profile",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "수정된닉네임"
        assert data["birth_year"] == 1995

    @pytest.mark.asyncio
    async def test_get_wellness_profile_not_found(
        self, 
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """웰니스 프로필 없을 때 테스트"""
        response = await async_client.get(
            "/api/v1/users/wellness-profile",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_wellness_profile(
        self, 
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """웰니스 프로필 생성 테스트"""
        wellness_data = {
            "fitness_level": "intermediate",
            "primary_goals": ["체중감량", "근력향상"],
            "preferred_workout_types": ["유산소", "근력운동"],
            "wake_up_time": "07:00",
            "sleep_time": "23:00"
        }
        
        response = await async_client.put(
            "/api/v1/users/wellness-profile",
            json=wellness_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fitness_level"] == "intermediate"
        assert "체중감량" in data["primary_goals"]
        assert data["wake_up_time"] == "07:00"

    @pytest.mark.asyncio
    async def test_get_personalization_data_not_found(
        self, 
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """개인화 데이터 없을 때 테스트"""
        response = await async_client.get(
            "/api/v1/users/personalization",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_personalization_data(
        self, 
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """개인화 데이터 생성 테스트"""
        personalization_data = {
            "motivation_style": "achievement",
            "communication_preference": "friendly",
            "coaching_frequency": "normal",
            "preferred_message_times": ["09:00", "18:00"]
        }
        
        response = await async_client.put(
            "/api/v1/users/personalization",
            json=personalization_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["motivation_style"] == "achievement"
        assert data["communication_preference"] == "friendly"
        assert "09:00" in data["preferred_message_times"]

    @pytest.mark.asyncio
    async def test_invalid_profile_update(
        self, 
        async_client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """잘못된 프로필 업데이트 테스트"""
        invalid_data = {
            "nickname": "a",  # 너무 짧음 (최소 2자)
            "birth_year": 2030  # 미래 연도
        }
        
        response = await async_client.put(
            "/api/v1/users/profile",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error