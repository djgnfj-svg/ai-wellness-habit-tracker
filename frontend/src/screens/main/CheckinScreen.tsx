import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  TextInput,
  Alert,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Habit {
  id: string;
  name: string;
  emoji: string;
  isCompleted: boolean;
}

interface Mood {
  id: number;
  emoji: string;
  label: string;
}

const CheckinScreen = () => {
  const [selectedHabit, setSelectedHabit] = useState<Habit | null>(null);
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);
  const [animationValue] = useState(new Animated.Value(0));

  const todayHabits: Habit[] = [
    { id: '1', name: '물 8잔 마시기', emoji: '💧', isCompleted: false },
    { id: '2', name: '점심 산책 15분', emoji: '🚶‍♀️', isCompleted: false },
    { id: '3', name: '스트레칭 10분', emoji: '🤸‍♀️', isCompleted: false },
    { id: '4', name: '명상 5분', emoji: '🧘‍♀️', isCompleted: true },
    { id: '5', name: '일기 쓰기', emoji: '📝', isCompleted: false },
  ];

  const moods: Mood[] = [
    { id: 1, emoji: '😢', label: '안좋음' },
    { id: 2, emoji: '😐', label: '보통' },
    { id: 3, emoji: '😊', label: '좋음' },
    { id: 4, emoji: '😍', label: '매우좋음' },
    { id: 5, emoji: '🤩', label: '최고' },
  ];

  const handleHabitSelect = (habit: Habit) => {
    if (!habit.isCompleted) {
      setSelectedHabit(habit);
      setIsCompleted(false);
      setShowCelebration(false);
    }
  };

  const handleCheckin = () => {
    if (!selectedHabit) {
      Alert.alert('알림', '체크인할 습관을 선택해주세요.');
      return;
    }

    if (selectedHabit.isCompleted) {
      Alert.alert('알림', '이미 완료된 습관입니다.');
      return;
    }

    // 체크인 애니메이션
    Animated.sequence([
      Animated.timing(animationValue, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(animationValue, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start();

    setIsCompleted(true);
    
    // 축하 화면 표시
    setTimeout(() => {
      setShowCelebration(true);
    }, 500);
  };

  const handleSave = () => {
    if (!selectedMood) {
      Alert.alert('알림', '오늘 기분을 선택해주세요.');
      return;
    }

    // TODO: 서버에 체크인 데이터 저장
    Alert.alert(
      '체크인 완료! 🎉',
      `${selectedHabit?.name}을(를) 완료했습니다!\n+50 포인트 획득 ⭐`,
      [
        {
          text: '확인',
          onPress: () => {
            // 초기화
            setSelectedHabit(null);
            setSelectedMood(null);
            setNotes('');
            setIsCompleted(false);
            setShowCelebration(false);
          },
        },
      ]
    );
  };

  const animatedScale = animationValue.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 1.2],
  });

  if (showCelebration && selectedHabit) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.celebrationContainer}>
          <Text style={styles.celebrationEmoji}>🎉</Text>
          <Text style={styles.celebrationTitle}>잘하셨어요!</Text>
          <Text style={styles.celebrationHabit}>{selectedHabit.name}</Text>
          <Text style={styles.celebrationMessage}>🔥 8일 연속 달성!</Text>
          <Text style={styles.celebrationPoints}>+50 포인트 획득 ⭐</Text>
          <Text style={styles.celebrationSubtext}>
            내일도 이 시간에 알려드릴게요!
          </Text>
          
          <View style={styles.celebrationButtons}>
            <TouchableOpacity
              style={styles.celebrationConfirmButton}
              onPress={handleSave}
            >
              <Text style={styles.celebrationConfirmText}>확인</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.celebrationShareButton}>
              <Ionicons name="share-outline" size={20} color="#34C759" />
              <Text style={styles.celebrationShareText}>공유하기</Text>
            </TouchableOpacity>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>습관 체크인</Text>
        <Text style={styles.headerSubtitle}>오늘 완료한 습관을 체크해보세요</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Habit Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>체크인할 습관 선택</Text>
          <View style={styles.habitsList}>
            {todayHabits.map((habit) => (
              <TouchableOpacity
                key={habit.id}
                style={[
                  styles.habitItem,
                  selectedHabit?.id === habit.id && styles.selectedHabitItem,
                  habit.isCompleted && styles.completedHabitItem,
                ]}
                onPress={() => handleHabitSelect(habit)}
                disabled={habit.isCompleted}
                activeOpacity={0.7}
              >
                <View style={styles.habitContent}>
                  <Text style={styles.habitEmoji}>{habit.emoji}</Text>
                  <Text style={[
                    styles.habitName,
                    habit.isCompleted && styles.completedHabitName
                  ]}>
                    {habit.name}
                  </Text>
                  {habit.isCompleted && (
                    <View style={styles.completedBadge}>
                      <Ionicons name="checkmark" size={16} color="white" />
                    </View>
                  )}
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {selectedHabit && (
          <>
            {/* Check-in Button */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>
                {selectedHabit.name}
              </Text>
              <View style={styles.checkinButtonContainer}>
                <Animated.View style={{ transform: [{ scale: animatedScale }] }}>
                  <TouchableOpacity
                    style={[
                      styles.checkinButton,
                      isCompleted && styles.completedCheckinButton,
                    ]}
                    onPress={handleCheckin}
                    disabled={isCompleted}
                    activeOpacity={0.8}
                  >
                    {isCompleted ? (
                      <Ionicons name="checkmark" size={60} color="white" />
                    ) : (
                      <Text style={styles.checkinButtonText}>✓</Text>
                    )}
                  </TouchableOpacity>
                </Animated.View>
                <Text style={styles.checkinButtonLabel}>
                  {isCompleted ? '완료!' : '체크인'}
                </Text>
              </View>
            </View>

            {/* Mood Selection */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>오늘 기분은 어떠셨나요?</Text>
              <View style={styles.moodContainer}>
                {moods.map((mood) => (
                  <TouchableOpacity
                    key={mood.id}
                    style={[
                      styles.moodButton,
                      selectedMood === mood.id && styles.selectedMoodButton,
                    ]}
                    onPress={() => setSelectedMood(mood.id)}
                  >
                    <Text style={styles.moodEmoji}>{mood.emoji}</Text>
                    <Text style={styles.moodLabel}>{mood.label}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Notes */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>메모 (선택사항)</Text>
              <TextInput
                style={styles.notesInput}
                value={notes}
                onChangeText={setNotes}
                placeholder="오늘의 느낌이나 특별한 점을 적어보세요"
                placeholderTextColor="#8E8E93"
                multiline
                numberOfLines={4}
                maxLength={200}
              />
              <Text style={styles.characterCount}>{notes.length}/200</Text>
            </View>

            {/* Photo Upload */}
            <View style={styles.section}>
              <TouchableOpacity style={styles.photoUploadButton}>
                <Ionicons name="camera-outline" size={24} color="#34C759" />
                <Text style={styles.photoUploadText}>📸 인증샷 추가하기</Text>
              </TouchableOpacity>
            </View>

            {/* Save Button */}
            {isCompleted && (
              <TouchableOpacity
                style={[
                  styles.saveButton,
                  !selectedMood && styles.disabledSaveButton,
                ]}
                onPress={handleSave}
                disabled={!selectedMood}
              >
                <Text style={[
                  styles.saveButtonText,
                  !selectedMood && styles.disabledSaveButtonText,
                ]}>
                  저장하기
                </Text>
              </TouchableOpacity>
            )}
          </>
        )}

        {!selectedHabit && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateEmoji}>🎯</Text>
            <Text style={styles.emptyStateTitle}>체크인할 습관을 선택해주세요</Text>
            <Text style={styles.emptyStateDescription}>
              위에서 오늘 완료한 습관을 선택해보세요
            </Text>
          </View>
        )}
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
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#8E8E93',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  habitsList: {
    gap: 12,
  },
  habitItem: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedHabitItem: {
    borderColor: '#34C759',
    backgroundColor: '#F0FDF4',
  },
  completedHabitItem: {
    backgroundColor: '#F8F9FA',
    opacity: 0.6,
  },
  habitContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  habitEmoji: {
    fontSize: 20,
    marginRight: 12,
  },
  habitName: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
  },
  completedHabitName: {
    textDecorationLine: 'line-through',
    color: '#8E8E93',
  },
  completedBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#34C759',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkinButtonContainer: {
    alignItems: 'center',
    gap: 16,
  },
  checkinButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#34C759',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
  },
  completedCheckinButton: {
    backgroundColor: '#22C55E',
  },
  checkinButtonText: {
    fontSize: 60,
    color: 'white',
    fontWeight: 'bold',
  },
  checkinButtonLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  moodContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  moodButton: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedMoodButton: {
    borderColor: '#34C759',
    backgroundColor: '#F0FDF4',
  },
  moodEmoji: {
    fontSize: 24,
    marginBottom: 8,
  },
  moodLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#1C1C1E',
  },
  notesInput: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#1C1C1E',
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  characterCount: {
    fontSize: 12,
    color: '#8E8E93',
    textAlign: 'right',
    marginTop: 8,
  },
  photoUploadButton: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    borderWidth: 2,
    borderColor: '#34C759',
    borderStyle: 'dashed',
  },
  photoUploadText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#34C759',
  },
  saveButton: {
    backgroundColor: '#34C759',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginTop: 20,
  },
  disabledSaveButton: {
    backgroundColor: '#C7C7CC',
  },
  saveButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
  disabledSaveButtonText: {
    color: '#8E8E93',
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyStateEmoji: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  emptyStateDescription: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
  celebrationContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    backgroundColor: 'white',
  },
  celebrationEmoji: {
    fontSize: 80,
    marginBottom: 20,
  },
  celebrationTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1C1C1E',
    marginBottom: 12,
  },
  celebrationHabit: {
    fontSize: 20,
    fontWeight: '600',
    color: '#34C759',
    marginBottom: 20,
  },
  celebrationMessage: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FF6B35',
    marginBottom: 8,
  },
  celebrationPoints: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFD60A',
    marginBottom: 20,
  },
  celebrationSubtext: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    marginBottom: 40,
  },
  celebrationButtons: {
    flexDirection: 'row',
    gap: 16,
  },
  celebrationConfirmButton: {
    backgroundColor: '#34C759',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  celebrationConfirmText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  celebrationShareButton: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#34C759',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  celebrationShareText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#34C759',
  },
});

export default CheckinScreen;