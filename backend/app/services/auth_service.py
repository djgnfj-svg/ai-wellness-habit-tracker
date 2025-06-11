"""
인증 관리 서비스
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
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def _get_social_account(
        self, 
        user_id: UUID, 
        provider: str
    ) -> Optional[SocialAccount]:
        """소셜 계정 조회"""
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
        """소셜 계정 생성 또는 업데이트"""
        social_account = await self._get_social_account(user_id, provider)
        
        if social_account:
            # 기존 계정 업데이트
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

    async def _get_kakao_user_info(self, access_token: str) -> Dict[str, Any]:
        """카카오 사용자 정보 조회"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ExternalServiceError("카카오 사용자 정보 조회 실패")
            
            return response.json()

    async def _get_naver_user_info(self, access_token: str) -> Dict[str, Any]:
        """네이버 사용자 정보 조회"""
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openapi.naver.com/v1/nid/me",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ExternalServiceError("네이버 사용자 정보 조회 실패")
            
            return response.json()

    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """구글 사용자 정보 조회"""
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ExternalServiceError("구글 사용자 정보 조회 실패")
            
            return response.json()

    async def kakao_login(self, access_token: str) -> AuthResponse:
        """카카오 로그인"""
        try:
            # 카카오 사용자 정보 조회
            kakao_user = await self._get_kakao_user_info(access_token)
            
            provider_user_id = str(kakao_user["id"])
            kakao_account = kakao_user.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            
            email = kakao_account.get("email")
            nickname = profile.get("nickname", f"카카오사용자{provider_user_id}")
            profile_image_url = profile.get("profile_image_url")
            
            if not email:
                raise AuthenticationError("카카오 계정에서 이메일 정보를 가져올 수 없습니다")
            
            # 기존 사용자 확인
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                # 새 사용자 생성
                user = await self.user_service.create_user(
                    email=email,
                    nickname=nickname,
                    profile_image_url=profile_image_url
                )
            
            # 소셜 계정 정보 저장
            await self._create_or_update_social_account(
                user_id=user.id,
                provider="kakao",
                provider_user_id=provider_user_id,
                access_token=access_token
            )
            
            # 마지막 로그인 시간 업데이트
            await self.user_service.update_last_login(user.id)
            
            # JWT 토큰 생성
            tokens = await self._create_tokens(user.id)
            
            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                user=user
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ExternalServiceError)):
                raise e
            raise AuthenticationError(f"카카오 로그인 처리 중 오류 발생: {str(e)}")

    async def naver_login(self, access_token: str) -> AuthResponse:
        """네이버 로그인"""
        try:
            # 네이버 사용자 정보 조회
            naver_response = await self._get_naver_user_info(access_token)
            naver_user = naver_response.get("response", {})
            
            provider_user_id = naver_user.get("id")
            email = naver_user.get("email")
            nickname = naver_user.get("nickname", f"네이버사용자{provider_user_id}")
            profile_image_url = naver_user.get("profile_image")
            
            if not email:
                raise AuthenticationError("네이버 계정에서 이메일 정보를 가져올 수 없습니다")
            
            # 기존 사용자 확인
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                # 새 사용자 생성
                user = await self.user_service.create_user(
                    email=email,
                    nickname=nickname,
                    profile_image_url=profile_image_url
                )
            
            # 소셜 계정 정보 저장
            await self._create_or_update_social_account(
                user_id=user.id,
                provider="naver",
                provider_user_id=provider_user_id,
                access_token=access_token
            )
            
            # 마지막 로그인 시간 업데이트
            await self.user_service.update_last_login(user.id)
            
            # JWT 토큰 생성
            tokens = await self._create_tokens(user.id)
            
            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                user=user
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ExternalServiceError)):
                raise e
            raise AuthenticationError(f"네이버 로그인 처리 중 오류 발생: {str(e)}")

    async def google_login(self, access_token: str) -> AuthResponse:
        """구글 로그인"""
        try:
            # 구글 사용자 정보 조회
            google_user = await self._get_google_user_info(access_token)
            
            provider_user_id = google_user.get("id")
            email = google_user.get("email")
            nickname = google_user.get("name", f"구글사용자{provider_user_id}")
            profile_image_url = google_user.get("picture")
            
            if not email:
                raise AuthenticationError("구글 계정에서 이메일 정보를 가져올 수 없습니다")
            
            # 기존 사용자 확인
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                # 새 사용자 생성
                user = await self.user_service.create_user(
                    email=email,
                    nickname=nickname,
                    profile_image_url=profile_image_url
                )
            
            # 소셜 계정 정보 저장
            await self._create_or_update_social_account(
                user_id=user.id,
                provider="google",
                provider_user_id=provider_user_id,
                access_token=access_token
            )
            
            # 마지막 로그인 시간 업데이트
            await self.user_service.update_last_login(user.id)
            
            # JWT 토큰 생성
            tokens = await self._create_tokens(user.id)
            
            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                user=user
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ExternalServiceError)):
                raise e
            raise AuthenticationError(f"구글 로그인 처리 중 오류 발생: {str(e)}")

    async def _create_tokens(self, user_id: UUID) -> Token:
        """JWT 토큰 생성"""
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """리프레시 토큰으로 액세스 토큰 갱신"""
        try:
            payload = verify_token(refresh_token)
            user_id = UUID(payload.get("sub"))
            
            # 사용자 존재 확인
            user = await self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("유효하지 않은 사용자입니다")
            
            # 새 토큰 생성
            return await self._create_tokens(user_id)
            
        except Exception as e:
            raise AuthenticationError("토큰 갱신에 실패했습니다")

    async def logout_user(self, user_id: UUID) -> bool:
        """사용자 로그아웃"""
        # TODO: 토큰 블랙리스트 구현 (Redis)
        # 현재는 클라이언트에서 토큰 삭제만 하면 됨
        return True

    async def delete_user_account(self, user_id: UUID) -> bool:
        """사용자 계정 삭제"""
        return await self.user_service.deactivate_user(user_id)
