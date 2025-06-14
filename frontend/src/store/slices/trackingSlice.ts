import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { TrackingState, HabitLog, StreakData, ProgressSummary } from '../../types';
import { trackingApi } from '../api/trackingApi';

// 초기 상태
const initialState: TrackingState = {
  todayLogs: [],
  streaks: [],
  progress: null,
  isLoading: false,
  error: null,
};

// 비동기 액션들
export const checkInHabit = createAsyncThunk(
  'tracking/checkInHabit',
  async (checkInData: Partial<HabitLog>, { rejectWithValue }) => {
    try {
      const log = await trackingApi.checkInHabit(checkInData);
      return log;
    } catch (error: any) {
      return rejectWithValue(error.message || '체크인에 실패했습니다.');
    }
  }
);

export const fetchTodayLogs = createAsyncThunk(
  'tracking/fetchTodayLogs',
  async (_, { rejectWithValue }) => {
    try {
      const logs = await trackingApi.getTodayLogs();
      return logs;
    } catch (error: any) {
      return rejectWithValue(error.message || '오늘의 기록을 불러오는데 실패했습니다.');
    }
  }
);

export const fetchHabitLogs = createAsyncThunk(
  'tracking/fetchHabitLogs',
  async (params: { habitId: string; startDate?: string; endDate?: string }, { rejectWithValue }) => {
    try {
      const logs = await trackingApi.getHabitLogs(params.habitId, params.startDate, params.endDate);
      return logs;
    } catch (error: any) {
      return rejectWithValue(error.message || '습관 기록을 불러오는데 실패했습니다.');
    }
  }
);

export const fetchStreaks = createAsyncThunk(
  'tracking/fetchStreaks',
  async (_, { rejectWithValue }) => {
    try {
      const streaks = await trackingApi.getStreaks();
      return streaks;
    } catch (error: any) {
      return rejectWithValue(error.message || '스트릭 정보를 불러오는데 실패했습니다.');
    }
  }
);

export const fetchProgress = createAsyncThunk(
  'tracking/fetchProgress',
  async (date?: string, { rejectWithValue }) => {
    try {
      const progress = await trackingApi.getProgress(date);
      return progress;
    } catch (error: any) {
      return rejectWithValue(error.message || '진척도 정보를 불러오는데 실패했습니다.');
    }
  }
);

export const updateHabitLog = createAsyncThunk(
  'tracking/updateHabitLog',
  async ({ logId, data }: { logId: string; data: Partial<HabitLog> }, { rejectWithValue }) => {
    try {
      const updatedLog = await trackingApi.updateHabitLog(logId, data);
      return updatedLog;
    } catch (error: any) {
      return rejectWithValue(error.message || '기록 수정에 실패했습니다.');
    }
  }
);

export const deleteHabitLog = createAsyncThunk(
  'tracking/deleteHabitLog',
  async (logId: string, { rejectWithValue }) => {
    try {
      await trackingApi.deleteHabitLog(logId);
      return logId;
    } catch (error: any) {
      return rejectWithValue(error.message || '기록 삭제에 실패했습니다.');
    }
  }
);

// 슬라이스 생성
export const trackingSlice = createSlice({
  name: 'tracking',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setTodayLogs: (state, action: PayloadAction<HabitLog[]>) => {
      state.todayLogs = action.payload;
    },
    addTodayLog: (state, action: PayloadAction<HabitLog>) => {
      // 같은 습관의 기존 로그가 있으면 업데이트, 없으면 추가
      const existingIndex = state.todayLogs.findIndex(
        log => log.user_habit_id === action.payload.user_habit_id
      );
      
      if (existingIndex !== -1) {
        state.todayLogs[existingIndex] = action.payload;
      } else {
        state.todayLogs.push(action.payload);
      }
    },
    updateLogInList: (state, action: PayloadAction<HabitLog>) => {
      const index = state.todayLogs.findIndex(log => log.id === action.payload.id);
      if (index !== -1) {
        state.todayLogs[index] = action.payload;
      }
    },
    removeLogFromList: (state, action: PayloadAction<string>) => {
      state.todayLogs = state.todayLogs.filter(log => log.id !== action.payload);
    },
    updateStreakData: (state, action: PayloadAction<StreakData>) => {
      const index = state.streaks.findIndex(
        streak => streak.user_habit_id === action.payload.user_habit_id
      );
      
      if (index !== -1) {
        state.streaks[index] = action.payload;
      } else {
        state.streaks.push(action.payload);
      }
    },
    // 로컬에서 임시로 체크인 상태 토글 (즉시 UI 업데이트용)
    toggleHabitCompletion: (state, action: PayloadAction<string>) => {
      const log = state.todayLogs.find(log => log.user_habit_id === action.payload);
      if (log) {
        log.completion_status = log.completion_status === 'completed' ? 'skipped' : 'completed';
        log.completion_percentage = log.completion_status === 'completed' ? 100 : 0;
      }
    },
  },
  extraReducers: (builder) => {
    // 체크인
    builder
      .addCase(checkInHabit.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(checkInHabit.fulfilled, (state, action) => {
        state.isLoading = false;
        
        // 오늘 로그에 추가 또는 업데이트
        const existingIndex = state.todayLogs.findIndex(
          log => log.user_habit_id === action.payload.user_habit_id
        );
        
        if (existingIndex !== -1) {
          state.todayLogs[existingIndex] = action.payload;
        } else {
          state.todayLogs.push(action.payload);
        }
        
        state.error = null;
      })
      .addCase(checkInHabit.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 오늘의 로그 조회
    builder
      .addCase(fetchTodayLogs.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTodayLogs.fulfilled, (state, action) => {
        state.isLoading = false;
        state.todayLogs = action.payload;
        state.error = null;
      })
      .addCase(fetchTodayLogs.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 스트릭 조회
    builder
      .addCase(fetchStreaks.fulfilled, (state, action) => {
        state.streaks = action.payload;
      })
      .addCase(fetchStreaks.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // 진척도 조회
    builder
      .addCase(fetchProgress.fulfilled, (state, action) => {
        state.progress = action.payload;
      })
      .addCase(fetchProgress.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // 로그 수정
    builder
      .addCase(updateHabitLog.fulfilled, (state, action) => {
        const index = state.todayLogs.findIndex(log => log.id === action.payload.id);
        if (index !== -1) {
          state.todayLogs[index] = action.payload;
        }
      })
      .addCase(updateHabitLog.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // 로그 삭제
    builder
      .addCase(deleteHabitLog.fulfilled, (state, action) => {
        state.todayLogs = state.todayLogs.filter(log => log.id !== action.payload);
      })
      .addCase(deleteHabitLog.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

// 액션 내보내기
export const {
  clearError,
  setTodayLogs,
  addTodayLog,
  updateLogInList,
  removeLogFromList,
  updateStreakData,
  toggleHabitCompletion,
} = trackingSlice.actions;

// 셀렉터
export const selectTracking = (state: { tracking: TrackingState }) => state.tracking;
export const selectTodayLogs = (state: { tracking: TrackingState }) => state.tracking.todayLogs;
export const selectStreaks = (state: { tracking: TrackingState }) => state.tracking.streaks;
export const selectProgress = (state: { tracking: TrackingState }) => state.tracking.progress;
export const selectTrackingLoading = (state: { tracking: TrackingState }) => state.tracking.isLoading;
export const selectTrackingError = (state: { tracking: TrackingState }) => state.tracking.error;

// 특정 습관의 오늘 로그 찾기
export const selectTodayLogByHabitId = (habitId: string) => (state: { tracking: TrackingState }) =>
  state.tracking.todayLogs.find(log => log.user_habit_id === habitId);

// 특정 습관의 스트릭 정보 찾기
export const selectStreakByHabitId = (habitId: string) => (state: { tracking: TrackingState }) =>
  state.tracking.streaks.find(streak => streak.user_habit_id === habitId);

// 완료된 습관 수 계산
export const selectCompletedHabitsCount = (state: { tracking: TrackingState }) =>
  state.tracking.todayLogs.filter(log => log.completion_status === 'completed').length;

// 전체 완료율 계산
export const selectTodayCompletionRate = (state: { tracking: TrackingState }) => {
  const logs = state.tracking.todayLogs;
  if (logs.length === 0) return 0;
  
  const completedCount = logs.filter(log => log.completion_status === 'completed').length;
  return Math.round((completedCount / logs.length) * 100);
};

// 현재 최대 스트릭 계산
export const selectMaxCurrentStreak = (state: { tracking: TrackingState }) => {
  const streaks = state.tracking.streaks;
  if (streaks.length === 0) return 0;
  
  return Math.max(...streaks.map(streak => streak.current_streak));
};

export default trackingSlice.reducer;