"""
인증 관리 서비스
소셜 로그인(카카오, 네이버, 구글) 처리 및 JWT 토큰 관리를 담당합니다.

주요 기능:
- 소셜 플랫폼 API 연동
- 사용자 정보 추출 및 검증
- JWT 토큰 생성 및 갱신
- 계정 탈퇴 처리
"""
import httpx
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User, SocialAccount
from app.schemas.auth import AuthResponse, Token
from app.services.user_service import UserService
from app.core.exceptions import AuthenticationError, ExternalServiceError


class AuthService:
    """
    인증 관리 서비스 클래스
    
    소셜 로그인과 JWT 토큰 관리를 담당하는 핵심 서비스입니다.
    각 소셜 플랫폼별로 다른 API 구조를 처리하고, 
    통일된 사용자 모델로 변환하여 관리합니다.
    
    Attributes:
        db (AsyncSession): 데이터베이스 세션
        user_service (UserService): 사용자 관리 서비스
    """
    
    def __init__(self, db: AsyncSession):
        """
        서비스 초기화
        
        Args:
            db: 비동기 데이터베이스 세션
        """
        self.db = db
        self.user_service = UserService(db)

    # =================================================================
    # 소셜 계정 관리 메서드
    # =================================================================

    async def _get_social_account(
        self, 
        user_id: UUID, 
        provider: str
    ) -> Optional[SocialAccount]:
        """
        사용자의 특정 소셜 계정 정보 조회
        
        Args:
            user_id: 사용자 ID
            provider: 소셜 제공자 (kakao, naver, google)
            
        Returns:
            SocialAccount 또는 None
        """
        stmt = select(SocialAccount).where(
            SocialAccount.user_id == user_id,
            SocialAccount.provider == provider
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _create_or_update_social_account(
        self,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> SocialAccount:
        """
        소셜 계정 정보 생성 또는 업데이트
        
        기존 소셜 계정이 있으면 토큰 정보를 업데이트하고,
        없으면 새로 생성합니다.
        
        Args:
            user_id: 사용자 ID
            provider: 소셜 제공자
            provider_user_id: 소셜 플랫폼에서의 사용자 ID
            access_token: 소셜 플랫폼 액세스 토큰
            refresh_token: 소셜 플랫폼 리프레시 토큰 (선택)
            expires_at: 토큰 만료 시간 (선택)
            
        Returns:
            SocialAccount: 생성/업데이트된 소셜 계정 정보
        """
        social_account = await self._get_social_account(user_id, provider)
        
        if social_account:
            # 기존 계정 업데이트 - 토큰 정보만 갱신
            social_account.access_token = access_token
            social_account.refresh_token = refresh_token
            social_account.expires_at = expires_at
        else:
            # 새 계정 생성
            social_account = SocialAccount(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            self.db.add(social_account)
        
        await self.db.commit()
        await self.db.refresh(social_account)
        return social_account

    # =================================================================
    # 소셜 플랫폼 API 연동 메서드
    # =================================================================

    async def _get_kakao_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        카카오 사용자 정보 조회
        
        카카오 API에서 사용자 정보를 가져옵니다.
        필수 정보(이메일)가 없으면 예외를 발생시킵니다.
        
        Args:
            access_token: 카카오 액세스 토큰
            
        Returns:
            Dict: 카카오 사용자 정보
            
        Raises:
            ExternalServiceError: 카카오 API 호출 실패
            
        Note:
            카카오 API 문서: https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise ExternalServiceError(
                        f"카카오 API 호출 실패: HTTP {response.status_code}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            raise ExternalServiceError("카카오 API 호출 시간 초과")
        except httpx.RequestError as e:
            raise ExternalServiceError(f"카카오 API 네트워크 오류: {str(e)}")

    async def _get_naver_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        네이버 사용자 정보 조회
        
        네이버 API에서 사용자 정보를 가져옵니다.
        
        Args:
            access_token: 네이버 액세스 토큰
            
        Returns:
            Dict: 네이버 사용자 정보
            
        Raises:
            ExternalServiceError: 네이버 API 호출 실패
            
        Note:
            네이버 API 문서: https://developers.naver.com/docs/login/api/api.md
        """
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://openapi.naver.com/v1/nid/me",
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise ExternalServiceError(
                        f"네이버 API 호출 실패: HTTP {response.status_code}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            raise ExternalServiceError("네이버 API 호출 시간 초과")
        except httpx.RequestError as e:
            raise ExternalServiceError(f"네이버 API 네트워크 오류: {str(e)}")

    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        구글 사용자 정보 조회
        
        구글 API에서 사용자 정보를 가져옵니다.
        
        Args:
            access_token: 구글 액세스 토큰
            
        Returns:
            Dict: 구글 사용자 정보
            
        Raises:
            ExternalServiceError: 구글 API 호출 실패
            
        Note:
            구글 API 문서: https://developers.google.com/identity/protocols/oauth2
        """
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise ExternalServiceError(
                        f"구글 API 호출 실패: HTTP {response.status_code}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            raise ExternalServiceError("구글 API 호출 시간 초과")
        except httpx.RequestError as e:
            raise ExternalServiceError(f"구글 API 네트워크 오류: {str(e)}")

    # =================================================================
    # 소셜 로그인 처리 메서드
    # =================================================================

    async def kakao_login(self, access_token: str) -> AuthResponse:
        """
        카카오 소셜 로그인 처리
        
        카카오 액세스 토큰을 검증하고 사용자 정보를 가져와서
        우리 시스템의 사용자로 등록하거나 로그인 처리합니다.
        
        Args:
            access_token: 프론트엔드에서 받은 카카오 액세스 토큰
            
        Returns:
            AuthResponse: JWT 토큰과 사용자 정보가 포함된 응답
            
        Raises:
            AuthenticationError: 인증 처리 중 오류 발생
            ExternalServiceError: 카카오 API 호출 실패
            
        Process:
            1. 카카오 API로 사용자 정보 조회
            2. 이메일 정보 확인 (필수)
            3. 기존 사용자 확인 또는 신규 사용자 생성
            4. 소셜 계정 정보 저장/업데이트
            5. JWT 토큰 생성 및 반환
        """
        try:
            # 1. 카카오 사용자 정보 조회
            kakao_user = await self._get_kakao_user_info(access_token)
            
            # 2. 필수 정보 추출 및 검증
            provider_user_id = str(kakao_user["id"])
            kakao_account = kakao_user.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            
            email = kakao_account.get("email")
            nickname = profile.get("nickname", f"카카오사용자{provider_user_id}")
            profile_image_url = profile.get("profile_image_url")
            
            if not email:
                raise AuthenticationError(
                    "카카오 계정에서 이메일 정보를 가져올 수 없습니다. "
                    "카카오 앱에서 이메일 제공에 동의해주세요."
                )
            
            # 3. 기존 사용자 확인 또는 신규 생성
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                # 신규 사용자 생성
                user = await self.user_service.create_user(
                    email=email,
                    nickname=nickname,
                    profile_image_url=profile_image_url
                )
            
            # 4. 소셜 계정 정보 저장/업데이트
            await self._create_or_update_social_account(
                user_id=user.id,
                provider="kakao",
                provider_user_id=provider_user_id,
                access_token=access_token
            )
            
            # 5. 마지막 로그인 시간 업데이트
            await self.user_service.update_last_login(user.id)
            
            # 6. JWT 토큰 생성
            tokens = await self._create_tokens(user.id)
            
            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                user=user
            )
            
        except (AuthenticationError, ExternalServiceError):
            # 이미 정의된 예외는 그대로 전파
            raise
        except Exception as e:
            # 예상치 못한 오류는 AuthenticationError로 래핑
            raise AuthenticationError(f"카카오 로그인 처리 중 오류 발생: {str(e)}")

    async def naver_login(self, access_token: str) -> AuthResponse:
        """
        네이버 소셜 로그인 처리
        
        Args:
            access_token: 네이버 액세스 토큰
            
        Returns:
            AuthResponse: JWT 토큰과 사용자 정보
        """
        try:
            # 네이버 사용자 정보 조회
            naver_response = await self._get_naver_user_info(access_token)
            naver_user = naver_response.get("response", {})
            
            provider_user_id = naver_user.get("id")
            email = naver_user.get("email")
            nickname = naver_user.get("nickname", f"네이버사용자{provider_user_id}")
            profile_image_url = naver_user.get("profile_image")
            
            if not email:
                raise AuthenticationError(
                    "네이버 계정에서 이메일 정보를 가져올 수 없습니다"
                )
            
            # 사용자 생성/조회 및 토큰 처리 (카카오와 동일한 로직)
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                user = await self.user_service.create_user(
                    email=email,
                    nickname=nickname,
                    profile_image_url=profile_image_url
                )
            
            await self._create_or_update_social_account(
                user_id=user.id,
                provider="naver",
                provider_user_id=provider_user_id,
                access_token=access_token
            )
            
            await self.user_service.update_last_login(user.id)
            tokens = await self._create_tokens(user.id)
            
            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                user=user
            )
            
        except (AuthenticationError, ExternalServiceError):
            raise
        except Exception as e:
            raise AuthenticationError(f"네이버 로그인 처리 중 오류 발생: {str(e)}")

    async def google_login(self, access_token: str) -> AuthResponse:
        """
        구글 소셜 로그인 처리
        
        Args:
            access_token: 구글 액세스 토큰
            
        Returns:
            AuthResponse: JWT 토큰과 사용자 정보
        """
        try:
            # 구글 사용자 정보 조회
            google_user = await self._get_google_user_info(access_token)
            
            provider_user_id = google_user.get("id")
            email = google_user.get("email")
            nickname = google_user.get("name", f"구글사용자{provider_user_id}")
            profile_image_url = google_user.get("picture")
            
            if not email:
                raise AuthenticationError(
                    "구글 계정에서 이메일 정보를 가져올 수 없습니다"
                )
            
            # 사용자 생성/조회 및 토큰 처리
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                user = await self.user_service.create_user(
                    email=email,
                    nickname=nickname,
                    profile_image_url=profile_image_url
                )
            
            await self._create_or_update_social_account(
                user_id=user.id,
                provider="google",
                provider_user_id=provider_user_id,
                access_token=access_token
            )
            
            await self.user_service.update_last_login(user.id)
            tokens = await self._create_tokens(user.id)
            
            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                user=user
            )
            
        except (AuthenticationError, ExternalServiceError):
            raise
        except Exception as e:
            raise AuthenticationError(f"구글 로그인 처리 중 오류 발생: {str(e)}")

    # =================================================================
    # JWT 토큰 관리 메서드  
    # =================================================================

    async def _create_tokens(self, user_id: UUID) -> Token:
        """
        JWT 토큰 쌍 생성 (Access Token + Refresh Token)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Token: 생성된 토큰 쌍
        """
        data = {"sub": str(user_id)}
        
        access_token = create_access_token(
            data=data,
            expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        )
        
        refresh_token = create_refresh_token(
            data=data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        리프레시 토큰으로 새로운 액세스 토큰 발급
        
        Args:
            refresh_token: 리프레시 토큰
            
        Returns:
            Token: 새로운 토큰 쌍
            
        Raises:
            AuthenticationError: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
        """
        try:
            # 리프레시 토큰 검증
            payload = verify_token(refresh_token, token_type="refresh")
            
            if payload is None:
                raise AuthenticationError("유효하지 않은 리프레시 토큰입니다")
            
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise AuthenticationError("토큰에 사용자 정보가 없습니다")
            
            try:
                user_id = UUID(user_id_str)
            except ValueError:
                raise AuthenticationError("올바르지 않은 사용자 ID 형식입니다")
            
            # 사용자 존재 및 활성화 상태 확인
            user = await self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("사용자를 찾을 수 없거나 비활성화된 계정입니다")
            
            # 새로운 토큰 쌍 생성
            return await self._create_tokens(user_id)
            
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"토큰 갱신 중 오류 발생: {str(e)}")

    async def logout_user(self, user_id: UUID) -> bool:
        """
        사용자 로그아웃 처리
        
        현재는 토큰 블랙리스트 기능이 구현되지 않아 
        클라이언트에서 토큰을 삭제하는 것으로 처리됩니다.
        
        Args:
            user_id: 로그아웃할 사용자 ID
            
        Returns:
            bool: 항상 True (성공)
            
        TODO:
            - Redis를 사용한 토큰 블랙리스트 구현
            - 디바이스별 로그아웃 처리
        """
        # TODO: 토큰 블랙리스트 구현 (Redis)
        # 
        # 구현 예시:
        # redis_key = f"blacklist_token:{token_jti}"
        # await redis.setex(redis_key, token_expire_time, "blacklisted")
        
        return True

    async def delete_user_account(self, user_id: UUID) -> bool:
        """
        사용자 계정 탈퇴 처리
        
        사용자 계정을 비활성화하고 관련 데이터를 정리합니다.
        실제 데이터 삭제가 아닌 비활성화 처리로 복구 가능성을 남겨둡니다.
        
        Args:
            user_id: 탈퇴할 사용자 ID
            
        Returns:
            bool: 탈퇴 처리 성공 여부
            
        Note:
            완전한 데이터 삭제가 필요한 경우 별도의 배치 작업으로 처리합니다.
        """
        return await self.user_service.deactivate_user(user_id)
