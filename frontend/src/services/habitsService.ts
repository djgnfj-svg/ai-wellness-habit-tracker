import apiClient from './apiClient';
import { API_ENDPOINTS } from '../constants';
import {
  UserHabit,
  HabitTemplate,
  HabitCategory,
  FrequencyConfig,
  ReminderConfig,
  PaginatedResponse,
} from '../types';

interface CreateHabitRequest {
  habit_template_id: string;
  custom_name?: string;
  target_frequency: FrequencyConfig;
  reminder_settings: ReminderConfig;
}

interface UpdateHabitRequest {
  custom_name?: string;
  target_frequency?: FrequencyConfig;
  reminder_settings?: ReminderConfig;
  is_active?: boolean;
}

interface HabitTemplateFilters {
  category_id?: string;
  difficulty_level?: number;
  search?: string;
  limit?: number;
  offset?: number;
}

class HabitsService {
  /**
   * 사용자 습관 목록 조회
   */
  async getUserHabits(status?: 'active' | 'inactive' | 'all'): Promise<UserHabit[]> {
    const params = status ? { status } : {};
    return await apiClient.get<UserHabit[]>(API_ENDPOINTS.HABITS.LIST, { params });
  }

  /**
   * 습관 생성
   */
  async createHabit(habitData: CreateHabitRequest): Promise<UserHabit> {
    return await apiClient.post<UserHabit>(API_ENDPOINTS.HABITS.LIST, habitData);
  }

  /**
   * 습관 수정
   */
  async updateHabit(habitId: string, updates: UpdateHabitRequest): Promise<UserHabit> {
    return await apiClient.put<UserHabit>(
      API_ENDPOINTS.HABITS.DETAIL(habitId),
      updates
    );
  }

  /**
   * 습관 삭제
   */
  async deleteHabit(habitId: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.HABITS.DETAIL(habitId));
  }

  /**
   * 습관 상세 조회
   */
  async getHabitDetail(habitId: string): Promise<UserHabit> {
    return await apiClient.get<UserHabit>(API_ENDPOINTS.HABITS.DETAIL(habitId));
  }

  /**
   * 습관 템플릿 목록 조회
   */
  async getHabitTemplates(filters?: HabitTemplateFilters): Promise<PaginatedResponse<HabitTemplate>> {
    return await apiClient.get<PaginatedResponse<HabitTemplate>>(
      API_ENDPOINTS.HABITS.TEMPLATES,
      { params: filters }
    );
  }

  /**
   * 습관 카테고리 목록 조회
   */
  async getHabitCategories(): Promise<HabitCategory[]> {
    return await apiClient.get<HabitCategory[]>(API_ENDPOINTS.HABITS.CATEGORIES);
  }

  /**
   * 개인화 습관 추천
   */
  async getRecommendedHabits(limit?: number): Promise<HabitTemplate[]> {
    const params = limit ? { limit } : {};
    return await apiClient.get<HabitTemplate[]>(
      API_ENDPOINTS.HABITS.RECOMMENDATIONS,
      { params }
    );
  }

  /**
   * 습관 순서 변경
   */
  async reorderHabits(habitIds: string[]): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.HABITS.LIST}/reorder`, {
      habit_ids: habitIds,
    });
  }

  /**
   * 습관 일괄 수정
   */
  async bulkUpdateHabits(updates: Array<{id: string; updates: UpdateHabitRequest}>): Promise<UserHabit[]> {
    return await apiClient.put<UserHabit[]>(`${API_ENDPOINTS.HABITS.LIST}/bulk`, {
      habits: updates,
    });
  }

  /**
   * 습관 복사
   */
  async duplicateHabit(habitId: string, customName?: string): Promise<UserHabit> {
    return await apiClient.post<UserHabit>(
      `${API_ENDPOINTS.HABITS.DETAIL(habitId)}/duplicate`,
      { custom_name: customName }
    );
  }
}

export const habitsService = new HabitsService();
export default habitsService;
