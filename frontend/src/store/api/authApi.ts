import { apiClient } from '../../services/apiClient';
import { API_ENDPOINTS } from '../../constants';
import type { 
  LoginRequest, 
  LoginResponse, 
  TokenRefreshRequest, 
  TokenRefreshResponse,
  User 
} from '../../types';

export class AuthApi {
  /**
   * 소셜 로그인 (카카오, 네이버, 구글)
   */
  async login(loginData: LoginRequest): Promise<LoginResponse> {
    let endpoint: string;
    
    switch (loginData.provider) {
      case 'kakao':
        endpoint = API_ENDPOINTS.AUTH.KAKAO_LOGIN;
        break;
      case 'naver':
        endpoint = API_ENDPOINTS.AUTH.NAVER_LOGIN;
        break;
      case 'google':
        endpoint = API_ENDPOINTS.AUTH.GOOGLE_LOGIN;
        break;
      default:
        throw new Error('지원하지 않는 로그인 방식입니다.');
    }

    const response = await apiClient.post<LoginResponse>(endpoint, loginData);
    return response;
  }

  /**
   * 토큰 갱신
   */
  async refreshToken(refreshData: TokenRefreshRequest): Promise<TokenRefreshResponse> {
    const response = await apiClient.post<TokenRefreshResponse>(
      API_ENDPOINTS.AUTH.REFRESH_TOKEN,
      refreshData
    );
    return response;
  }

  /**
   * 로그아웃
   */
  async logout(): Promise<void> {
    await apiClient.post<void>(API_ENDPOINTS.AUTH.LOGOUT);
  }

  /**
   * 현재 사용자 정보 조회
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>(API_ENDPOINTS.USERS.PROFILE);
    return response;
  }

  /**
   * 사용자 프로필 업데이트
   */
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(API_ENDPOINTS.USERS.PROFILE, userData);
    return response;
  }

  /**
   * 웰니스 프로필 조회
   */
  async getWellnessProfile(): Promise<any> {
    const response = await apiClient.get<any>(API_ENDPOINTS.USERS.WELLNESS_PROFILE);
    return response;
  }

  /**
   * 웰니스 프로필 업데이트
   */
  async updateWellnessProfile(wellnessData: any): Promise<any> {
    const response = await apiClient.put<any>(API_ENDPOINTS.USERS.WELLNESS_PROFILE, wellnessData);
    return response;
  }

  /**
   * 개인화 데이터 조회
   */
  async getPersonalizationData(): Promise<any> {
    const response = await apiClient.get<any>(API_ENDPOINTS.USERS.PERSONALIZATION);
    return response;
  }

  /**
   * 개인화 데이터 업데이트
   */
  async updatePersonalizationData(personalizationData: any): Promise<any> {
    const response = await apiClient.put<any>(API_ENDPOINTS.USERS.PERSONALIZATION, personalizationData);
    return response;
  }
}

// 싱글톤 인스턴스
export const authApi = new AuthApi();