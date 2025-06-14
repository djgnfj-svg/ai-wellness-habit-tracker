import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { HabitsState, UserHabit, HabitTemplate, HabitCategory } from '../../types';
import { habitsApi } from '../api/habitsApi';

// 초기 상태
const initialState: HabitsState = {
  userHabits: [],
  habitTemplates: [],
  categories: [],
  isLoading: false,
  error: null,
};

// 비동기 액션들
export const fetchUserHabits = createAsyncThunk(
  'habits/fetchUserHabits',
  async (_, { rejectWithValue }) => {
    try {
      const habits = await habitsApi.getUserHabits();
      return habits;
    } catch (error: any) {
      return rejectWithValue(error.message || '습관 목록을 불러오는데 실패했습니다.');
    }
  }
);

export const fetchHabitTemplates = createAsyncThunk(
  'habits/fetchHabitTemplates',
  async (_, { rejectWithValue }) => {
    try {
      const templates = await habitsApi.getHabitTemplates();
      return templates;
    } catch (error: any) {
      return rejectWithValue(error.message || '습관 템플릿을 불러오는데 실패했습니다.');
    }
  }
);

export const fetchHabitCategories = createAsyncThunk(
  'habits/fetchHabitCategories',
  async (_, { rejectWithValue }) => {
    try {
      const categories = await habitsApi.getHabitCategories();
      return categories;
    } catch (error: any) {
      return rejectWithValue(error.message || '카테고리를 불러오는데 실패했습니다.');
    }
  }
);

export const createUserHabit = createAsyncThunk(
  'habits/createUserHabit',
  async (habitData: Partial<UserHabit>, { rejectWithValue }) => {
    try {
      const newHabit = await habitsApi.createUserHabit(habitData);
      return newHabit;
    } catch (error: any) {
      return rejectWithValue(error.message || '습관 생성에 실패했습니다.');
    }
  }
);

export const updateUserHabit = createAsyncThunk(
  'habits/updateUserHabit',
  async ({ id, data }: { id: string; data: Partial<UserHabit> }, { rejectWithValue }) => {
    try {
      const updatedHabit = await habitsApi.updateUserHabit(id, data);
      return updatedHabit;
    } catch (error: any) {
      return rejectWithValue(error.message || '습관 수정에 실패했습니다.');
    }
  }
);

export const deleteUserHabit = createAsyncThunk(
  'habits/deleteUserHabit',
  async (habitId: string, { rejectWithValue }) => {
    try {
      await habitsApi.deleteUserHabit(habitId);
      return habitId;
    } catch (error: any) {
      return rejectWithValue(error.message || '습관 삭제에 실패했습니다.');
    }
  }
);

export const getHabitRecommendations = createAsyncThunk(
  'habits/getHabitRecommendations',
  async (_, { rejectWithValue }) => {
    try {
      const recommendations = await habitsApi.getHabitRecommendations();
      return recommendations;
    } catch (error: any) {
      return rejectWithValue(error.message || '추천 습관을 불러오는데 실패했습니다.');
    }
  }
);

// 슬라이스 생성
export const habitsSlice = createSlice({
  name: 'habits',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUserHabits: (state, action: PayloadAction<UserHabit[]>) => {
      state.userHabits = action.payload;
    },
    addUserHabit: (state, action: PayloadAction<UserHabit>) => {
      state.userHabits.push(action.payload);
    },
    updateHabitInList: (state, action: PayloadAction<UserHabit>) => {
      const index = state.userHabits.findIndex(habit => habit.id === action.payload.id);
      if (index !== -1) {
        state.userHabits[index] = action.payload;
      }
    },
    removeHabitFromList: (state, action: PayloadAction<string>) => {
      state.userHabits = state.userHabits.filter(habit => habit.id !== action.payload);
    },
    toggleHabitActive: (state, action: PayloadAction<string>) => {
      const habit = state.userHabits.find(h => h.id === action.payload);
      if (habit) {
        habit.is_active = !habit.is_active;
      }
    },
  },
  extraReducers: (builder) => {
    // 사용자 습관 목록 조회
    builder
      .addCase(fetchUserHabits.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserHabits.fulfilled, (state, action) => {
        state.isLoading = false;
        state.userHabits = action.payload;
        state.error = null;
      })
      .addCase(fetchUserHabits.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 습관 템플릿 조회
    builder
      .addCase(fetchHabitTemplates.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchHabitTemplates.fulfilled, (state, action) => {
        state.isLoading = false;
        state.habitTemplates = action.payload;
        state.error = null;
      })
      .addCase(fetchHabitTemplates.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 카테고리 조회
    builder
      .addCase(fetchHabitCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })
      .addCase(fetchHabitCategories.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // 습관 생성
    builder
      .addCase(createUserHabit.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createUserHabit.fulfilled, (state, action) => {
        state.isLoading = false;
        state.userHabits.push(action.payload);
        state.error = null;
      })
      .addCase(createUserHabit.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 습관 수정
    builder
      .addCase(updateUserHabit.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateUserHabit.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.userHabits.findIndex(habit => habit.id === action.payload.id);
        if (index !== -1) {
          state.userHabits[index] = action.payload;
        }
        state.error = null;
      })
      .addCase(updateUserHabit.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 습관 삭제
    builder
      .addCase(deleteUserHabit.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteUserHabit.fulfilled, (state, action) => {
        state.isLoading = false;
        state.userHabits = state.userHabits.filter(habit => habit.id !== action.payload);
        state.error = null;
      })
      .addCase(deleteUserHabit.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

// 액션 내보내기
export const {
  clearError,
  setUserHabits,
  addUserHabit,
  updateHabitInList,
  removeHabitFromList,
  toggleHabitActive,
} = habitsSlice.actions;

// 셀렉터
export const selectHabits = (state: { habits: HabitsState }) => state.habits;
export const selectUserHabits = (state: { habits: HabitsState }) => state.habits.userHabits;
export const selectActiveHabits = (state: { habits: HabitsState }) => 
  state.habits.userHabits.filter(habit => habit.is_active);
export const selectHabitTemplates = (state: { habits: HabitsState }) => state.habits.habitTemplates;
export const selectHabitCategories = (state: { habits: HabitsState }) => state.habits.categories;
export const selectHabitsLoading = (state: { habits: HabitsState }) => state.habits.isLoading;
export const selectHabitsError = (state: { habits: HabitsState }) => state.habits.error;

// 특정 습관 찾기
export const selectHabitById = (habitId: string) => (state: { habits: HabitsState }) =>
  state.habits.userHabits.find(habit => habit.id === habitId);

// 카테고리별 습관 필터링
export const selectHabitsByCategory = (categoryId: string) => (state: { habits: HabitsState }) =>
  state.habits.userHabits.filter(habit => habit.habit_template?.category_id === categoryId);

export default habitsSlice.reducer;