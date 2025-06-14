import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  ScrollView,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';

const ProfileSetupScreen = () => {
  const navigation = useNavigation();
  const [nickname, setNickname] = useState('');
  const [ageGroup, setAgeGroup] = useState('');
  const [occupation, setOccupation] = useState('');

  const ageGroups = [
    '20대 초반',
    '20대 후반', 
    '30대 초반',
    '30대 후반',
    '40대 이상'
  ];

  const occupations = [
    '재택근무',
    '사무직',
    '학생',
    '기타'
  ];

  const handleNext = () => {
    if (!nickname.trim()) {
      Alert.alert('알림', '닉네임을 입력해주세요.');
      return;
    }
    if (!ageGroup) {
      Alert.alert('알림', '나이대를 선택해주세요.');
      return;
    }
    if (!occupation) {
      Alert.alert('알림', '직업을 선택해주세요.');
      return;
    }

    // TODO: 프로필 정보 저장
    navigation.navigate('WellnessGoals' as never);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>당신에 대해 알려주세요</Text>
          <Text style={styles.subtitle}>더 나은 코칭을 위해 필요해요</Text>
        </View>

        {/* Form */}
        <View style={styles.form}>
          {/* Nickname Input */}
          <View style={styles.inputSection}>
            <Text style={styles.label}>닉네임</Text>
            <View style={styles.inputContainer}>
              <TextInput
                style={styles.textInput}
                value={nickname}
                onChangeText={setNickname}
                placeholder="어떻게 불러드릴까요?"
                placeholderTextColor="#8E8E93"
                maxLength={20}
              />
              <TouchableOpacity style={styles.editIcon}>
                <Ionicons name="pencil" size={16} color="#8E8E93" />
              </TouchableOpacity>
            </View>
          </View>

          {/* Age Group Selection */}
          <View style={styles.inputSection}>
            <Text style={styles.label}>나이대</Text>
            <View style={styles.optionsContainer}>
              {ageGroups.map((age) => (
                <TouchableOpacity
                  key={age}
                  style={[
                    styles.optionButton,
                    ageGroup === age && styles.selectedOption
                  ]}
                  onPress={() => setAgeGroup(age)}
                >
                  <Text style={[
                    styles.optionText,
                    ageGroup === age && styles.selectedOptionText
                  ]}>
                    {age}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Occupation Selection */}
          <View style={styles.inputSection}>
            <Text style={styles.label}>직업</Text>
            <View style={styles.dropdownContainer}>
              {occupations.map((job) => (
                <TouchableOpacity
                  key={job}
                  style={[
                    styles.dropdownOption,
                    occupation === job && styles.selectedDropdownOption
                  ]}
                  onPress={() => setOccupation(job)}
                >
                  <Text style={[
                    styles.dropdownText,
                    occupation === job && styles.selectedDropdownText
                  ]}>
                    {job}
                  </Text>
                  {occupation === job && (
                    <Ionicons name="checkmark" size={16} color="#34C759" />
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        {/* Next Button */}
        <TouchableOpacity
          style={[
            styles.nextButton,
            (!nickname.trim() || !ageGroup || !occupation) && styles.disabledButton
          ]}
          onPress={handleNext}
          disabled={!nickname.trim() || !ageGroup || !occupation}
          activeOpacity={0.8}
        >
          <Text style={[
            styles.nextButtonText,
            (!nickname.trim() || !ageGroup || !occupation) && styles.disabledButtonText
          ]}>
            다음
          </Text>
        </TouchableOpacity>

        {/* Progress Indicator */}
        <View style={styles.progressContainer}>
          <View style={styles.progressDot} />
          <View style={styles.progressDotInactive} />
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
    marginBottom: 40,
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
  inputSection: {
    marginBottom: 32,
  },
  label: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: '#1C1C1E',
  },
  editIcon: {
    padding: 4,
  },
  optionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  optionButton: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  selectedOption: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
  },
  optionText: {
    fontSize: 16,
    color: '#1C1C1E',
    fontWeight: '500',
  },
  selectedOptionText: {
    color: 'white',
  },
  dropdownContainer: {
    backgroundColor: 'white',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  dropdownOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  selectedDropdownOption: {
    backgroundColor: '#F0FDF4',
  },
  dropdownText: {
    fontSize: 16,
    color: '#1C1C1E',
  },
  selectedDropdownText: {
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

export default ProfileSetupScreen;