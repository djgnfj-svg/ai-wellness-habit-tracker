import { configureStore } from '@reduxjs/toolkit';
import { authSlice } from './slices/authSlice';
import { habitsSlice } from './slices/habitsSlice';
import { trackingSlice } from './slices/trackingSlice';
import { aiCoachingSlice } from './slices/aiCoachingSlice';
import { appSlice } from './slices/appSlice';
import { apiSlice } from './api/apiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    habits: habitsSlice.reducer,
    tracking: trackingSlice.reducer,
    aiCoaching: aiCoachingSlice.reducer,
    app: appSlice.reducer,
    api: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }).concat(apiSlice.middleware),
  devTools: __DEV__,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;