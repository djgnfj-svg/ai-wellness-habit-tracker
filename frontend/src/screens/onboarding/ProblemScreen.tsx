import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';

interface Problem {
  id: string;
  title: string;
  description: string;
  emoji: string;
}

const problems: Problem[] = [
  {
    id: 'irregular_lifestyle',
    title: '불규칙한 생활패턴',
    description: '집에서 일하니까 운동할 시간이 애매해',
    emoji: '😵',
  },
  {
    id: 'lack_motivation',
    title: '혼자서는 동기부여 어려움',
    description: '운동하자고 다짐해도 3일도 못 가',
    emoji: '😰',
  },
  {
    id: 'dont_know_method',
    title: '나에게 맞는 방법 모름',
    description: '인터넷에 정보는 많은데 뭐가 나한테 맞는지 모르겠어',
    emoji: '🤷‍♀️',
  },
];

const ProblemScreen = () => {
  const navigation = useNavigation();
  const [selectedProblems, setSelectedProblems] = useState<string[]>([]);

  const toggleProblem = (problemId: string) => {
    setSelectedProblems(prev => 
      prev.includes(problemId)
        ? prev.filter(id => id !== problemId)
        : [...prev, problemId]
    );
  };

  const handleNext = () => {
    navigation.navigate('Login' as never);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>이런 고민 있으신가요?</Text>
        </View>

        {/* Problems List */}
        <View style={styles.problemsContainer}>
          {problems.map((problem) => (
            <TouchableOpacity
              key={problem.id}
              style={[
                styles.problemCard,
                selectedProblems.includes(problem.id) && styles.selectedCard
              ]}
              onPress={() => toggleProblem(problem.id)}
              activeOpacity={0.7}
            >
              <View style={styles.problemHeader}>
                <View style={styles.problemInfo}>
                  <Text style={styles.problemEmoji}>{problem.emoji}</Text>
                  <Text style={styles.problemTitle}>{problem.title}</Text>
                </View>
                <View style={[
                  styles.checkbox,
                  selectedProblems.includes(problem.id) && styles.checkedBox
                ]}>
                  {selectedProblems.includes(problem.id) && (
                    <Ionicons name="checkmark" size={16} color="white" />
                  )}
                </View>
              </View>
              <Text style={styles.problemDescription}>
                "{problem.description}"
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Description */}
        <View style={styles.descriptionContainer}>
          <Text style={styles.description}>
            WellnessAI가 해결해드릴게요!
          </Text>
        </View>

        {/* Next Button */}
        <TouchableOpacity
          style={[
            styles.nextButton,
            selectedProblems.length === 0 && styles.disabledButton
          ]}
          onPress={handleNext}
          disabled={selectedProblems.length === 0}
          activeOpacity={0.8}
        >
          <Text style={[
            styles.nextButtonText,
            selectedProblems.length === 0 && styles.disabledButtonText
          ]}>
            다음
          </Text>
        </TouchableOpacity>
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
    marginBottom: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1C1C1E',
    textAlign: 'center',
  },
  problemsContainer: {
    marginBottom: 40,
  },
  problemCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: 'transparent',
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
  problemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  problemInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  problemEmoji: {
    fontSize: 24,
    marginRight: 12,
  },
  problemTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    flex: 1,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#C7C7CC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkedBox: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
  },
  problemDescription: {
    fontSize: 16,
    color: '#8E8E93',
    fontStyle: 'italic',
    marginLeft: 36,
  },
  descriptionContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  description: {
    fontSize: 18,
    fontWeight: '600',
    color: '#34C759',
    textAlign: 'center',
  },
  nextButton: {
    backgroundColor: '#34C759',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
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
});

export default ProblemScreen;