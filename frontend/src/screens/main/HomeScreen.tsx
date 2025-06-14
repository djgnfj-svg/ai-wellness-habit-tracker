import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';

interface HabitItem {
  id: string;
  name: string;
  target: number;
  completed: number;
  isCompleted: boolean;
  emoji: string;
  scheduledTime?: string;
}

const HomeScreen = () => {
  const navigation = useNavigation();
  const [userName, setUserName] = useState('현아');
  const [todayHabits, setTodayHabits] = useState<HabitItem[]>([
    {
      id: '1',
      name: '물 8잔 마시기',
      target: 8,
      completed: 6,
      isCompleted: false,
      emoji: '💧',
    },
    {
      id: '2',
      name: '명상 5분',
      target: 1,
      completed: 1,
      isCompleted: true,
      emoji: '🧘‍♀️',
    },
    {
      id: '3',
      name: '런치 산책',
      target: 1,
      completed: 0,
      isCompleted: false,
      emoji: '🚶‍♀️',
      scheduledTime: '12:30',
    },
    {
      id: '4',
      name: '스트레칭 10분',
      target: 1,
      completed: 0,
      isCompleted: false,
      emoji: '🤸‍♀️',
    },
    {
      id: '5',
      name: '일기 쓰기',
      target: 1,
      completed: 0,
      isCompleted: false,
      emoji: '📝',
    },
  ]);

  const [aiMessage, setAiMessage] = useState(
    '점심시간이에요! 15분 산책 어떠세요?'
  );
  const [currentStreak, setCurrentStreak] = useState(7);

  const completedCount = todayHabits.filter(habit => habit.isCompleted).length;
  const totalCount = todayHabits.length;
  const completionRate = Math.round((completedCount / totalCount) * 100);

  const handleHabitToggle = (habitId: string) => {
    setTodayHabits(prev => prev.map(habit => {
      if (habit.id === habitId) {
        const isCompleting = !habit.isCompleted;
        return {
          ...habit,
          isCompleted: isCompleting,
          completed: isCompleting ? habit.target : Math.max(0, habit.completed - 1)
        };
      }
      return habit;
    }));
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

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleNotificationPress}>
          <Ionicons name="notifications-outline" size={24} color="#1C1C1E" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>WellnessAI</Text>
        <TouchableOpacity onPress={handleSettingsPress}>
          <Ionicons name="settings-outline" size={24} color="#1C1C1E" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
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
            {todayHabits.map((habit) => (
              <TouchableOpacity
                key={habit.id}
                style={[
                  styles.habitItem,
                  habit.isCompleted && styles.completedHabit
                ]}
                onPress={() => handleHabitToggle(habit.id)}
                activeOpacity={0.7}
              >
                <View style={styles.habitContent}>
                  <View style={styles.habitInfo}>
                    <Text style={styles.habitEmoji}>{habit.emoji}</Text>
                    <View style={styles.habitTextContainer}>
                      <Text style={[
                        styles.habitName,
                        habit.isCompleted && styles.completedHabitText
                      ]}>
                        {habit.name}
                      </Text>
                      {habit.target > 1 && (
                        <Text style={styles.habitProgress}>
                          ({habit.completed}/{habit.target})
                        </Text>
                      )}
                      {habit.scheduledTime && !habit.isCompleted && (
                        <Text style={styles.scheduledTime}>
                          ⏰ {habit.scheduledTime}
                        </Text>
                      )}
                    </View>
                  </View>
                  <View style={[
                    styles.habitStatus,
                    habit.isCompleted ? styles.completedStatus : styles.pendingStatus
                  ]}>
                    {habit.isCompleted ? (
                      <Ionicons name="checkmark" size={16} color="white" />
                    ) : (
                      <Text style={styles.pendingStatusText}>❌</Text>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            ))}
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
                <Ionicons name="chevron-forward" size={16} color="#34C759" />
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
            <Ionicons name="add-circle" size={24} color="#34C759" />
            <Text style={styles.quickActionText}>체크인</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={() => navigation.navigate('Stats' as never)}
          >
            <Ionicons name="bar-chart" size={24} color="#007AFF" />
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
    backgroundColor: '#F2F2F7',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1C1C1E',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  greetingContainer: {
    marginBottom: 24,
  },
  greetingText: {
    fontSize: 22,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  subGreetingText: {
    fontSize: 16,
    color: '#8E8E93',
  },
  progressCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
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
    color: '#34C759',
    marginBottom: 12,
  },
  progressBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#F2F2F7',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#34C759',
    borderRadius: 4,
  },
  streakText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF6B35',
  },
  habitsCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  habitsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  habitsList: {
    gap: 12,
  },
  habitItem: {
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    padding: 16,
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
    marginRight: 12,
  },
  habitTextContainer: {
    flex: 1,
  },
  habitName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 2,
  },
  completedHabitText: {
    textDecorationLine: 'line-through',
    color: '#8E8E93',
  },
  habitProgress: {
    fontSize: 14,
    color: '#8E8E93',
  },
  scheduledTime: {
    fontSize: 12,
    color: '#007AFF',
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
    backgroundColor: '#34C759',
  },
  pendingStatus: {
    backgroundColor: 'transparent',
  },
  pendingStatusText: {
    fontSize: 16,
  },
  aiCoachCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  aiCoachTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  aiMessageContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  aiCoachIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  aiMessageContent: {
    flex: 1,
  },
  aiMessage: {
    fontSize: 16,
    color: '#1C1C1E',
    lineHeight: 22,
    marginBottom: 8,
  },
  aiMessageAction: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionText: {
    fontSize: 14,
    color: '#34C759',
    fontWeight: '600',
    marginRight: 4,
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    gap: 12,
    marginBottom: 20,
  },
  quickActionButton: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
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
    color: '#1C1C1E',
    marginTop: 8,
  },
});

export default HomeScreen;