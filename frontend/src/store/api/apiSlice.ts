import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, STORAGE_KEYS } from '../../constants';
import type { 
  User, 
  UserHabit, 
  HabitTemplate, 
  HabitCategory,
  HabitLog,
  ProgressSummary,
  WeeklyReport,
  ChatMessage,
  CoachingCard,
  AIInsight
} from '../../types';

// Base query with token handling
const baseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: async (headers) => {
    const token = await AsyncStorage.getItem(STORAGE_KEYS.USER_TOKEN);
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    headers.set('content-type', 'application/json');
    return headers;
  },
});

// Enhanced base query with token refresh
const baseQueryWithReauth = async (args: any, api: any, extraOptions: any) => {
  let result = await baseQuery(args, api, extraOptions);
  
  if (result?.error?.status === 401) {
    // Try to refresh token
    const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    if (refreshToken) {
      const refreshResult = await baseQuery(
        {
          url: '/auth/refresh',
          method: 'POST',
          body: { refresh_token: refreshToken },
        },
        api,
        extraOptions
      );
      
      if (refreshResult?.data) {
        const { access_token, refresh_token } = refreshResult.data as any;
        await AsyncStorage.setItem(STORAGE_KEYS.USER_TOKEN, access_token);
        await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
        
        // Retry original request with new token
        result = await baseQuery(args, api, extraOptions);
      } else {
        // Refresh failed, clear auth data
        await AsyncStorage.multiRemove([
          STORAGE_KEYS.USER_TOKEN,
          STORAGE_KEYS.REFRESH_TOKEN,
          STORAGE_KEYS.USER_PROFILE,
        ]);
        // Could dispatch logout action here
      }
    }
  }
  
  return result;
};

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    'User',
    'UserHabit', 
    'HabitTemplate',
    'HabitCategory',
    'HabitLog',
    'Progress',
    'AICoaching',
    'Analytics'
  ],
  endpoints: (builder) => ({
    // User endpoints
    getUserProfile: builder.query<User, void>({
      query: () => '/users/profile',
      providesTags: ['User'],
    }),
    
    updateUserProfile: builder.mutation<User, Partial<User>>({
      query: (userData) => ({
        url: '/users/profile',
        method: 'PUT',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),

    // Habits endpoints
    getUserHabits: builder.query<UserHabit[], void>({
      query: () => '/habits',
      providesTags: ['UserHabit'],
    }),

    getHabitTemplates: builder.query<HabitTemplate[], { category?: string }>({
      query: ({ category }) => ({
        url: '/habits/templates',
        params: category ? { category_id: category } : {},
      }),
      providesTags: ['HabitTemplate'],
    }),

    getHabitCategories: builder.query<HabitCategory[], void>({
      query: () => '/habits/categories',
      providesTags: ['HabitCategory'],
    }),

    createUserHabit: builder.mutation<UserHabit, Partial<UserHabit>>({
      query: (habitData) => ({
        url: '/habits',
        method: 'POST',
        body: habitData,
      }),
      invalidatesTags: ['UserHabit'],
    }),

    updateUserHabit: builder.mutation<UserHabit, { id: string; data: Partial<UserHabit> }>({
      query: ({ id, data }) => ({
        url: `/habits/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['UserHabit'],
    }),

    deleteUserHabit: builder.mutation<void, string>({
      query: (id) => ({
        url: `/habits/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['UserHabit'],
    }),

    // Tracking endpoints
    getTodayProgress: builder.query<ProgressSummary, void>({
      query: () => '/tracking/progress?period=today',
      providesTags: ['Progress'],
    }),

    getHabitLogs: builder.query<HabitLog[], { habitId?: string; date?: string }>({
      query: (params) => ({
        url: '/tracking/logs',
        params,
      }),
      providesTags: ['HabitLog'],
    }),

    createHabitLog: builder.mutation<HabitLog, Partial<HabitLog>>({
      query: (logData) => ({
        url: '/tracking/checkin',
        method: 'POST',
        body: logData,
      }),
      invalidatesTags: ['HabitLog', 'Progress'],
    }),

    // Analytics endpoints
    getDashboardData: builder.query<any, void>({
      query: () => '/analytics/dashboard',
      providesTags: ['Analytics'],
    }),

    getWeeklyReport: builder.query<WeeklyReport, { date: string }>({
      query: ({ date }) => ({
        url: '/analytics/weekly-report',
        params: { date },
      }),
      providesTags: ['Analytics'],
    }),

    // AI Coaching endpoints
    sendAIMessage: builder.mutation<{ message: string; context?: any }, string>({
      query: (message) => ({
        url: '/ai-coaching/chat',
        method: 'POST',
        body: { message },
      }),
      invalidatesTags: ['AICoaching'],
    }),

    getCoachingCards: builder.query<CoachingCard[], void>({
      query: () => '/ai-coaching/cards',
      providesTags: ['AICoaching'],
    }),

    getAIInsights: builder.query<AIInsight[], void>({
      query: () => '/ai-coaching/insights',
      providesTags: ['AICoaching'],
    }),

    dismissCoachingCard: builder.mutation<void, string>({
      query: (cardId) => ({
        url: `/ai-coaching/cards/${cardId}/dismiss`,
        method: 'POST',
      }),
      invalidatesTags: ['AICoaching'],
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  // User hooks
  useGetUserProfileQuery,
  useUpdateUserProfileMutation,
  
  // Habits hooks
  useGetUserHabitsQuery,
  useGetHabitTemplatesQuery,
  useGetHabitCategoriesQuery,
  useCreateUserHabitMutation,
  useUpdateUserHabitMutation,
  useDeleteUserHabitMutation,
  
  // Tracking hooks
  useGetTodayProgressQuery,
  useGetHabitLogsQuery,
  useCreateHabitLogMutation,
  
  // Analytics hooks
  useGetDashboardDataQuery,
  useGetWeeklyReportQuery,
  
  // AI Coaching hooks
  useSendAIMessageMutation,
  useGetCoachingCardsQuery,
  useGetAIInsightsQuery,
  useDismissCoachingCardMutation,
} = apiSlice;