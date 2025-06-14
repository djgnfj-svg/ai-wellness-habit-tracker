import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface HabitStat {
  id: string;
  name: string;
  emoji: string;
  completionRate: number;
  currentStreak: number;
  weeklyData: number[];
}

const StatsScreen = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('week');
  
  const periods = [
    { key: 'week' as const, label: '이번 주' },
    { key: 'month' as const, label: '이번 달' },
    { key: 'year' as const, label: '올해' },
  ];

  const weeklyStats = {
    period: '6월 5일 ~ 6월 11일',
    overallScore: 85,
    scoreChange: 12,
    habits: [
      {
        id: '1',
        name: '물 마시기',
        emoji: '💧',
        completionRate: 90,
        currentStreak: 12,
        weeklyData: [1, 1, 0, 1, 1, 1, 1], // 7일 데이터
      },
      {
        id: '2',
        name: '명상',
        emoji: '🧘‍♀️',
        completionRate: 70,
        currentStreak: 3,
        weeklyData: [0, 1, 1, 0, 1, 1, 1],
      },
      {
        id: '3',
        name: '운동',
        emoji: '💪',
        completionRate: 50,
        currentStreak: 2,
        weeklyData: [1, 0, 0, 1, 0, 1, 1],
      },
      {
        id: '4',
        name: '일기 쓰기',
        emoji: '📝',
        completionRate: 60,
        currentStreak: 1,
        weeklyData: [0, 1, 1, 0, 0, 1, 1],
      },
    ] as HabitStat[],
  };

  const highlights = [
    {
      id: '1',
      title: '최장 스트릭',
      description: '물 마시기 (12일 연속!)',
      emoji: '🏆',
    },
    {
      id: '2',
      title: '가장 발전',
      description: '명상 (전주 30% → 이번주 70%)',
      emoji: '📈',
    },
  ];

  const getDayLabel = (index: number) => {
    const days = ['월', '화', '수', '목', '금', '토', '일'];
    return days[index];
  };

  const renderProgressBar = (rate: number) => {
    const filledBars = Math.round(rate / 10);
    return (
      <View style={styles.progressBarContainer}>
        {Array.from({ length: 10 }).map((_, index) => (
          <View
            key={index}
            style={[
              styles.progressBarSegment,
              index < filledBars && styles.progressBarFilled,
            ]}
          />
        ))}
      </View>
    );
  };

  const renderWeeklyChart = (data: number[], habitName: string) => {
    const maxHeight = 40;
    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>{habitName}</Text>
        <View style={styles.chart}>
          {data.map((value, index) => (
            <View key={index} style={styles.chartDay}>
              <View
                style={[
                  styles.chartBar,
                  {
                    height: value ? maxHeight : 4,
                    backgroundColor: value ? '#34C759' : '#F2F2F7',
                  },
                ]}
              />
              <Text style={styles.chartDayLabel}>{getDayLabel(index)}</Text>
            </View>
          ))}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>이번 주 성과</Text>
        <Text style={styles.headerSubtitle}>{weeklyStats.period}</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Period Selector */}
        <View style={styles.periodSelector}>
          {periods.map((period) => (
            <TouchableOpacity
              key={period.key}
              style={[
                styles.periodButton,
                selectedPeriod === period.key && styles.selectedPeriodButton,
              ]}
              onPress={() => setSelectedPeriod(period.key)}
            >
              <Text
                style={[
                  styles.periodButtonText,
                  selectedPeriod === period.key && styles.selectedPeriodButtonText,
                ]}
              >
                {period.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Overall Score Card */}
        <View style={styles.scoreCard}>
          <Text style={styles.scoreTitle}>종합 점수</Text>
          <View style={styles.scoreContent}>
            <Text style={styles.scoreValue}>{weeklyStats.overallScore}점</Text>
            <Text style={styles.scoreEmoji}>🏆</Text>
          </View>
          <Text style={styles.scoreChange}>
            지난주보다 +{weeklyStats.scoreChange}점!
          </Text>
        </View>

        {/* Habits Performance */}
        <View style={styles.habitsCard}>
          <Text style={styles.habitsTitle}>습관별 달성률</Text>
          <View style={styles.habitsList}>
            {weeklyStats.habits.map((habit) => (
              <View key={habit.id} style={styles.habitStatItem}>
                <View style={styles.habitStatHeader}>
                  <View style={styles.habitStatInfo}>
                    <Text style={styles.habitStatEmoji}>{habit.emoji}</Text>
                    <Text style={styles.habitStatName}>{habit.name}</Text>
                  </View>
                  <Text style={styles.habitStatRate}>{habit.completionRate}%</Text>
                </View>
                {renderProgressBar(habit.completionRate)}
              </View>
            ))}
          </View>
        </View>

        {/* Weekly Charts */}
        <View style={styles.chartsCard}>
          <Text style={styles.chartsTitle}>주간 활동 차트</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.chartsScrollView}
          >
            {weeklyStats.habits.map((habit) => (
              <View key={habit.id} style={styles.chartWrapper}>
                {renderWeeklyChart(habit.weeklyData, habit.name)}
              </View>
            ))}
          </ScrollView>
        </View>

        {/* Weekly Highlights */}
        <View style={styles.highlightsCard}>
          <Text style={styles.highlightsTitle}>이번 주 하이라이트</Text>
          <View style={styles.highlightsList}>
            {highlights.map((highlight) => (
              <View key={highlight.id} style={styles.highlightItem}>
                <Text style={styles.highlightEmoji}>{highlight.emoji}</Text>
                <View style={styles.highlightContent}>
                  <Text style={styles.highlightTitle}>{highlight.title}</Text>
                  <Text style={styles.highlightDescription}>
                    {highlight.description}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="document-text-outline" size={20} color="#007AFF" />
            <Text style={styles.actionButtonText}>월간 보고서</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="people-outline" size={20} color="#34C759" />
            <Text style={styles.actionButtonText}>친구와 비교</Text>
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
  periodSelector: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 4,
    marginBottom: 20,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  selectedPeriodButton: {
    backgroundColor: '#34C759',
  },
  periodButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#8E8E93',
  },
  selectedPeriodButtonText: {
    color: 'white',
  },
  scoreCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 24,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  scoreTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  scoreContent: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#34C759',
    marginRight: 12,
  },
  scoreEmoji: {
    fontSize: 32,
  },
  scoreChange: {
    fontSize: 16,
    color: '#34C759',
    fontWeight: '600',
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
    gap: 16,
  },
  habitStatItem: {
    gap: 8,
  },
  habitStatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  habitStatInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  habitStatEmoji: {
    fontSize: 16,
    marginRight: 8,
  },
  habitStatName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
  },
  habitStatRate: {
    fontSize: 16,
    fontWeight: '600',
    color: '#34C759',
  },
  progressBarContainer: {
    flexDirection: 'row',
    gap: 2,
  },
  progressBarSegment: {
    flex: 1,
    height: 4,
    backgroundColor: '#F2F2F7',
    borderRadius: 2,
  },
  progressBarFilled: {
    backgroundColor: '#34C759',
  },
  chartsCard: {
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
  chartsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  chartsScrollView: {
    marginHorizontal: -20,
    paddingHorizontal: 20,
  },
  chartWrapper: {
    marginRight: 20,
  },
  chartContainer: {
    width: 140,
  },
  chartTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 12,
    textAlign: 'center',
  },
  chart: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 60,
  },
  chartDay: {
    alignItems: 'center',
    gap: 4,
  },
  chartBar: {
    width: 12,
    borderRadius: 2,
  },
  chartDayLabel: {
    fontSize: 12,
    color: '#8E8E93',
  },
  highlightsCard: {
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
  highlightsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  highlightsList: {
    gap: 16,
  },
  highlightItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  highlightEmoji: {
    fontSize: 24,
    marginRight: 12,
  },
  highlightContent: {
    flex: 1,
  },
  highlightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  highlightDescription: {
    fontSize: 14,
    color: '#8E8E93',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  actionButton: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1C1C1E',
  },
});

export default StatsScreen;