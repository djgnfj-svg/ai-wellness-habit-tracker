// 공통 타입
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// 사용자 관련 타입
export interface User extends BaseEntity {
  email: string;
  nickname: string;
  profile_image_url?: string;
  birth_year?: number;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  timezone: string;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string;
}

export interface WellnessProfile extends BaseEntity {
  user_id: string;
  fitness_level: 'beginner' | 'intermediate' | 'advanced';
  primary_goals: string[];
  available_time_slots: TimeSlot[];
  preferred_workout_times: string[];
  preferred_workout_types: string[];
  health_conditions: string[];
  wake_up_time?: string;
  sleep_time?: string;
  work_schedule: Record<string, any>;
}

export interface PersonalizationData extends BaseEntity {
  user_id: string;
  personality_type?: string;
  motivation_style?: 'competitive' | 'achievement' | 'social';
  communication_preference: 'friendly' | 'professional' | 'casual';
  coaching_frequency: 'low' | 'normal' | 'high';
  preferred_message_times: string[];
  language: string;
  country: string;
  usage_patterns: Record<string, any>;
}

export interface TimeSlot {
  day_of_week: number; // 0-6 (0=일요일)
  start_time: string; // "HH:MM"
  end_time: string; // "HH:MM"
}

// 습관 관련 타입
export interface HabitCategory extends BaseEntity {
  name: string;
  icon: string;
  color_code: string;
  parent_category_id?: string;
}

export interface HabitTemplate extends BaseEntity {
  name: string;
  description: string;
  category_id: string;
  difficulty_level: number; // 1-5
  estimated_time_minutes: number;
  recommended_frequency: FrequencyConfig;
  success_criteria: string;
  tips: string[];
  ai_coaching_prompts: string[];
}

export interface UserHabit extends BaseEntity {
  user_id: string;
  habit_template_id: string;
  custom_name?: string;
  target_frequency: FrequencyConfig;
  reminder_settings: ReminderConfig;
  reward_points: number;
  is_active: boolean;
  
  // Relations
  habit_template?: HabitTemplate;
  category?: HabitCategory;
}

export interface FrequencyConfig {
  type: 'daily' | 'weekly' | 'monthly';
  count: number; // 주 3회, 일 2회 등
  specific_days?: number[]; // 특정 요일 (0-6)
  time_slots?: TimeSlot[];
}

export interface ReminderConfig {
  enabled: boolean;
  times: string[]; // ["09:00", "14:00"]
  days_before?: number; // 며칠 전 알림
  type: 'push' | 'email' | 'both';
}

// 추적 관련 타입
export interface HabitLog extends BaseEntity {
  user_habit_id: string;
  logged_at: string;
  completion_status: 'completed' | 'partial' | 'skipped';
  completion_percentage: number; // 0-100
  duration_minutes?: number;
  intensity_level?: number; // 1-5
  mood_before?: number; // 1-10
  mood_after?: number; // 1-10
  notes?: string;
  location?: string;
  weather_condition?: string;
  energy_level?: number; // 1-5
  
  // Relations
  user_habit?: UserHabit;
}

export interface StreakData {
  user_habit_id: string;
  current_streak: number;
  longest_streak: number;
  last_completion_date?: string;
  risk_level: 'low' | 'medium' | 'high'; // 스트릭 중단 위험도
}

export interface ProgressSummary {
  user_id: string;
  date: string;
  total_habits: number;
  completed_habits: number;
  completion_rate: number;
  total_streaks: number;
  wellness_score: number; // 0-100
}

// AI 코칭 관련 타입
export interface ChatMessage {
  id: string;
  type: 'ai' | 'user';
  message: string;
  timestamp: string;
  context?: Record<string, any>;
}

export interface CoachingCard {
  id: string;
  type: 'motivation' | 'reminder' | 'insight' | 'celebration';
  title: string;
  message: string;
  emoji: string;
  action?: string;
  priority: number; // 1-10
  expires_at?: string;
  metadata?: Record<string, any>;
}

export interface AIInsight {
  id: string;
  type: 'pattern' | 'improvement' | 'achievement' | 'warning';
  title: string;
  description: string;
  data: Record<string, any>;
  confidence_score: number; // 0-1
  generated_at: string;
}

// 알림 관련 타입
export interface NotificationSettings {
  habit_reminders: boolean;
  ai_coaching: boolean;
  weekly_reports: boolean;
  achievement_alerts: boolean;
  marketing: boolean;
  quiet_hours: {
    enabled: boolean;
    start_time: string; // "22:00"
    end_time: string; // "08:00"
  };
}

export interface DeviceToken {
  device_id: string;
  token: string;
  platform: 'ios' | 'android';
  is_active: boolean;
}

// 분석 관련 타입
export interface DashboardData {
  user_id: string;
  date: string;
  completion_summary: {
    today: number;
    this_week: number;
    this_month: number;
  };
  streak_summary: {
    current_max: number;
    total_days: number;
    habit_streaks: StreakData[];
  };
  wellness_trends: {
    score: number;
    change_from_last_week: number;
    mood_average: number;
    energy_average: number;
  };
  upcoming_habits: UserHabit[];
  recent_achievements: Achievement[];
}

export interface WeeklyReport {
  user_id: string;
  week_start: string;
  week_end: string;
  completion_rate: number;
  total_completed: number;
  streak_changes: number;
  mood_trend: 'improving' | 'stable' | 'declining';
  top_performing_habits: string[];
  areas_for_improvement: string[];
  ai_recommendations: string[];
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  emoji: string;
  earned_at: string;
  category: 'streak' | 'completion' | 'consistency' | 'milestone';
  metadata?: Record<string, any>;
}

// 인증 관련 타입
export interface LoginRequest {
  provider: 'kakao' | 'naver' | 'google';
  access_token: string;
  device_info?: {
    device_id: string;
    platform: 'ios' | 'android';
    app_version: string;
  };
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  is_new_user: boolean;
}

export interface TokenRefreshRequest {
  refresh_token: string;
}

export interface TokenRefreshResponse {
  access_token: string;
  refresh_token: string;
}

// 네비게이션 관련 타입
export type RootStackParamList = {
  Welcome: undefined;
  Problem: undefined;
  Login: undefined;
  ProfileSetup: undefined;
  WellnessGoals: undefined;
  LifestylePattern: undefined;
  Main: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Stats: undefined;
  Checkin: undefined;
  AICoach: undefined;
  Profile: undefined;
};

// 폼 관련 타입
export interface ProfileSetupForm {
  nickname: string;
  birth_year?: number;
  gender?: string;
}

export interface WellnessGoalsForm {
  fitness_level: string;
  primary_goals: string[];
  preferred_workout_types: string[];
  health_conditions: string[];
}

export interface LifestylePatternForm {
  wake_up_time?: string;
  sleep_time?: string;
  work_schedule: Record<string, any>;
  available_time_slots: TimeSlot[];
}

// Redux 상태 타입
export interface AuthState {
  user: User | null;
  tokens: {
    access: string | null;
    refresh: string | null;
  };
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface HabitsState {
  userHabits: UserHabit[];
  habitTemplates: HabitTemplate[];
  categories: HabitCategory[];
  isLoading: boolean;
  error: string | null;
}

export interface TrackingState {
  todayLogs: HabitLog[];
  streaks: StreakData[];
  progress: ProgressSummary | null;
  isLoading: boolean;
  error: string | null;
}

export interface AICoachingState {
  messages: ChatMessage[];
  coachingCards: CoachingCard[];
  insights: AIInsight[];
  isTyping: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AppState {
  theme: 'light' | 'dark';
  notifications: NotificationSettings;
  hasLaunched: boolean;
  isOnboardingComplete: boolean;
  connectivity: 'online' | 'offline';
}