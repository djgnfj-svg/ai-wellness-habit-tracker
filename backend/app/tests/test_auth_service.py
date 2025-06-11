"""
인증 서비스 테스트

인증 관련 비즈니스 로직을 포괄적으로 테스트합니다.
- 소셜 로그인 플로우 (카카오, 네이버, 구글)
- JWT 토큰 생성 및 검증
- 토큰 갱신 로직
- 외부 API 호출 실패 처리
- 에러 시나리오 및 보안 검증
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.models.user import User, SocialAccount
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.exceptions import AuthenticationError, ExternalServiceError
from app.core.security import create_access_token, create_refresh_token


class TestAuthService:
    """인증 서비스 테스트 클래스"""

    @pytest.fixture
    async def auth_service(self, db: AsyncSession) -> AuthService:
        """테스트용 인증 서비스 인스턴스"""
        return AuthService(db)

    @pytest.fixture
    async def existing_user(self, db: AsyncSession) -> User:
        """이미 가입된 사용자 (기존 사용자 시나리오용)"""
        user_service = UserService(db)
        return await user_service.create_user(
            email="existing@test.com",
            nickname="기존사용자",
            birth_year=1990
        )

    @pytest.fixture
    def mock_kakao_response(self):
        """카카오 API 응답 모킹 데이터"""
        return {
            "id": 12345678,
            "kakao_account": {
                "email": "kakao@test.com",
                "profile": {
                    "nickname": "카카오사용자",
                    "profile_image_url": "https://example.com/kakao.jpg"
                }
            }
        }

    @pytest.fixture
    def mock_naver_response(self):
        """네이버 API 응답 모킹 데이터"""
        return {
            "response": {
                "id": "naver123456",
                "email": "naver@test.com",
                "nickname": "네이버사용자",
                "profile_image": "https://example.com/naver.jpg"
            }
        }

    @pytest.fixture
    def mock_google_response(self):
        """구글 API 응답 모킹 데이터"""
        return {
            "id": "google123456",
            "email": "google@test.com",
            "name": "구글사용자",
            "picture": "https://example.com/google.jpg"
        }

    # =================================================================
    # 카카오 로그인 테스트
    # =================================================================

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_kakao_login_new_user(
        self, 
        mock_client: MagicMock,
        auth_service: AuthService,
        mock_kakao_response: dict
    ):
        """카카오 로그인 - 신규 사용자 생성 테스트"""
        # Mock HTTP 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kakao_response
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 카카오 로그인 실행
        result = await auth_service.kakao_login("test_kakao_token")
        
        # 결과 검증
        assert result.token_type == "bearer"
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.user.email == "kakao@test.com"
        assert result.user.nickname == "카카오사용자"
        assert result.user.is_active is True
        assert result.user.is_verified is True

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_kakao_login_existing_user(
        self,
        mock_client: MagicMock,
        auth_service: AuthService,
        existing_user: User
    ):
        """카카오 로그인 - 기존 사용자 로그인 테스트"""
        # 기존 사용자 이메일로 카카오 응답 설정
        kakao_response = {
            "id": 87654321,
            "kakao_account": {
                "email": existing_user.email,  # 기존 사용자와 같은 이메일
                "profile": {
                    "nickname": "카카오닉네임",
                    "profile_image_url": "https://example.com/new.jpg"
                }
            }
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = kakao_response
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 카카오 로그인 실행
        result = await auth_service.kakao_login("test_token")
        
        # 기존 사용자로 로그인되어야 함
        assert result.user.id == existing_user.id
        assert result.user.email == existing_user.email
        # 마지막 로그인 시간이 업데이트되어야 함
        assert result.user.last_login_at is not None

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_kakao_login_no_email(
        self,
        mock_client: MagicMock,
        auth_service: AuthService
    ):
        """카카오 로그인 - 이메일 정보 없음 에러 테스트"""
        # 이메일이 없는 카카오 응답
        kakao_response = {
            "id": 12345678,
            "kakao_account": {
                # email 필드가 없음
                "profile": {
                    "nickname": "카카오사용자"
                }
            }
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = kakao_response
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 이메일 없음 에러 발생해야 함
        with pytest.raises(AuthenticationError, match="이메일 정보를 가져올 수 없습니다"):
            await auth_service.kakao_login("test_token")

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_kakao_api_failure(
        self,
        mock_client: MagicMock,
        auth_service: AuthService
    ):
        """카카오 API 호출 실패 테스트"""
        # HTTP 401 응답 (잘못된 토큰)
        mock_response = MagicMock()
        mock_response.status_code = 401
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ExternalServiceError, match="카카오 API 호출 실패"):
            await auth_service.kakao_login("invalid_token")

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_kakao_network_timeout(
        self,
        mock_client: MagicMock,
        auth_service: AuthService
    ):
        """카카오 API 네트워크 타임아웃 테스트"""
        # 타임아웃 예외 발생
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ExternalServiceError, match="카카오 API 호출 시간 초과"):
            await auth_service.kakao_login("test_token")

    # =================================================================
    # 네이버 로그인 테스트
    # =================================================================

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_naver_login_success(
        self,
        mock_client: MagicMock,
        auth_service: AuthService,
        mock_naver_response: dict
    ):
        """네이버 로그인 성공 테스트"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_naver_response
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await auth_service.naver_login("naver_token")
        
        assert result.user.email == "naver@test.com"
        assert result.user.nickname == "네이버사용자"
        assert result.access_token is not None

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_naver_login_no_email(
        self,
        mock_client: MagicMock,
        auth_service: AuthService
    ):
        """네이버 로그인 - 이메일 없음 에러 테스트"""
        naver_response = {
            "response": {
                "id": "naver123",
                "nickname": "네이버사용자"
                # email 필드 없음
            }
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = naver_response
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(AuthenticationError, match="이메일 정보를 가져올 수 없습니다"):
            await auth_service.naver_login("test_token")

    # =================================================================
    # 구글 로그인 테스트
    # =================================================================

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_google_login_success(
        self,
        mock_client: MagicMock,
        auth_service: AuthService,
        mock_google_response: dict
    ):
        """구글 로그인 성공 테스트"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_google_response
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await auth_service.google_login("google_token")
        
        assert result.user.email == "google@test.com"
        assert result.user.nickname == "구글사용자"
        assert result.access_token is not None

    # =================================================================
    # 토큰 갱신 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        auth_service: AuthService,
        existing_user: User
    ):
        """리프레시 토큰 갱신 성공 테스트"""
        # 유효한 리프레시 토큰 생성
        data = {"sub": str(existing_user.id)}
        refresh_token = create_refresh_token(data=data)
        
        # 토큰 갱신 실행
        new_tokens = await auth_service.refresh_access_token(refresh_token)
        
        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None
        assert new_tokens.token_type == "bearer"
        # 새로운 토큰은 기존과 달라야 함
        assert new_tokens.refresh_token != refresh_token

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_service: AuthService):
        """잘못된 리프레시 토큰 갱신 테스트"""
        invalid_token = "invalid.refresh.token"
        
        with pytest.raises(AuthenticationError, match="유효하지 않은 리프레시 토큰"):
            await auth_service.refresh_access_token(invalid_token)

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(self, auth_service: AuthService):
        """존재하지 않는 사용자의 리프레시 토큰 갱신 테스트"""
        # 존재하지 않는 사용자 ID로 토큰 생성
        non_existent_user_id = str(uuid4())
        data = {"sub": non_existent_user_id}
        refresh_token = create_refresh_token(data=data)
        
        with pytest.raises(AuthenticationError, match="사용자를 찾을 수 없거나 비활성화된"):
            await auth_service.refresh_access_token(refresh_token)

    @pytest.mark.asyncio
    async def test_refresh_token_deactivated_user(
        self,
        auth_service: AuthService,
        existing_user: User,
        db: AsyncSession
    ):
        """비활성화된 사용자의 리프레시 토큰 갱신 테스트"""
        # 사용자 비활성화
        user_service = UserService(db)
        await user_service.deactivate_user(existing_user.id)
        
        # 비활성화된 사용자의 토큰으로 갱신 시도
        data = {"sub": str(existing_user.id)}
        refresh_token = create_refresh_token(data=data)
        
        with pytest.raises(AuthenticationError, match="사용자를 찾을 수 없거나 비활성화된"):
            await auth_service.refresh_access_token(refresh_token)

    # =================================================================
    # 소셜 계정 관리 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_social_account_creation_and_update(
        self,
        auth_service: AuthService,
        existing_user: User
    ):
        """소셜 계정 생성 및 업데이트 테스트"""
        # 첫 번째 소셜 계정 생성
        social_account = await auth_service._create_or_update_social_account(
            user_id=existing_user.id,
            provider="kakao",
            provider_user_id="kakao123",
            access_token="token1"
        )
        
        assert social_account.user_id == existing_user.id
        assert social_account.provider == "kakao"
        assert social_account.access_token == "token1"
        
        # 같은 제공자로 토큰 업데이트
        updated_account = await auth_service._create_or_update_social_account(
            user_id=existing_user.id,
            provider="kakao",
            provider_user_id="kakao123",
            access_token="token2"  # 새 토큰
        )
        
        # 같은 ID여야 하고 토큰만 업데이트되어야 함
        assert updated_account.id == social_account.id
        assert updated_account.access_token == "token2"

    @pytest.mark.asyncio
    async def test_multiple_social_providers_same_user(
        self,
        auth_service: AuthService,
        existing_user: User
    ):
        """한 사용자가 여러 소셜 제공자 연동 테스트"""
        # 카카오 계정 연동
        kakao_account = await auth_service._create_or_update_social_account(
            user_id=existing_user.id,
            provider="kakao",
            provider_user_id="kakao123",
            access_token="kakao_token"
        )
        
        # 구글 계정 연동 (같은 사용자)
        google_account = await auth_service._create_or_update_social_account(
            user_id=existing_user.id,
            provider="google",
            provider_user_id="google456",
            access_token="google_token"
        )
        
        # 다른 계정이어야 하지만 같은 사용자
        assert kakao_account.id != google_account.id
        assert kakao_account.user_id == google_account.user_id == existing_user.id
        assert kakao_account.provider == "kakao"
        assert google_account.provider == "google"

    # =================================================================
    # 계정 관리 테스트
    # =================================================================

    @pytest.mark.asyncio
    async def test_logout_user(self, auth_service: AuthService, existing_user: User):
        """사용자 로그아웃 테스트"""
        result = await auth_service.logout_user(existing_user.id)
        assert result is True
        # TODO: 실제 토큰 블랙리스트 구현 시 추가 검증

    @pytest.mark.asyncio
    async def test_delete_user_account(
        self,
        auth_service: AuthService,
        existing_user: User,
        db: AsyncSession
    ):
        """계정 탈퇴 처리 테스트"""
        result = await auth_service.delete_user_account(existing_user.id)
        assert result is True
        
        # 사용자가 비활성화되었는지 확인
        user_service = UserService(db)
        updated_user = await user_service.get_user_by_id(existing_user.id)
        assert updated_user.is_active is False

    # =================================================================
    # 보안 및 에러 처리 테스트
    # =================================================================

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_social_login_network_error_handling(
        self,
        mock_client: MagicMock,
        auth_service: AuthService
    ):
        """소셜 로그인 네트워크 에러 처리 테스트"""
        # 네트워크 연결 에러 시뮬레이션
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ExternalServiceError, match="네트워크 오류"):
            await auth_service.kakao_login("test_token")

    @pytest.mark.asyncio
    @patch("app.services.auth_service.httpx.AsyncClient")
    async def test_social_login_malformed_response(
        self,
        mock_client: MagicMock,
        auth_service: AuthService
    ):
        """소셜 로그인 잘못된 응답 형식 처리 테스트"""
        # 잘못된 JSON 응답
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(AuthenticationError):
            await auth_service.kakao_login("test_token")

    @pytest.mark.asyncio
    async def test_token_with_wrong_type(self, auth_service: AuthService, existing_user: User):
        """잘못된 토큰 타입으로 갱신 시도 테스트"""
        # 액세스 토큰을 리프레시 토큰처럼 사용
        data = {"sub": str(existing_user.id)}
        access_token = create_access_token(data=data)
        
        with pytest.raises(AuthenticationError):
            await auth_service.refresh_access_token(access_token)

    @pytest.mark.asyncio
    async def test_token_generation_consistency(self, auth_service: AuthService, existing_user: User):
        """토큰 생성 일관성 테스트"""
        # 같은 사용자로 여러 번 토큰 생성
        tokens1 = await auth_service._create_tokens(existing_user.id)
        tokens2 = await auth_service._create_tokens(existing_user.id)
        
        # 토큰은 달라야 하지만 형식은 동일해야 함
        assert tokens1.access_token != tokens2.access_token
        assert tokens1.refresh_token != tokens2.refresh_token
        assert tokens1.token_type == tokens2.token_type == "bearer"
