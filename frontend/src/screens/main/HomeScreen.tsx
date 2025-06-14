import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  RefreshControl,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { useSelector, useDispatch } from 'react-redux';

import { RootState, AppDispatch } from '../../store';
import { trackingService } from '../../services';
import { COLORS, SPACING } from '../../constants';
import { UserHabit, HabitLog } from '../../types';

interface TodayHabitItem {
  user_habit_id: string;
  habit_name: string;
  target: number;
  completed: number;
  completion_rate: number;
  status: string;
  next_reminder?: string;
  logs: HabitLog[];
  emoji?: string;
}

interface TodayHabitsData {
  date: string;
  overall_completion_rate: number;
  total_habits: number;
  completed_habits: number;
  habits: TodayHabitItem[];
  mood_average: number;
  ai_insights: string[];
}

const HomeScreen = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch<AppDispatch>();
  
  // Redux state
  const { user } = useSelector((state: RootState) => state.auth);
  const { userHabits } = useSelector((state: RootState) => state.habits);
  
  // Local state
  const [todayData, setTodayData] = useState<TodayHabitsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [currentStreak, setCurrentStreak] = useState(7);

  const userName = user?.nickname || '사용자';

  // Load today's habits data
  const loadTodayData = async (showRefreshing = false) => {
    try {
      if (showRefreshing) setIsRefreshing(true);
      else setIsLoading(true);

      const response = await trackingService.getTodayHabits();
      setTodayData(response);
      
      // Get streak data
      const streaks = await trackingService.getStreaks();
      if (streaks.length > 0) {
        const maxStreak = Math.max(...streaks.map(s => s.current_streak));
        setCurrentStreak(maxStreak);
      }
    } catch (error) {
      console.error('Failed to load today data:', error);
      Alert.alert('오류', '데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  // Load data on screen focus
  useFocusEffect(
    React.useCallback(() => {
      loadTodayData();
    }, [])
  );

  // Pull to refresh
  const onRefresh = () => {
    loadTodayData(true);
  };

  // Handle habit toggle
  const handleHabitToggle = async (habitItem: TodayHabitItem) => {
    try {
      const isCompleting = habitItem.status !== 'completed';
      
      await trackingService.checkInHabit({
        user_habit_id: habitItem.user_habit_id,
        completion_status: isCompleting ? 'completed' : 'skipped',
        completion_percentage: isCompleting ? 100 : 0,
        mood_after: 7, // Default mood
      });

      // Refresh data after check-in
      loadTodayData();
    } catch (error) {
      console.error('Failed to check in habit:', error);
      Alert.alert('오류', '체크인에 실패했습니다.');
    }
  };

  const handleAICoachTap = () => {
    navigation.navigate('AICoach' as never);
  };

  const handleNotificationPress = () => {
    Alert.alert('알림', '새로운 알림이 없습니다.');
  };

  const handleSettingsPress = () => {
    navigation.navigate('Profile' as never);
  };

  const getCurrentTime = () => {
    const now = new Date();
    const hours = now.getHours();
    
    if (hours < 12) return '오전';
    if (hours < 18) return '오후';
    return '저녁';
  };

  const getGreetingMessage = () => {
    const timeOfDay = getCurrentTime();
    return `${timeOfDay} 좋은 시간이에요, ${userName}님! 😊`;
  };

  // Get emoji for habit (fallback to default emojis)
  const getHabitEmoji = (habitName: string, index: number) => {
    const defaultEmojis = ['💧', '🧘‍♀️', '🚶‍♀️', '🤸‍♀️', '📝', '🥗', '💊', '📱'];
    
    if (habitName.includes('물')) return '💧';
    if (habitName.includes('명상')) return '🧘‍♀️';
    if (habitName.includes('산책') || habitName.includes('걷기')) return '🚶‍♀️';
    if (habitName.includes('스트레칭')) return '🤸‍♀️';
    if (habitName.includes('일기')) return '📝';
    if (habitName.includes('식사') || habitName.includes('음식')) return '🥗';
    if (habitName.includes('영양제') || habitName.includes('비타민')) return '💊';
    if (habitName.includes('독서')) return '📚';
    if (habitName.includes('운동')) return '💪';
    
    return defaultEmojis[index % defaultEmojis.length];
  };

  if (isLoading && !todayData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>로딩 중...</Text>
        </View>
      </SafeAreaView>
    );
  }

  const completedCount = todayData?.completed_habits || 0;
  const totalCount = todayData?.total_habits || 0;
  const completionRate = Math.round((todayData?.overall_completion_rate || 0) * 100);
  const aiMessage = todayData?.ai_insights?.[0] || '오늘도 건강한 하루 보내세요! 💪';

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleNotificationPress}>
          <Ionicons name="notifications-outline" size={24} color={COLORS.TEXT.PRIMARY} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>WellnessAI</Text>
        <TouchableOpacity onPress={handleSettingsPress}>
          <Ionicons name="settings-outline" size={24} color={COLORS.TEXT.PRIMARY} />
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.content} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={onRefresh}
            tintColor={COLORS.PRIMARY}
          />
        }
      >
        {/* Greeting */}
        <View style={styles.greetingContainer}>
          <Text style={styles.greetingText}>{getGreetingMessage()}</Text>
          <Text style={styles.subGreetingText}>오늘도 건강한 하루 보내세요</Text>
        </View>

        {/* Progress Card */}
        <View style={styles.progressCard}>
          <Text style={styles.progressTitle}>오늘의 진행상황</Text>
          <View style={styles.progressContent}>
            <View style={styles.progressInfo}>
              <Text style={styles.progressStats}>
                💪 {completedCount}/{totalCount} 완료 ({completionRate}%)
              </Text>
              <View style={styles.progressBarContainer}>
                <View style={styles.progressBar}>
                  <View 
                    style={[
                      styles.progressBarFill, 
                      { width: `${completionRate}%` }
                    ]} 
                  />
                </View>
                <Text style={styles.streakText}>🔥{currentStreak}일 연속</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Today's Habits */}
        <View style={styles.habitsCard}>
          <Text style={styles.habitsTitle}>오늘의 습관</Text>
          <View style={styles.habitsList}>
            {todayData?.habits?.map((habit, index) => (
              <TouchableOpacity
                key={habit.user_habit_id}
                style={[
                  styles.habitItem,
                  habit.status === 'completed' && styles.completedHabit
                ]}
                onPress={() => handleHabitToggle(habit)}
                activeOpacity={0.7}
              >
                <View style={styles.habitContent}>
                  <View style={styles.habitInfo}>
                    <Text style={styles.habitEmoji}>
                      {getHabitEmoji(habit.habit_name, index)}
                    </Text>
                    <View style={styles.habitTextContainer}>
                      <Text style={[
                        styles.habitName,
                        habit.status === 'completed' && styles.completedHabitText
                      ]}>
                        {habit.habit_name}
                      </Text>
                      {habit.target > 1 && (
                        <Text style={styles.habitProgress}>
                          ({habit.completed}/{habit.target})
                        </Text>
                      )}
                      {habit.next_reminder && habit.status !== 'completed' && (
                        <Text style={styles.scheduledTime}>
                          ⏰ {habit.next_reminder}
                        </Text>
                      )}
                    </View>
                  </View>
                  <View style={[
                    styles.habitStatus,
                    habit.status === 'completed' ? styles.completedStatus : styles.pendingStatus
                  ]}>
                    {habit.status === 'completed' ? (
                      <Ionicons name="checkmark" size={16} color="white" />
                    ) : (
                      <Text style={styles.pendingStatusText}>❌</Text>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            )) || []}
            
            {(!todayData?.habits || todayData.habits.length === 0) && (
              <View style={styles.emptyHabits}>
                <Text style={styles.emptyHabitsText}>오늘 등록된 습관이 없습니다</Text>
                <TouchableOpacity
                  style={styles.addHabitButton}
                  onPress={() => navigation.navigate('Profile' as never)}
                >
                  <Text style={styles.addHabitButtonText}>습관 추가하기</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>

        {/* AI Coach Message */}
        <TouchableOpacity 
          style={styles.aiCoachCard}
          onPress={handleAICoachTap}
          activeOpacity={0.8}
        >
          <Text style={styles.aiCoachTitle}>AI 코치 메시지</Text>
          <View style={styles.aiMessageContainer}>
            <Text style={styles.aiCoachIcon}>🤖</Text>
            <View style={styles.aiMessageContent}>
              <Text style={styles.aiMessage}>"{aiMessage}"</Text>
              <View style={styles.aiMessageAction}>
                <Text style={styles.actionText}>답변하기</Text>
                <Ionicons name="chevron-forward" size={16} color={COLORS.PRIMARY} />
              </View>
            </View>
          </View>
        </TouchableOpacity>

        {/* Quick Actions */}
        <View style={styles.quickActionsContainer}>
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={() => navigation.navigate('Checkin' as never)}
          >
            <Ionicons name="add-circle" size={24} color={COLORS.PRIMARY} />
            <Text style={styles.quickActionText}>체크인</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={() => navigation.navigate('Stats' as never)}
          >
            <Ionicons name="bar-chart" size={24} color={COLORS.SECONDARY} />
            <Text style={styles.quickActionText}>통계 보기</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND.SECONDARY,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: COLORS.TEXT.SECONDARY,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.XL,
    paddingVertical: SPACING.LG,
    backgroundColor: COLORS.BACKGROUND.PRIMARY,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.BORDER.PRIMARY,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.TEXT.PRIMARY,
  },
  content: {
    flex: 1,
    padding: SPACING.XL,
  },
  greetingContainer: {
    marginBottom: SPACING.XXL,
  },
  greetingText: {
    fontSize: 22,
    fontWeight: '600',
    color: COLORS.TEXT.PRIMARY,
    marginBottom: SPACING.XS,
  },
  subGreetingText: {
    fontSize: 16,
    color: COLORS.TEXT.SECONDARY,
  },
  progressCard: {
    backgroundColor: COLORS.BACKGROUND.CARD,
    borderRadius: 16,
    padding: SPACING.XL,
    marginBottom: SPACING.XL,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT.PRIMARY,
    marginBottom: SPACING.LG,
  },
  progressContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressInfo: {
    flex: 1,
  },
  progressStats: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.PRIMARY,
    marginBottom: SPACING.MD,
  },
  progressBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.MD,
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: COLORS.BACKGROUND.SECONDARY,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 4,
  },
  streakText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF6B35',
  },
  habitsCard: {
    backgroundColor: COLORS.BACKGROUND.CARD,
    borderRadius: 16,
    padding: SPACING.XL,
    marginBottom: SPACING.XL,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  habitsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT.PRIMARY,
    marginBottom: SPACING.LG,
  },
  habitsList: {
    gap: SPACING.MD,
  },
  habitItem: {
    backgroundColor: COLORS.BACKGROUND.SECONDARY,
    borderRadius: 12,
    padding: SPACING.LG,
  },
  completedHabit: {
    backgroundColor: '#F0FDF4',
  },
  habitContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  habitInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  habitEmoji: {
    fontSize: 20,
    marginRight: SPACING.MD,
  },
  habitTextContainer: {
    flex: 1,
  },
  habitName: {
    fontSize: 16,
    fontWeight: '500',
    color: COLORS.TEXT.PRIMARY,
    marginBottom: 2,
  },
  completedHabitText: {
    textDecorationLine: 'line-through',
    color: COLORS.TEXT.SECONDARY,
  },
  habitProgress: {
    fontSize: 14,
    color: COLORS.TEXT.SECONDARY,
  },
  scheduledTime: {
    fontSize: 12,
    color: COLORS.SECONDARY,
    marginTop: 2,
  },
  habitStatus: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  completedStatus: {
    backgroundColor: COLORS.PRIMARY,
  },
  pendingStatus: {
    backgroundColor: 'transparent',
  },
  pendingStatusText: {
    fontSize: 16,
  },
  emptyHabits: {
    alignItems: 'center',
    paddingVertical: SPACING.XXL,
  },
  emptyHabitsText: {
    fontSize: 16,
    color: COLORS.TEXT.SECONDARY,
    marginBottom: SPACING.LG,
  },
  addHabitButton: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: SPACING.XL,
    paddingVertical: SPACING.MD,
    borderRadius: 8,
  },
  addHabitButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  aiCoachCard: {
    backgroundColor: COLORS.BACKGROUND.CARD,
    borderRadius: 16,
    padding: SPACING.XL,
    marginBottom: SPACING.XL,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  aiCoachTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT.PRIMARY,
    marginBottom: SPACING.LG,
  },
  aiMessageContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  aiCoachIcon: {
    fontSize: 24,
    marginRight: SPACING.MD,
  },
  aiMessageContent: {
    flex: 1,
  },
  aiMessage: {
    fontSize: 16,
    color: COLORS.TEXT.PRIMARY,
    lineHeight: 22,
    marginBottom: SPACING.SM,
  },
  aiMessageAction: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionText: {
    fontSize: 14,
    color: COLORS.PRIMARY,
    fontWeight: '600',
    marginRight: SPACING.XS,
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    gap: SPACING.MD,
    marginBottom: SPACING.XL,
  },
  quickActionButton: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND.CARD,
    borderRadius: 12,
    padding: SPACING.LG,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT.PRIMARY,
    marginTop: SPACING.SM,
  },
});

export default HomeScreen;
