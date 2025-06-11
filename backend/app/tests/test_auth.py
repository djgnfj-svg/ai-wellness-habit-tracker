"""
인증 API 테스트
"""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user_service import UserService


class TestAuth:
    """인증 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """헬스체크 테스트"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """루트 엔드포인트 테스트"""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data

    @pytest.mark.asyncio
    @patch("app.services.auth_service.AuthService._get_kakao_user_info")
    async def test_kakao_login_new_user(
        self, 
        mock_kakao_api: AsyncMock,
        async_client: AsyncClient, 
        mock_social_user_data: dict
    ):
        """카카오 로그인 - 신규 사용자 테스트"""
        # Mock 카카오 API 응답
        mock_kakao_api.return_value = mock_social_user_data["kakao"]
        
        # 로그인 요청
        response = await async_client.post(
            "/api/v1/auth/kakao/login",
            json={"access_token": "test_access_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 확인
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        
        # 사용자 정보 확인
        user_data = data["user"]
        assert user_data["email"] == "test@kakao.com"
        assert user_data["nickname"] == "테스트사용자"

    @pytest.mark.asyncio
    @patch("app.services.auth_service.AuthService._get_naver_user_info")
    async def test_naver_login(
        self, 
        mock_naver_api: AsyncMock,
        async_client: AsyncClient, 
        mock_social_user_data: dict
    ):
        """네이버 로그인 테스트"""
        mock_naver_api.return_value = mock_social_user_data["naver"]
        
        response = await async_client.post(
            "/api/v1/auth/naver/login",
            json={"access_token": "test_naver_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@naver.com"

    @pytest.mark.asyncio
    @patch("app.services.auth_service.AuthService._get_google_user_info")
    async def test_google_login(
        self, 
        mock_google_api: AsyncMock,
        async_client: AsyncClient, 
        mock_social_user_data: dict
    ):
        """구글 로그인 테스트"""
        mock_google_api.return_value = mock_social_user_data["google"]
        
        response = await async_client.post(
            "/api/v1/auth/google/login",
            json={"access_token": "test_google_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@gmail.com"

    @pytest.mark.asyncio
    async def test_invalid_social_login(self, async_client: AsyncClient):
        """잘못된 소셜 로그인 토큰 테스트"""
        response = await async_client.post(
            "/api/v1/auth/kakao/login",
            json={"access_token": "invalid_token"}
        )
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """잘못된 리프레시 토큰 테스트"""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_without_token(self, async_client: AsyncClient):
        """토큰 없이 사용자 정보 조회 테스트"""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No credentials provided

    @pytest.mark.asyncio
    async def test_me_with_invalid_token(self, async_client: AsyncClient):
        """잘못된 토큰으로 사용자 정보 조회 테스트"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401