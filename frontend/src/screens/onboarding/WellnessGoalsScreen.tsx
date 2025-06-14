import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';

interface WellnessGoal {
  id: string;
  title: string;
  emoji: string;
  description: string;
}

const wellnessGoals: WellnessGoal[] = [
  {
    id: 'weight_management',
    title: '체중 관리',
    emoji: '💪',
    description: '건강한 다이어트와 체중 유지'
  },
  {
    id: 'stress_relief',
    title: '스트레스 해소',
    emoji: '🧘‍♀️',
    description: '마음의 평온과 휴식'
  },
  {
    id: 'sleep_improvement',
    title: '수면 개선',
    emoji: '😴',
    description: '깊고 편안한 잠'
  },
  {
    id: 'healthy_diet',
    title: '건강한 식습관',
    emoji: '🥗',
    description: '영양 균형 잡힌 식단'
  },
  {
    id: 'exercise_habit',
    title: '운동 습관',
    emoji: '💃',
    description: '규칙적인 신체 활동'
  },
  {
    id: 'mental_health',
    title: '정신 건강',
    emoji: '🧠',
    description: '긍정적인 마인드셋'
  }
];

const WellnessGoalsScreen = () => {
  const navigation = useNavigation();
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const toggleGoal = (goalId: string) => {
    setSelectedGoals(prev => 
      prev.includes(goalId)
        ? prev.filter(id => id !== goalId)
        : [...prev, goalId]
    );
  };

  const handleNext = () => {
    if (selectedGoals.length === 0) {
      Alert.alert('알림', '최소 하나의 목표를 선택해주세요.');
      return;
    }

    // TODO: 웰니스 목표 저장
    navigation.navigate('LifestylePattern' as never);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>어떤 변화를 원하세요?</Text>
          <Text style={styles.subtitle}>복수 선택 가능해요</Text>
        </View>

        {/* Goals Grid */}
        <View style={styles.goalsContainer}>
          {wellnessGoals.map((goal) => (
            <TouchableOpacity
              key={goal.id}
              style={[
                styles.goalCard,
                selectedGoals.includes(goal.id) && styles.selectedCard
              ]}
              onPress={() => toggleGoal(goal.id)}
              activeOpacity={0.7}
            >
              <View style={styles.goalEmoji}>
                <Text style={styles.emojiText}>{goal.emoji}</Text>
              </View>
              <Text style={[
                styles.goalTitle,
                selectedGoals.includes(goal.id) && styles.selectedTitle
              ]}>
                {goal.title}
              </Text>
              <Text style={[
                styles.goalDescription,
                selectedGoals.includes(goal.id) && styles.selectedDescription
              ]}>
                {goal.description}
              </Text>
              
              {/* Selection Indicator */}
              {selectedGoals.includes(goal.id) && (
                <View style={styles.selectionBadge}>
                  <Text style={styles.checkmark}>✓</Text>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>

        {/* Selected Count */}
        {selectedGoals.length > 0 && (
          <View style={styles.selectionInfo}>
            <Text style={styles.selectionText}>
              {selectedGoals.length}개 목표 선택됨
            </Text>
          </View>
        )}

        {/* Next Button */}
        <TouchableOpacity
          style={[
            styles.nextButton,
            selectedGoals.length === 0 && styles.disabledButton
          ]}
          onPress={handleNext}
          disabled={selectedGoals.length === 0}
          activeOpacity={0.8}
        >
          <Text style={[
            styles.nextButtonText,
            selectedGoals.length === 0 && styles.disabledButtonText
          ]}>
            다음
          </Text>
        </TouchableOpacity>

        {/* Progress Indicator */}
        <View style={styles.progressContainer}>
          <View style={styles.progressDotInactive} />
          <View style={styles.progressDot} />
          <View style={styles.progressDotInactive} />
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
  content: {
    padding: 20,
    paddingTop: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1C1C1E',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
  goalsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  goalCard: {
    width: '48%',
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  selectedCard: {
    borderColor: '#34C759',
    backgroundColor: '#F0FDF4',
  },
  goalEmoji: {
    marginBottom: 12,
  },
  emojiText: {
    fontSize: 32,
  },
  goalTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    textAlign: 'center',
    marginBottom: 8,
  },
  selectedTitle: {
    color: '#34C759',
  },
  goalDescription: {
    fontSize: 14,
    color: '#8E8E93',
    textAlign: 'center',
    lineHeight: 18,
  },
  selectedDescription: {
    color: '#22C55E',
  },
  selectionBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#34C759',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmark: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  selectionInfo: {
    alignItems: 'center',
    marginBottom: 24,
  },
  selectionText: {
    fontSize: 16,
    color: '#34C759',
    fontWeight: '600',
  },
  nextButton: {
    backgroundColor: '#34C759',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 30,
  },
  disabledButton: {
    backgroundColor: '#C7C7CC',
  },
  nextButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
  disabledButtonText: {
    color: '#8E8E93',
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  progressDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
  },
  progressDotInactive: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#C7C7CC',
  },
});

export default WellnessGoalsScreen;