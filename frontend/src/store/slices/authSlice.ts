import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthState, User, LoginRequest, LoginResponse } from '../../types';
import { STORAGE_KEYS } from '../../constants';
import { authApi } from '../api/authApi';

// 초기 상태
const initialState: AuthState = {
  user: null,
  tokens: {
    access: null,
    refresh: null,
  },
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// 비동기 액션들
export const loginWithProvider = createAsyncThunk(
  'auth/loginWithProvider',
  async (loginData: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authApi.login(loginData);
      
      // 토큰을 AsyncStorage에 저장
      await AsyncStorage.setItem(STORAGE_KEYS.USER_TOKEN, response.access_token);
      await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token);
      await AsyncStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(response.user));
      await AsyncStorage.setItem(STORAGE_KEYS.HAS_LAUNCHED, 'true');
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || '로그인에 실패했습니다.');
    }
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
      if (!refreshToken) {
        throw new Error('Refresh token not found');
      }
      
      const response = await authApi.refreshToken({ refresh_token: refreshToken });
      
      // 새로운 토큰 저장
      await AsyncStorage.setItem(STORAGE_KEYS.USER_TOKEN, response.access_token);
      await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token);
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || '토큰 갱신에 실패했습니다.');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      // 서버에 로그아웃 요청
      await authApi.logout();
      
      // 로컬 스토리지 정리
      await AsyncStorage.multiRemove([
        STORAGE_KEYS.USER_TOKEN,
        STORAGE_KEYS.REFRESH_TOKEN,
        STORAGE_KEYS.USER_PROFILE,
      ]);
      
      return true;
    } catch (error: any) {
      // 로그아웃은 실패해도 로컬 상태는 정리
      await AsyncStorage.multiRemove([
        STORAGE_KEYS.USER_TOKEN,
        STORAGE_KEYS.REFRESH_TOKEN,
        STORAGE_KEYS.USER_PROFILE,
      ]);
      
      return true;
    }
  }
);

export const loadStoredAuth = createAsyncThunk(
  'auth/loadStoredAuth',
  async (_, { rejectWithValue }) => {
    try {
      const [accessToken, refreshTokenValue, userProfile] = await AsyncStorage.multiGet([
        STORAGE_KEYS.USER_TOKEN,
        STORAGE_KEYS.REFRESH_TOKEN,
        STORAGE_KEYS.USER_PROFILE,
      ]);
      
      const access = accessToken[1];
      const refresh = refreshTokenValue[1];
      const profile = userProfile[1];
      
      if (!access || !refresh || !profile) {
        throw new Error('Authentication data not found');
      }
      
      const user: User = JSON.parse(profile);
      
      return {
        user,
        tokens: {
          access,
          refresh,
        },
      };
    } catch (error: any) {
      return rejectWithValue('저장된 인증 정보가 없습니다.');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData: Partial<User>, { rejectWithValue }) => {
    try {
      const response = await authApi.updateProfile(profileData);
      
      // 업데이트된 사용자 정보를 저장
      await AsyncStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(response));
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || '프로필 업데이트에 실패했습니다.');
    }
  }
);

// 슬라이스 생성
export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    clearAuth: (state) => {
      state.user = null;
      state.tokens = { access: null, refresh: null };
      state.isAuthenticated = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 로그인
    builder
      .addCase(loginWithProvider.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginWithProvider.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = {
          access: action.payload.access_token,
          refresh: action.payload.refresh_token,
        };
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginWithProvider.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // 토큰 갱신
    builder
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.tokens = {
          access: action.payload.access_token,
          refresh: action.payload.refresh_token,
        };
        state.error = null;
      })
      .addCase(refreshToken.rejected, (state) => {
        state.user = null;
        state.tokens = { access: null, refresh: null };
        state.isAuthenticated = false;
      });

    // 로그아웃
    builder
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.tokens = { access: null, refresh: null };
        state.isAuthenticated = false;
        state.error = null;
      });

    // 저장된 인증 정보 로드
    builder
      .addCase(loadStoredAuth.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(loadStoredAuth.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loadStoredAuth.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
      });

    // 프로필 업데이트
    builder
      .addCase(updateProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

// 액션 내보내기
export const { clearError, setUser, clearAuth } = authSlice.actions;

// 셀렉터
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectUser = (state: { auth: AuthState }) => state.auth.user;
export const selectIsAuthenticated = (state: { auth: AuthState }) => state.auth.isAuthenticated;
export const selectAuthLoading = (state: { auth: AuthState }) => state.auth.isLoading;
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;
export const selectAccessToken = (state: { auth: AuthState }) => state.auth.tokens.access;

export default authSlice.reducer;