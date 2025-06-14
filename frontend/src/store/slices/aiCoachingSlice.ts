import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AICoachingState, ChatMessage, CoachingCard, AIInsight } from '../../types';
import { aiCoachingApi } from '../api/aiCoachingApi';

// 초기 상태
const initialState: AICoachingState = {
  messages: [],
  coachingCards: [],
  insights: [],
  isTyping: false,
  isLoading: false,
  error: null,
};

// 비동기 액션들
export const sendChatMessage = createAsyncThunk(
  'aiCoaching/sendChatMessage',
  async (message: string, { rejectWithValue }) => {
    try {
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'user',
        message,
        timestamp: new Date().toISOString(),
      };

      const response = await aiCoachingApi.sendMessage(message);
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        message: response.message,
        timestamp: new Date().toISOString(),
        context: response.context,
      };

      return { userMessage, aiMessage };
    } catch (error: any) {
      return rejectWithValue(error.message || 'AI 코칭 메시지 전송에 실패했습니다.');
    }
  }
);

export const loadCoachingCards = createAsyncThunk(
  'aiCoaching/loadCoachingCards',
  async (_, { rejectWithValue }) => {
    try {
      const cards = await aiCoachingApi.getCoachingCards();
      return cards;
    } catch (error: any) {
      return rejectWithValue(error.message || '코칭 카드 로드에 실패했습니다.');
    }
  }
);

export const loadInsights = createAsyncThunk(
  'aiCoaching/loadInsights',
  async (_, { rejectWithValue }) => {
    try {
      const insights = await aiCoachingApi.getInsights();
      return insights;
    } catch (error: any) {
      return rejectWithValue(error.message || '인사이트 로드에 실패했습니다.');
    }
  }
);

export const dismissCoachingCard = createAsyncThunk(
  'aiCoaching/dismissCoachingCard',
  async (cardId: string, { rejectWithValue }) => {
    try {
      await aiCoachingApi.dismissCard(cardId);
      return cardId;
    } catch (error: any) {
      return rejectWithValue(error.message || '카드 제거에 실패했습니다.');
    }
  }
);

// 슬라이스 생성
export const aiCoachingSlice = createSlice({
  name: 'aiCoaching',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    removeCoachingCard: (state, action: PayloadAction<string>) => {
      state.coachingCards = state.coachingCards.filter(
        card => card.id !== action.payload
      );
    },
    updateCoachingCard: (state, action: PayloadAction<CoachingCard>) => {
      const index = state.coachingCards.findIndex(
        card => card.id === action.payload.id
      );
      if (index !== -1) {
        state.coachingCards[index] = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    // 채팅 메시지 전송
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.isLoading = true;
        state.isTyping = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isTyping = false;
        state.messages.push(action.payload.userMessage);
        state.messages.push(action.payload.aiMessage);
        state.error = null;
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.isTyping = false;
        state.error = action.payload as string;
      });

    // 코칭 카드 로드
    builder
      .addCase(loadCoachingCards.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadCoachingCards.fulfilled, (state, action) => {
        state.isLoading = false;
        state.coachingCards = action.payload;
        state.error = null;
      })
      .addCase(loadCoachingCards.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // 인사이트 로드
    builder
      .addCase(loadInsights.fulfilled, (state, action) => {
        state.insights = action.payload;
      })
      .addCase(loadInsights.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // 코칭 카드 제거
    builder
      .addCase(dismissCoachingCard.fulfilled, (state, action) => {
        state.coachingCards = state.coachingCards.filter(
          card => card.id !== action.payload
        );
      })
      .addCase(dismissCoachingCard.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

// 액션 내보내기
export const {
  clearError,
  setTyping,
  addMessage,
  clearMessages,
  removeCoachingCard,
  updateCoachingCard,
} = aiCoachingSlice.actions;

// 셀렉터
export const selectAICoaching = (state: { aiCoaching: AICoachingState }) => state.aiCoaching;
export const selectMessages = (state: { aiCoaching: AICoachingState }) => state.aiCoaching.messages;
export const selectCoachingCards = (state: { aiCoaching: AICoachingState }) => state.aiCoaching.coachingCards;
export const selectInsights = (state: { aiCoaching: AICoachingState }) => state.aiCoaching.insights;
export const selectIsTyping = (state: { aiCoaching: AICoachingState }) => state.aiCoaching.isTyping;
export const selectAICoachingLoading = (state: { aiCoaching: AICoachingState }) => state.aiCoaching.isLoading;
export const selectAICoachingError = (state: { aiCoaching: AICoachingState }) => state.aiCoaching.error;

export default aiCoachingSlice.reducer;