import apiClient from './apiClient';
import { API_ENDPOINTS } from '../constants';
import {
  LoginRequest,
  LoginResponse,
  TokenRefreshRequest,
  TokenRefreshResponse,
  User,
} from '../types';

class AuthService {
  /**
   * 카카오 로그인
   */
  async loginWithKakao(accessToken: string, deviceInfo?: any): Promise<LoginResponse> {
    const loginData: LoginRequest = {
      provider: 'kakao',
      access_token: accessToken,
      device_info: deviceInfo,
    };
    
    return await apiClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.KAKAO_LOGIN,
      loginData
    );
  }

  /**
   * 네이버 로그인
   */
  async loginWithNaver(accessToken: string, deviceInfo?: any): Promise<LoginResponse> {
    const loginData: LoginRequest = {
      provider: 'naver',
      access_token: accessToken,
      device_info: deviceInfo,
    };
    
    return await apiClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.NAVER_LOGIN,
      loginData
    );
  }

  /**
   * 구글 로그인
   */
  async loginWithGoogle(accessToken: string, deviceInfo?: any): Promise<LoginResponse> {
    const loginData: LoginRequest = {
      provider: 'google',
      access_token: accessToken,
      device_info: deviceInfo,
    };
    
    return await apiClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.GOOGLE_LOGIN,
      loginData
    );
  }

  /**
   * 토큰 갱신
   */
  async refreshToken(refreshToken: string): Promise<TokenRefreshResponse> {
    const refreshData: TokenRefreshRequest = {
      refresh_token: refreshToken,
    };
    
    return await apiClient.post<TokenRefreshResponse>(
      API_ENDPOINTS.AUTH.REFRESH_TOKEN,
      refreshData
    );
  }

  /**
   * 로그아웃
   */
  async logout(deviceId?: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
      device_id: deviceId,
    });
  }

  /**
   * 현재 사용자 정보 조회
   */
  async getCurrentUser(): Promise<User> {
    return await apiClient.get<User>(API_ENDPOINTS.USERS.PROFILE);
  }
}

export const authService = new AuthService();
export default authService;
