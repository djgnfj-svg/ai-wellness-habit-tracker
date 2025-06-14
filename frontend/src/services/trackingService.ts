import apiClient from './apiClient';
import { API_ENDPOINTS } from '../constants';
import {
  HabitLog,
  StreakData,
  ProgressSummary,
  DashboardData,
  WeeklyReport,
} from '../types';

interface CheckInRequest {
  user_habit_id: string;
  completion_status: 'completed' | 'partial' | 'skipped';
  completion_percentage: number;
  duration_minutes?: number;
  intensity_level?: number;
  mood_before?: number;
  mood_after?: number;
  notes?: string;
  location?: string;
  evidence_file?: FormData;
}

interface CheckInResponse {
  log_id: string;
  streak_updated: boolean;
  new_streak: number;
  points_earned: number;
  achievements_unlocked: any[];
  ai_response: string;
}

interface ProgressFilters {
  habit_id?: string;
  period?: 'week' | 'month' | 'year';
  start_date?: string;
  end_date?: string;
}

interface TodayHabitsResponse {
  date: string;
  overall_completion_rate: number;
  total_habits: number;
  completed_habits: number;
  habits: Array<{
    user_habit_id: string;
    habit_name: string;
    target: number;
    completed: number;
    completion_rate: number;
    status: string;
    next_reminder?: string;
    logs: HabitLog[];
  }>;
  mood_average: number;
  ai_insights: string[];
}

class TrackingService {
  /**
   * 습관 체크인
   */
  async checkInHabit(checkInData: CheckInRequest): Promise<CheckInResponse> {
    if (checkInData.evidence_file) {
      // FormData로 파일과 함께 전송
      const formData = new FormData();
      Object.entries(checkInData).forEach(([key, value]) => {
        if (key !== 'evidence_file' && value !== undefined) {
          formData.append(key, value.toString());
        }
      });
      
      if (checkInData.evidence_file) {
        formData.append('evidence_file', checkInData.evidence_file);
      }

      return await apiClient.uploadFile<CheckInResponse>(
        API_ENDPOINTS.TRACKING.CHECK_IN,
        formData
      );
    } else {
      // 일반 JSON 요청
      const { evidence_file, ...jsonData } = checkInData;
      return await apiClient.post<CheckInResponse>(
        API_ENDPOINTS.TRACKING.CHECK_IN,
        jsonData
      );
    }
  }

  /**
   * 오늘의 습관 현황 조회
   */
  async getTodayHabits(date?: string): Promise<TodayHabitsResponse> {
    const params = date ? { date } : {};
    return await apiClient.get<TodayHabitsResponse>(
      `${API_ENDPOINTS.TRACKING.CHECK_IN}/today`,
      { params }
    );
  }

  /**
   * 습관 로그 조회
   */
  async getHabitLogs(
    habitId?: string,
    startDate?: string,
    endDate?: string,
    limit?: number
  ): Promise<HabitLog[]> {
    const params: any = {};
    if (habitId) params.habit_id = habitId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (limit) params.limit = limit;

    return await apiClient.get<HabitLog[]>(API_ENDPOINTS.TRACKING.LOGS, { params });
  }

  /**
   * 습관 로그 수정
   */
  async updateHabitLog(logId: string, updates: Partial<CheckInRequest>): Promise<HabitLog> {
    return await apiClient.put<HabitLog>(
      `${API_ENDPOINTS.TRACKING.LOGS}/${logId}`,
      updates
    );
  }

  /**
   * 습관 로그 삭제
   */
  async deleteHabitLog(logId: string): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.TRACKING.LOGS}/${logId}`);
  }

  /**
   * 진척도 조회
   */
  async getProgress(filters?: ProgressFilters): Promise<ProgressSummary> {
    return await apiClient.get<ProgressSummary>(
      API_ENDPOINTS.TRACKING.PROGRESS,
      { params: filters }
    );
  }

  /**
   * 스트릭 데이터 조회
   */
  async getStreaks(habitId?: string): Promise<StreakData[]> {
    const params = habitId ? { habit_id: habitId } : {};
    return await apiClient.get<StreakData[]>(
      API_ENDPOINTS.TRACKING.STREAKS,
      { params }
    );
  }

  /**
   * 대시보드 데이터 조회
   */
  async getDashboardData(period?: 'week' | 'month'): Promise<DashboardData> {
    const params = period ? { period } : {};
    return await apiClient.get<DashboardData>(
      API_ENDPOINTS.ANALYTICS.DASHBOARD,
      { params }
    );
  }

  /**
   * 주간 리포트 조회
   */
  async getWeeklyReport(date?: string): Promise<WeeklyReport> {
    const params = date ? { date } : {};
    return await apiClient.get<WeeklyReport>(
      API_ENDPOINTS.ANALYTICS.WEEKLY_REPORT,
      { params }
    );
  }

  /**
   * 월간 리포트 조회
   */
  async getMonthlyReport(year: number, month: number): Promise<WeeklyReport> {
    return await apiClient.get<WeeklyReport>(
      API_ENDPOINTS.ANALYTICS.MONTHLY_REPORT,
      { params: { year, month } }
    );
  }

  /**
   * 습관 통계 조회
   */
  async getHabitStats(
    habitId: string,
    period: 'week' | 'month' | 'quarter' | 'year'
  ): Promise<any> {
    return await apiClient.get(
      `${API_ENDPOINTS.ANALYTICS.DASHBOARD}/habits/${habitId}`,
      { params: { period } }
    );
  }

  /**
   * 일괄 체크인 (여러 습관 동시에)
   */
  async bulkCheckIn(checkIns: CheckInRequest[]): Promise<CheckInResponse[]> {
    return await apiClient.post<CheckInResponse[]>(
      `${API_ENDPOINTS.TRACKING.CHECK_IN}/bulk`,
      { check_ins: checkIns }
    );
  }

  /**
   * 과거 날짜 체크인
   */
  async backfillCheckIn(
    habitId: string,
    date: string,
    checkInData: Omit<CheckInRequest, 'user_habit_id'>
  ): Promise<CheckInResponse> {
    return await apiClient.post<CheckInResponse>(
      `${API_ENDPOINTS.TRACKING.CHECK_IN}/backfill`,
      {
        user_habit_id: habitId,
        date,
        ...checkInData,
      }
    );
  }
}

export const trackingService = new TrackingService();
export default trackingService;
