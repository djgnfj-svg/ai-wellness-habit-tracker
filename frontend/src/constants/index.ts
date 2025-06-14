// API 베이스 URL 설정
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1'  // 개발 환경
  : 'https://api.wellnessai.com/api/v1';  // 프로덕션 환경

// API 엔드포인트
export const API_ENDPOINTS = {
  // 인증
  AUTH: {
    KAKAO_LOGIN: '/auth/kakao/login',
    NAVER_LOGIN: '/auth/naver/login', 
    GOOGLE_LOGIN: '/auth/google/login',
    REFRESH_TOKEN: '/auth/refresh',
    LOGOUT: '/auth/logout',
  },
  
  // 사용자
  USERS: {
    PROFILE: '/users/profile',
    WELLNESS_PROFILE: '/users/wellness-profile',
    PERSONALIZATION: '/users/personalization',
  },
  
  // 습관
  HABITS: {
    LIST: '/habits',
    DETAIL: (id: string) => `/habits/${id}`,
    TEMPLATES: '/habits/templates',
    CATEGORIES: '/habits/categories',
    RECOMMENDATIONS: '/habits/recommendations',
  },
  
  // 추적
  TRACKING: {
    CHECK_IN: '/tracking/checkin',
    LOGS: '/tracking/logs',
    PROGRESS: '/tracking/progress',
    STREAKS: '/tracking/streaks',
  },
  
  // AI 코칭
  AI_COACHING: {
    CHAT: '/ai-coaching/chat',
    INSIGHTS: '/ai-coaching/insights',
    CARDS: '/ai-coaching/cards',
  },
  
  // 분석
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard',
    WEEKLY_REPORT: '/analytics/weekly-report',
    MONTHLY_REPORT: '/analytics/monthly-report',
  },
  
  // 알림
  NOTIFICATIONS: {
    SETTINGS: '/notifications/settings',
    DEVICE_TOKEN: '/notifications/device-token',
  },
} as const;

// HTTP 상태 코드
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;

// 앱 설정
export const APP_CONFIG = {
  NAME: 'WellnessAI',
  VERSION: '1.0.0',
  SUPPORT_EMAIL: 'support@wellnessai.com',
  PRIVACY_URL: 'https://wellnessai.com/privacy',
  TERMS_URL: 'https://wellnessai.com/terms',
} as const;

// 스토리지 키
export const STORAGE_KEYS = {
  USER_TOKEN: 'userToken',
  REFRESH_TOKEN: 'refreshToken',
  USER_PROFILE: 'userProfile',
  HAS_LAUNCHED: 'hasLaunched',
  NOTIFICATION_SETTINGS: 'notificationSettings',
  ONBOARDING_COMPLETED: 'onboardingCompleted',
} as const;

// 색상 테마
export const COLORS = {
  PRIMARY: '#34C759',
  SECONDARY: '#007AFF',
  DANGER: '#FF3B30',
  WARNING: '#FF9500',
  SUCCESS: '#34C759',
  
  TEXT: {
    PRIMARY: '#1C1C1E',
    SECONDARY: '#8E8E93',
    TERTIARY: '#C7C7CC',
  },
  
  BACKGROUND: {
    PRIMARY: '#FFFFFF',
    SECONDARY: '#F2F2F7',
    CARD: '#FFFFFF',
  },
  
  BORDER: {
    PRIMARY: '#F2F2F7',
    SECONDARY: '#C7C7CC',
  },
} as const;

// 애니메이션 설정
export const ANIMATION = {
  DURATION: {
    SHORT: 200,
    MEDIUM: 300,
    LONG: 500,
  },
  EASING: {
    EASE_IN_OUT: 'easeInOut',
    EASE_OUT: 'easeOut',
  },
} as const;

// 폰트 크기
export const FONT_SIZES = {
  CAPTION: 12,
  BODY: 16,
  TITLE: 18,
  LARGE_TITLE: 22,
  HEADLINE: 28,
} as const;

// 간격
export const SPACING = {
  XS: 4,
  SM: 8,
  MD: 12,
  LG: 16,
  XL: 20,
  XXL: 24,
} as const;