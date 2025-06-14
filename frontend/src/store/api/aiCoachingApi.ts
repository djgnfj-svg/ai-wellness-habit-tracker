import { apiClient } from '../../services/apiClient';
import { API_ENDPOINTS } from '../../constants';
import type { 
  ChatMessage, 
  CoachingCard, 
  AIInsight 
} from '../../types';

export class AICoachingApi {
  /**
   * AI 코치에게 메시지 전송
   */
  async sendMessage(message: string, context?: Record<string, any>): Promise<{
    message: string;
    context?: Record<string, any>;
  }> {
    const response = await apiClient.post<{
      message: string;
      context?: Record<string, any>;
    }>(API_ENDPOINTS.AI_COACHING.CHAT, {
      message,
      context,
    });
    return response;
  }

  /**
   * 코칭 카드 목록 조회
   */
  async getCoachingCards(): Promise<CoachingCard[]> {
    const response = await apiClient.get<CoachingCard[]>(API_ENDPOINTS.AI_COACHING.CARDS);
    return response;
  }

  /**
   * AI 인사이트 목록 조회
   */
  async getInsights(): Promise<AIInsight[]> {
    const response = await apiClient.get<AIInsight[]>(API_ENDPOINTS.AI_COACHING.INSIGHTS);
    return response;
  }

  /**
   * 코칭 카드 제거
   */
  async dismissCard(cardId: string): Promise<void> {
    await apiClient.post<void>(`${API_ENDPOINTS.AI_COACHING.CARDS}/${cardId}/dismiss`);
  }

  /**
   * 대화 히스토리 조회
   */
  async getChatHistory(limit: number = 50, offset: number = 0): Promise<ChatMessage[]> {
    const response = await apiClient.get<{
      messages: ChatMessage[];
      total: number;
    }>(`${API_ENDPOINTS.AI_COACHING.CHAT}/history`, {
      params: { limit, offset }
    });
    return response.messages;
  }

  /**
   * AI 코칭 설정 업데이트
   */
  async updateCoachingSettings(settings: {
    communication_style?: 'friendly' | 'professional' | 'casual';
    coaching_frequency?: 'low' | 'normal' | 'high';
    motivation_type?: 'positive' | 'challenge' | 'gentle';
    preferred_message_times?: string[];
  }): Promise<void> {
    await apiClient.put<void>(`${API_ENDPOINTS.AI_COACHING.CHAT}/settings`, settings);
  }

  /**
   * 컨텍스트 기반 코칭 메시지 요청
   */
  async requestContextualCoaching(context: {
    message_type: 'habit_reminder' | 'motivation' | 'encouragement' | 'insight';
    habit_id?: string;
    current_mood?: number;
    current_situation?: string;
    weather?: string;
  }): Promise<{
    message: string;
    suggestions?: Array<{
      text: string;
      action: string;
      habit_id?: string;
    }>;
  }> {
    const response = await apiClient.post<{
      message: string;
      suggestions?: Array<{
        text: string;
        action: string;
        habit_id?: string;
      }>;
    }>(`${API_ENDPOINTS.AI_COACHING.CHAT}/contextual`, context);
    return response;
  }

  /**
   * 특정 습관에 대한 맞춤 조언 요청
   */
  async getHabitAdvice(habitId: string, situation?: string): Promise<{
    advice: string;
    tips: string[];
    motivation: string;
  }> {
    const response = await apiClient.post<{
      advice: string;
      tips: string[];
      motivation: string;
    }>(`${API_ENDPOINTS.AI_COACHING.CHAT}/habit-advice`, {
      habit_id: habitId,
      situation,
    });
    return response;
  }

  /**
   * 사용자 진행상황 기반 격려 메시지 생성
   */
  async generateEncouragement(progressData: {
    completion_rate: number;
    current_streak: number;
    struggling_habits: string[];
  }): Promise<{
    message: string;
    tone: 'celebratory' | 'supportive' | 'motivational';
    action_suggestions: string[];
  }> {
    const response = await apiClient.post<{
      message: string;
      tone: 'celebratory' | 'supportive' | 'motivational';
      action_suggestions: string[];
    }>(`${API_ENDPOINTS.AI_COACHING.CHAT}/encouragement`, progressData);
    return response;
  }
}

// 싱글톤 인스턴스
export const aiCoachingApi = new AICoachingApi();