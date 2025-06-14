// Mock 데이터 - 백엔드 없이 앱을 테스트할 수 있도록 하는 샘플 데이터

import { 
  User, 
  WellnessProfile, 
  HabitTemplate, 
  HabitCategory, 
  UserHabit, 
  HabitLog, 
  ChatMessage, 
  CoachingCard,
  AIInsight,
  Achievement,
  StreakData,
  DashboardData
} from '../types';

// Mock 사용자 데이터
export const mockUser: User = {
  id: 'user_001',
  email: 'test@wellnessai.com',
  nickname: '민지',
  profile_image_url: null,
  birth_year: 1995,
  gender: 'female',
  timezone: 'Asia/Seoul',
  is_active: true,
  is_verified: true,
  last_login_at: new Date().toISOString(),
  created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  updated_at: new Date().toISOString(),
};

// Mock 웰니스 프로필
export const mockWellnessProfile: WellnessProfile = {
  id: 'wellness_001',
  user_id: 'user_001',
  fitness_level: 'beginner',
  primary_goals: ['체중 관리', '스트레스 해소', '수면 개선'],
  available_time_slots: [
    { day_of_week: 1, start_time: '07:00', end_time: '08:00' },
    { day_of_week: 3, start_time: '19:00', end_time: '20:00' },
    { day_of_week: 5, start_time: '07:00', end_time: '08:00' },
  ],
  preferred_workout_times: ['아침', '저녁'],
  preferred_workout_types: ['요가', '스트레칭', '산책'],
  health_conditions: [],
  wake_up_time: '07:00',
  sleep_time: '23:00',
  work_schedule: {
    type: 'remote',
    start_time: '09:00',
    end_time: '18:00',
    flexible: true
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// Mock 습관 카테고리
export const mockHabitCategories: HabitCategory[] = [
  {
    id: 'category_001',
    name: '건강 관리',
    icon: '💪',
    color_code: '#34C759',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'category_002', 
    name: '정신 건강',
    icon: '🧘‍♀️',
    color_code: '#007AFF',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'category_003',
    name: '수분 섭취',
    icon: '💧',
    color_code: '#50C8F5',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'category_004',
    name: '자기계발',
    icon: '📚',
    color_code: '#FF9500',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// Mock 습관 템플릿
export const mockHabitTemplates: HabitTemplate[] = [
  {
    id: 'template_001',
    name: '물 마시기',
    description: '하루 8잔의 물을 마셔 수분을 유지해요',
    category_id: 'category_003',
    difficulty_level: 1,
    estimated_time_minutes: 1,
    recommended_frequency: {
      type: 'daily',
      count: 8,
      time_slots: []
    },
    success_criteria: '하루 8잔 (약 2L) 완료',
    tips: [
      '기상 후 물 한 잔으로 시작하세요',
      '식사 30분 전에 물을 마시면 좋아요',
      '스마트폰 알림을 활용해보세요'
    ],
    ai_coaching_prompts: [
      '오늘 물을 충분히 마셨나요?',
      '수분 섭취로 피부와 건강을 관리해보세요!'
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'template_002',
    name: '명상하기',
    description: '10분간 마음챙김 명상으로 스트레스를 해소해요',
    category_id: 'category_002',
    difficulty_level: 2,
    estimated_time_minutes: 10,
    recommended_frequency: {
      type: 'daily',
      count: 1,
      time_slots: []
    },
    success_criteria: '10분 명상 완료',
    tips: [
      '조용한 장소에서 시작하세요',
      '호흡에 집중해보세요',
      '처음엔 5분부터 시작해도 좋아요'
    ],
    ai_coaching_prompts: [
      '오늘의 명상은 어떠셨나요?',
      '마음이 차분해졌다면 성공이에요!'
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'template_003',
    name: '스트레칭',
    description: '간단한 스트레칭으로 몸의 긴장을 풀어요',
    category_id: 'category_001',
    difficulty_level: 1,
    estimated_time_minutes: 15,
    recommended_frequency: {
      type: 'daily',
      count: 2,
      time_slots: []
    },
    success_criteria: '15분 스트레칭 완료',
    tips: [
      '어깨와 목부터 시작하세요',
      '무리하지 말고 천천히',
      '규칙적인 시간에 하는 것이 좋아요'
    ],
    ai_coaching_prompts: [
      '스트레칭 후 몸이 가벼워졌나요?',
      '꾸준함이 가장 중요해요!'
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'template_004',
    name: '산책하기',
    description: '30분간 가벼운 산책으로 활력을 충전해요',
    category_id: 'category_001',
    difficulty_level: 2,
    estimated_time_minutes: 30,
    recommended_frequency: {
      type: 'daily',
      count: 1,
      time_slots: []
    },
    success_criteria: '30분 산책 완료',
    tips: [
      '편한 신발을 착용하세요',
      '자연을 감상하며 걸어보세요',
      '친구나 가족과 함께 걸어도 좋아요'
    ],
    ai_coaching_prompts: [
      '오늘 산책에서 무엇을 보셨나요?',
      '걷기는 최고의 운동이에요!'
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'template_005',
    name: '독서하기',
    description: '20분간 책을 읽으며 지식을 쌓아요',
    category_id: 'category_004',
    difficulty_level: 2,
    estimated_time_minutes: 20,
    recommended_frequency: {
      type: 'daily',
      count: 1,
      time_slots: []
    },
    success_criteria: '20분 독서 완료',
    tips: [
      '관심 있는 분야부터 시작하세요',
      '편안한 자세로 읽어보세요',
      '메모하며 읽으면 더 효과적이에요'
    ],
    ai_coaching_prompts: [
      '오늘은 어떤 내용을 읽으셨나요?',
      '독서는 마음의 양식이에요!'
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// Mock 사용자 습관
export const mockUserHabits: UserHabit[] = [
  {
    id: 'user_habit_001',
    user_id: 'user_001',
    habit_template_id: 'template_001',
    custom_name: null,
    target_frequency: {
      type: 'daily',
      count: 8,
      time_slots: []
    },
    reminder_settings: {
      enabled: true,
      times: ['09:00', '12:00', '15:00', '18:00'],
      type: 'push'
    },
    reward_points: 150,
    is_active: true,
    habit_template: mockHabitTemplates[0],
    category: mockHabitCategories[2],
    created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'user_habit_002',
    user_id: 'user_001',
    habit_template_id: 'template_002',
    custom_name: null,
    target_frequency: {
      type: 'daily',
      count: 1,
      time_slots: []
    },
    reminder_settings: {
      enabled: true,
      times: ['08:00'],
      type: 'push'
    },
    reward_points: 120,
    is_active: true,
    habit_template: mockHabitTemplates[1],
    category: mockHabitCategories[1],
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'user_habit_003',
    user_id: 'user_001',
    habit_template_id: 'template_003',
    custom_name: null,
    target_frequency: {
      type: 'daily',
      count: 2,
      time_slots: []
    },
    reminder_settings: {
      enabled: true,
      times: ['09:00', '17:00'],
      type: 'push'
    },
    reward_points: 80,
    is_active: true,
    habit_template: mockHabitTemplates[2],
    category: mockHabitCategories[0],
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// Mock 습관 로그
export const mockHabitLogs: HabitLog[] = [
  {
    id: 'log_001',
    user_habit_id: 'user_habit_001',
    logged_at: new Date().toISOString(),
    completion_status: 'completed',
    completion_percentage: 100,
    mood_before: 6,
    mood_after: 8,
    notes: '상쾌한 기분!',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'log_002',
    user_habit_id: 'user_habit_002',
    logged_at: new Date().toISOString(),
    completion_status: 'completed',
    completion_percentage: 100,
    duration_minutes: 10,
    mood_before: 5,
    mood_after: 7,
    notes: '마음이 차분해졌어요',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// Mock AI 채팅 메시지
export const mockChatMessages: ChatMessage[] = [
  {
    id: 'msg_001',
    type: 'ai',
    message: '안녕하세요, 민지님! 🌱 오늘도 건강한 하루 보내고 계신가요? 현재 물 마시기와 명상 습관을 꾸준히 실천하고 계시는 걸 보니 정말 대단해요!',
    timestamp: new Date(Date.now() - 60000).toISOString(),
  },
  {
    id: 'msg_002',
    type: 'user', 
    message: '안녕하세요! 오늘 아침 명상을 했는데 정말 도움이 됐어요.',
    timestamp: new Date(Date.now() - 30000).toISOString(),
  },
  {
    id: 'msg_003',
    type: 'ai',
    message: '정말 좋은 소식이에요! 