// API 서비스들을 한 곳에서 export
export { default as apiClient } from './apiClient';
export { default as authService } from './authService';
export { default as userService } from './userService';
export { default as habitsService } from './habitsService';
export { default as trackingService } from './trackingService';
export { default as aiCoachingService } from './aiCoachingService';

// 편의를 위한 통합 서비스 객체
export const services = {
  api: apiClient,
  auth: authService,
  user: userService,
  habits: habitsService,
  tracking: trackingService,
  aiCoaching: aiCoachingService,
};

// 타입들도 re-export
export type {
  LoginRequest,
  LoginResponse,
  User,
  UserHabit,
  HabitTemplate,
  HabitLog,
  ChatMessage,
  CoachingCard,
} from '../types';
