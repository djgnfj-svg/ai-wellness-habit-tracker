import apiClient from './apiClient';
import { API_ENDPOINTS } from '../constants';
import {
  User,
  WellnessProfile,
  PersonalizationData,
  NotificationSettings,
  DeviceToken,
} from '../types';

interface UpdateProfileRequest {
  nickname?: string;
  profile_image_url?: string;
  birth_year?: number;
  gender?: string;
  timezone?: string;
}

interface UpdateWellnessProfileRequest {
  fitness_level?: 'beginner' | 'intermediate' | 'advanced';
  primary_goals?: string[];
  available_time_slots?: any[];
  preferred_workout_times?: string[];
  preferred_workout_types?: string[];
  health_conditions?: string[];
  wake_up_time?: string;
  sleep_time?: string;
  work_schedule?: Record<string, any>;
}

interface UpdatePersonalizationRequest {
  personality_type?: string;
  motivation_style?: 'competitive' | 'achievement' | 'social';
  communication_preference?: 'friendly' | 'professional' | 'casual';
  coaching_frequency?: 'low' | 'normal' | 'high';
  preferred_message_times?: string[];
  language?: string;
  country?: string;
}

class UserService {
  /**
   * 사용자 프로필 조회
   */
  async getProfile(): Promise<User> {
    return await apiClient.get<User>(API_ENDPOINTS.USERS.PROFILE);
  }

  /**
   * 사용자 프로필 업데이트
   */
  async updateProfile(updates: UpdateProfileRequest): Promise<User> {
    return await apiClient.put<User>(API_ENDPOINTS.USERS.PROFILE, updates);
  }

  /**
   * 웰니스 프로필 조회
   */
  async getWellnessProfile(): Promise<WellnessProfile> {
    return await apiClient.get<WellnessProfile>(API_ENDPOINTS.USERS.WELLNESS_PROFILE);
  }

  /**
   * 웰니스 프로필 업데이트
   */
  async updateWellnessProfile(updates: UpdateWellnessProfileRequest): Promise<WellnessProfile> {
    return await apiClient.put<WellnessProfile>(
      API_ENDPOINTS.USERS.WELLNESS_PROFILE,
      updates
    );
  }

  /**
   * 개인화 데이터 조회
   */
  async getPersonalizationData(): Promise<PersonalizationData> {
    return await apiClient.get<PersonalizationData>(API_ENDPOINTS.USERS.PERSONALIZATION);
  }

  /**
   * 개인화 데이터 업데이트
   */
  async updatePersonalizationData(updates: UpdatePersonalizationRequest): Promise<PersonalizationData> {
    return await apiClient.put<PersonalizationData>(
      API_ENDPOINTS.USERS.PERSONALIZATION,
      updates
    );
  }

  /**
   * 알림 설정 조회
   */
  async getNotificationSettings(): Promise<NotificationSettings> {
    return await apiClient.get<NotificationSettings>(API_ENDPOINTS.NOTIFICATIONS.SETTINGS);
  }

  /**
   * 알림 설정 업데이트
   */
  async updateNotificationSettings(settings: Partial<NotificationSettings>): Promise<NotificationSettings> {
    return await apiClient.put<NotificationSettings>(
      API_ENDPOINTS.NOTIFICATIONS.SETTINGS,
      settings
    );
  }

  /**
   * 디바이스 토큰 등록
   */
  async registerDeviceToken(deviceToken: Omit<DeviceToken, 'is_active'>): Promise<void> {
    await apiClient.post(API_ENDPOINTS.NOTIFICATIONS.DEVICE_TOKEN, deviceToken);
  }

  /**
   * 디바이스 토큰 해제
   */
  async unregisterDeviceToken(deviceId: string): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.NOTIFICATIONS.DEVICE_TOKEN}/${deviceId}`);
  }

  /**
   * 프로필 이미지 업로드
   */
  async uploadProfileImage(
    imageFile: FormData,
    onProgress?: (progress: number) => void
  ): Promise<{ profile_image_url: string }> {
    return await apiClient.uploadFile<{ profile_image_url: string }>(
      `${API_ENDPOINTS.USERS.PROFILE}/image`,
      imageFile,
      onProgress
    );
  }

  /**
   * 계정 탈퇴
   */
  async deleteAccount(reason?: string, feedback?: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.USERS.PROFILE, {
      data: { reason, feedback },
    });
  }

  /**
   * 계정 비활성화
   */
  async deactivateAccount(): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.USERS.PROFILE}/deactivate`);
  }

  /**
   * 데이터 내보내기 요청
   */
  async requestDataExport(): Promise<{ download_url: string; expires_at: string }> {
    return await apiClient.post(`${API_ENDPOINTS.USERS.PROFILE}/export`);
  }

  /**
   * 사용자 통계 조회
   */
  async getUserStats(): Promise<{
    total_habits: number;
    active_habits: number;
    total_check_ins: number;
    longest_streak: number;
    current_streaks: number;
    join_date: string;
    days_active: number;
  }> {
    return await apiClient.get(`${API_ENDPOINTS.USERS.PROFILE}/stats`);
  }

  /**
   * 온보딩 완료 처리
   */
  async completeOnboarding(): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.USERS.PROFILE}/onboarding/complete`);
  }

  /**
   * 사용자 선호도 업데이트
   */
  async updatePreferences(preferences: {
    theme?: 'light' | 'dark' | 'auto';
    language?: string;
    time_format?: '12h' | '24h';
    date_format?: string;
    first_day_of_week?: number;
  }): Promise<void> {
    await apiClient.put(`${API_ENDPOINTS.USERS.PROFILE}/preferences`, preferences);
  }

  /**
   * 비밀번호 변경 (소셜 로그인이 아닌 경우)
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.USERS.PROFILE}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  /**
   * 이메일 변경
   */
  async changeEmail(newEmail: string): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.USERS.PROFILE}/change-email`, {
      new_email: newEmail,
    });
  }

  /**
   * 이메일 인증
   */
  async verifyEmail(token: string): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.USERS.PROFILE}/verify-email`, {
      token,
    });
  }
}

export const userService = new UserService();
export default userService;
