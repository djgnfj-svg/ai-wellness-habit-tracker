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
import AsyncStorage from '@react-native-async-storage/async-storage';

const LifestylePatternScreen = () => {
  const navigation = useNavigation();
  const [wakeUpTime, setWakeUpTime] = useState('08:00');
  const [sleepTime, setSleepTime] = useState('23:00');
  const [exerciseTime, setExerciseTime] = useState('');
  const [weekendPattern, setWeekendPattern] = useState('');

  const timeSlots = [
    '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', 
    '09:00', '09:30', '10:00', '10:30', '11:00', '11:30'
  ];

  const sleepTimeSlots = [
    '21:00', '21:30', '22:00', '22:30', '23:00', '23:30',
    '24:00', '00:30', '01:00', '01:30', '02:00'
  ];

  const exerciseTimeOptions = [
    { id: 'morning', label: '아침 (06-09시)', emoji: '🌅' },
    { id: 'lunch', label: '점심 (12-14시)', emoji: '☀️' },
    { id: 'evening', label: '저녁 (18-21시)', emoji: '🌆' }
  ];

  const weekendOptions = [
    { id: 'same', label: '평일과 동일', description: '규칙적인 생활' },
    { id: 'different', label: '조금 다름', description: '여유로운 휴식' }
  ];

  const handleComplete = async () => {
    if (!exerciseTime) {
      Alert.alert('알림', '운동 선호 시간을 선택해주세요.');
      return;
    }
    if (!weekendPattern) {
      Alert.alert('알림', '주말 패턴을 선택해주세요.');
      return;
    }

    try {
      // TODO: 생활 패턴 정보 저장
      const lifestyleData = {
        wakeUpTime,
        sleepTime,
        exerciseTime,
        weekendPattern,
      };
      
      await AsyncStorage.setItem('lifestyleData', JSON.stringify(lifestyleData));
      
      // 온보딩 완료, 메인 앱으로 이동
      navigation.navigate('Main' as never);
    } catch (error) {
      console.error('생활 패턴 저장 오류:', error);
      Alert.alert('오류', '설정 저장 중 문제가 발생했습니다.');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>언제 활동하실 건가요?</Text>
          <Text style={styles.subtitle}>맞춤 알림을 위해 알려주세요</Text>
        </View>

        {/* Form */}
        <View style={styles.form}>
          {/* Wake Up Time */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>⏰ 기상 시간</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.timeScrollView}>
              <View style={styles.timeContainer}>
                {timeSlots.map((time) => (
                  <TouchableOpacity
                    key={time}
                    style={[
                      styles.timeButton,
                      wakeUpTime === time && styles.selectedTimeButton
                    ]}
                    onPress={() => setWakeUpTime(time)}
                  >
                    <Text style={[
                      styles.timeText,
                      wakeUpTime === time && styles.selectedTimeText
                    ]}>
                      {time}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>
          </View>

          {/* Sleep Time */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🌙 취침 시간</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.timeScrollView}>
              <View style={styles.timeContainer}>
                {sleepTimeSlots.map((time) => (
                  <TouchableOpacity
                    key={time}
                    style={[
                      styles.timeButton,
                      sleepTime === time && styles.selectedTimeButton
                    ]}
                    onPress={() => setSleepTime(time)}
                  >
                    <Text style={[
                      styles.timeText,
                      sleepTime === time && styles.selectedTimeText
                    ]}>
                      {time}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>
          </View>

          {/* Exercise Time Preference */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>운동 선호 시간</Text>
            <View style={styles.optionsContainer}>
              {exerciseTimeOptions.map((option) => (
                <TouchableOpacity
                  key={option.id}
                  style={[
                    styles.optionCard,
                    exerciseTime === option.id && styles.selectedOptionCard
                  ]}
                  onPress={() => setExerciseTime(option.id)}
                >
                  <Text style={styles.optionEmoji}>{option.emoji}</Text>
                  <Text style={[
                    styles.optionLabel,
                    exerciseTime === option.id && styles.selectedOptionLabel
                  ]}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Weekend Pattern */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>주말 패턴</Text>
            <View style={styles.weekendContainer}>
              {weekendOptions.map((option) => (
                <TouchableOpacity
                  key={option.id}
                  style={[
                    styles.weekendOption,
                    weekendPattern === option.id && styles.selectedWeekendOption
                  ]}
                  onPress={() => setWeekendPattern(option.id)}
                >
                  <View style={styles.weekendOptionContent}>
                    <View style={[
                      styles.radioButton,
                      weekendPattern === option.id && styles.selectedRadioButton
                    ]}>
                      {weekendPattern === option.id && (
                        <View style={styles.radioButtonInner} />
                      )}
                    </View>
                    <View style={styles.weekendOptionText}>
                      <Text style={[
                        styles.weekendOptionLabel,
                        weekendPattern === option.id && styles.selectedWeekendOptionLabel
                      ]}>
                        {option.label}
                      </Text>
                      <Text style={styles.weekendOptionDescription}>
                        {option.description}
                      </Text>
                    </View>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        {/* Complete Button */}
        <TouchableOpacity
          style={[
            styles.completeButton,
            (!exerciseTime || !weekendPattern) && styles.disabledButton
          ]}
          onPress={handleComplete}
          disabled={!exerciseTime || !weekendPattern}
          activeOpacity={0.8}
        >
          <Text style={[
            styles.completeButtonText,
            (!exerciseTime || !weekendPattern) && styles.disabledButtonText
          ]}>
            완료
          </Text>
        </TouchableOpacity>

        {/* Progress Indicator */}
        <View style={styles.progressContainer}>
          <View style={styles.progressDotInactive} />
          <View style={styles.progressDotInactive} />
          <View style={styles.progressDot} />
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
  form: {
    marginBottom: 40,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  timeScrollView: {
    marginHorizontal: -20,
    paddingHorizontal: 20,
  },
  timeContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  timeButton: {
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  selectedTimeButton: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
  },
  timeText: {
    fontSize: 16,
    color: '#1C1C1E',
    fontWeight: '500',
  },
  selectedTimeText: {
    color: 'white',
  },
  optionsContainer: {
    gap: 12,
  },
  optionCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    flexDirection: 'row',
    alignItems: 'center',
  },
  selectedOptionCard: {
    backgroundColor: '#F0FDF4',
    borderColor: '#34C759',
  },
  optionEmoji: {
    fontSize: 20,
    marginRight: 12,
  },
  optionLabel: {
    fontSize: 16,
    color: '#1C1C1E',
    fontWeight: '500',
  },
  selectedOptionLabel: {
    color: '#34C759',
  },
  weekendContainer: {
    gap: 12,
  },
  weekendOption: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  selectedWeekendOption: {
    backgroundColor: '#F0FDF4',
    borderColor: '#34C759',
  },
  weekendOptionContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#C7C7CC',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  selectedRadioButton: {
    borderColor: '#34C759',
  },
  radioButtonInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
  },
  weekendOptionText: {
    flex: 1,
  },
  weekendOptionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  selectedWeekendOptionLabel: {
    color: '#34C759',
  },
  weekendOptionDescription: {
    fontSize: 14,
    color: '#8E8E93',
  },
  completeButton: {
    backgroundColor: '#34C759',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 30,
  },
  disabledButton: {
    backgroundColor: '#C7C7CC',
  },
  completeButtonText: {
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

export default LifestylePatternScreen;