import apiClient from './apiClient';
import { API_ENDPOINTS } from '../constants';
import {
  ChatMessage,
  CoachingCard,
  AIInsight,
} from '../types';

interface ChatRequest {
  message: string;
  context?: {
    current_mood?: number;
    recent_activities?: string[];
    time_of_day?: string;
    habit_id?: string;
  };
}

interface ChatResponse {
  message_id: string;
  content: string;
  message_type: string;
  suggestions?: Array<{
    text: string;
    action: string;
    habit_id?: string;
  }>;
  tone: string;
  created_at: string;
}

interface CoachingMessageRequest {
  message_type: 'habit_reminder' | 'motivation' | 'encouragement' | 'insight';
  context?: {
    habit_id?: string;
    current_mood?: number;
    current_situation?: string;
    weather?: string;
  };
  user_message?: string;
}

interface PersonalizationSettings {
  communication_style: 'friendly' | 'professional' | 'casual';
  coaching_frequency: 'low' | 'normal' | 'high';
  motivation_type: 'positive' | 'challenge' | 'gentle';
  preferred_message_times: string[];
}

class AICoachingService {
  /**
   * AI와 채팅
   */
  async sendChatMessage(chatData: ChatRequest): Promise<ChatResponse> {
    return await apiClient.post<ChatResponse>(
      API_ENDPOINTS.AI_COACHING.CHAT,
      chatData
    );
  }

  /**
   * AI 코칭 메시지 요청
   */
  async requestCoachingMessage(requestData: CoachingMessageRequest): Promise<ChatResponse> {
    return await apiClient.post<ChatResponse>(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/coaching`,
      requestData
    );
  }

  /**
   * 채팅 히스토리 조회
   */
  async getChatHistory(limit?: number, offset?: number): Promise<ChatMessage[]> {
    const params: any = {};
    if (limit) params.limit = limit;
    if (offset) params.offset = offset;

    return await apiClient.get<ChatMessage[]>(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/history`,
      { params }
    );
  }

  /**
   * 코칭 카드 목록 조회
   */
  async getCoachingCards(): Promise<CoachingCard[]> {
    return await apiClient.get<CoachingCard[]>(API_ENDPOINTS.AI_COACHING.CARDS);
  }

  /**
   * 코칭 카드 읽음 처리
   */
  async markCardAsRead(cardId: string): Promise<void> {
    await apiClient.post(`${API_ENDPOINTS.AI_COACHING.CARDS}/${cardId}/read`);
  }

  /**
   * 코칭 카드 액션 실행
   */
  async executeCardAction(cardId: string, action: string): Promise<any> {
    return await apiClient.post(
      `${API_ENDPOINTS.AI_COACHING.CARDS}/${cardId}/action`,
      { action }
    );
  }

  /**
   * AI 인사이트 조회
   */
  async getAIInsights(
    type?: 'pattern' | 'improvement' | 'achievement' | 'warning',
    limit?: number
  ): Promise<AIInsight[]> {
    const params: any = {};
    if (type) params.type = type;
    if (limit) params.limit = limit;

    return await apiClient.get<AIInsight[]>(
      API_ENDPOINTS.AI_COACHING.INSIGHTS,
      { params }
    );
  }

  /**
   * AI 코칭 개인화 설정 조회
   */
  async getPersonalizationSettings(): Promise<PersonalizationSettings> {
    return await apiClient.get<PersonalizationSettings>(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/settings`
    );
  }

  /**
   * AI 코칭 개인화 설정 업데이트
   */
  async updatePersonalizationSettings(settings: Partial<PersonalizationSettings>): Promise<PersonalizationSettings> {
    return await apiClient.put<PersonalizationSettings>(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/settings`,
      settings
    );
  }

  /**
   * 습관별 맞춤 조언 요청
   */
  async getHabitAdvice(habitId: string, situation?: string): Promise<ChatResponse> {
    return await apiClient.post<ChatResponse>(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/advice`,
      {
        habit_id: habitId,
        situation,
      }
    );
  }

  /**
   * 동기부여 메시지 요청
   */
  async getMotivationMessage(context?: {
    mood?: number;
    energy_level?: number;
    recent_performance?: 'good' | 'average' | 'poor';
  }): Promise<ChatResponse> {
    return await apiClient.post<ChatResponse>(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/motivation`,
      { context }
    );
  }

  /**
   * 주간 회고 AI 분석
   */
  async getWeeklyReflection(): Promise<{
    highlights: string[];
    areas_for_improvement: string[];
    personalized_recommendations: string[];
    motivational_message: string;
  }> {
    return await apiClient.get(
      `${API_ENDPOINTS.AI_COACHING.INSIGHTS}/weekly-reflection`
    );
  }

  /**
   * AI 코칭 피드백 제공
   */
  async provideFeedback(
    messageId: string,
    feedback: 'helpful' | 'not_helpful' | 'inappropriate',
    comment?: string
  ): Promise<void> {
    await apiClient.post(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/feedback`,
      {
        message_id: messageId,
        feedback,
        comment,
      }
    );
  }

  /**
   * 채팅 세션 초기화
   */
  async clearChatHistory(): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.AI_COACHING.CHAT}/history`);
  }

  /**
   * AI 코칭 통계 조회
   */
  async getCoachingStats(): Promise<{
    total_messages: number;
    helpful_messages: number;
    avg_response_time: number;
    most_discussed_topics: string[];
    improvement_areas: string[];
  }> {
    return await apiClient.get(
      `${API_ENDPOINTS.AI_COACHING.CHAT}/stats`
    );
  }
}

export const aiCoachingService = new AICoachingService();
export default aiCoachingService;
