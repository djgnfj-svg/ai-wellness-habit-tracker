import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppState, NotificationSettings } from '../../types';
import { STORAGE_KEYS } from '../../constants';

// 초기 상태
const initialState: AppState = {
  theme: 'light',
  notifications: {
    habit_reminders: true,
    ai_coaching: true,
    weekly_reports: true,
    achievement_alerts: true,
    marketing: false,
    quiet_hours: {
      enabled: true,
      start_time: '22:00',
      end_time: '08:00',
    },
  },
  hasLaunched: false,
  isOnboardingComplete: false,
  connectivity: 'online',
};

// 비동기 액션들
export const loadAppSettings = createAsyncThunk(
  'app/loadAppSettings',
  async (_, { rejectWithValue }) => {
    try {
      const [hasLaunched, notificationSettings, onboardingComplete] = await AsyncStorage.multiGet([
        STORAGE_KEYS.HAS_LAUNCHED,
        STORAGE_KEYS.NOTIFICATION_SETTINGS,
        STORAGE_KEYS.ONBOARDING_COMPLETED,
      ]);

      return {
        hasLaunched: hasLaunched[1] === 'true',
        notifications: notificationSettings[1] 
          ? JSON.parse(notificationSettings[1]) 
          : initialState.notifications,
        isOnboardingComplete: onboardingComplete[1] === 'true',
      };
    } catch (error: any) {
      return rejectWithValue('앱 설정 로드에 실패했습니다.');
    }
  }
);

export const updateNotificationSettings = createAsyncThunk(
  'app/updateNotificationSettings',
  async (settings: NotificationSettings, { rejectWithValue }) => {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.NOTIFICATION_SETTINGS, JSON.stringify(settings));
      return settings;
    } catch (error: any) {
      return rejectWithValue('알림 설정 저장에 실패했습니다.');
    }
  }
);

export const completeOnboarding = createAsyncThunk(
  'app/completeOnboarding',
  async (_, { rejectWithValue }) => {
    try {
      await AsyncStorage.multiSet([
        [STORAGE_KEYS.HAS_LAUNCHED, 'true'],
        [STORAGE_KEYS.ONBOARDING_COMPLETED, 'true'],
      ]);
      return true;
    } catch (error: any) {
      return rejectWithValue('온보딩 완료 저장에 실패했습니다.');
    }
  }
);

export const setFirstLaunch = createAsyncThunk(
  'app/setFirstLaunch',
  async (_, { rejectWithValue }) => {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.HAS_LAUNCHED, 'true');
      return true;
    } catch (error: any) {
      return rejectWithValue('첫 실행 설정 저장에 실패했습니다.');
    }
  }
);

// 슬라이스 생성
export const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    setConnectivity: (state, action: PayloadAction<'online' | 'offline'>) => {
      state.connectivity = action.payload;
    },
    toggleNotification: (state, action: PayloadAction<keyof Omit<NotificationSettings, 'quiet_hours'>>) => {
      state.notifications[action.payload] = !state.notifications[action.payload];
    },
    updateQuietHours: (state, action: PayloadAction<{ start_time: string; end_time: string }>) => {
      state.notifications.quiet_hours = {
        ...state.notifications.quiet_hours,
        ...action.payload,
      };
    },
    toggleQuietHours: (state) => {
      state.notifications.quiet_hours.enabled = !state.notifications.quiet_hours.enabled;
    },
    resetAppState: (state) => {
      return {
        ...initialState,
        hasLaunched: true, // 이미 설치된 앱이므로 유지
      };
    },
  },
  extraReducers: (builder) => {
    // 앱 설정 로드
    builder
      .addCase(loadAppSettings.fulfilled, (state, action) => {
        state.hasLaunched = action.payload.hasLaunched;
        state.notifications = action.payload.notifications;
        state.isOnboardingComplete = action.payload.isOnboardingComplete;
      })
      .addCase(loadAppSettings.rejected, (state) => {
        // 실패해도 기본값 유지
      });

    // 알림 설정 업데이트
    builder
      .addCase(updateNotificationSettings.fulfilled, (state, action) => {
        state.notifications = action.payload;
      })
      .addCase(updateNotificationSettings.rejected, (state) => {
        // 실패해도 현재 상태 유지
      });

    // 온보딩 완료
    builder
      .addCase(completeOnboarding.fulfilled, (state) => {
        state.hasLaunched = true;
        state.isOnboardingComplete = true;
      })
      .addCase(completeOnboarding.rejected, (state) => {
        // 실패해도 현재 상태 유지
      });

    // 첫 실행 설정
    builder
      .addCase(setFirstLaunch.fulfilled, (state) => {
        state.hasLaunched = true;
      })
      .addCase(setFirstLaunch.rejected, (state) => {
        // 실패해도 현재 상태 유지
      });
  },
});

// 액션 내보내기
export const {
  setTheme,
  setConnectivity,
  toggleNotification,
  updateQuietHours,
  toggleQuietHours,
  resetAppState,
} = appSlice.actions;

// 셀렉터
export const selectApp = (state: { app: AppState }) => state.app;
export const selectTheme = (state: { app: AppState }) => state.app.theme;
export const selectNotifications = (state: { app: AppState }) => state.app.notifications;
export const selectHasLaunched = (state: { app: AppState }) => state.app.hasLaunched;
export const selectIsOnboardingComplete = (state: { app: AppState }) => state.app.isOnboardingComplete;
export const selectConnectivity = (state: { app: AppState }) => state.app.connectivity;
export const selectIsOnline = (state: { app: AppState }) => state.app.connectivity === 'online';

export default appSlice.reducer;