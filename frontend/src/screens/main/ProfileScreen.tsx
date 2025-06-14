import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  Switch,
  Modal,
  TextInput,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface UserProfile {
  name: string;
  email: string;
  joinDate: string;
  streakCount: number;
  completedHabits: number;
}

interface SettingsItem {
  id: string;
  title: string;
  subtitle?: string;
  icon: string;
  type: 'switch' | 'navigation' | 'action';
  value?: boolean;
  action?: () => void;
}

const ProfileScreen = () => {
  const navigation = useNavigation();
  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: '현아',
    email: 'hyuna@example.com',
    joinDate: '2024년 6월',
    streakCount: 7,
    completedHabits: 145,
  });

  const [notifications, setNotifications] = useState({
    habitReminder: true,
    aiCoaching: true,
    weeklyReport: true,
    marketing: false,
  });

  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editName, setEditName] = useState(userProfile.name);

  const settingsSections = [
    {
      title: '계정 관리',
      items: [
        {
          id: 'profile',
          title: '프로필 수정',
          subtitle: '이름, 프로필 사진 변경',
          icon: 'person-outline',
          type: 'action' as const,
          action: () => setIsEditModalVisible(true),
        },
        {
          id: 'wellness',
          title: '웰니스 설정',
          subtitle: '목표, 운동 선호도 설정',
          icon: 'fitness-outline',
          type: 'navigation' as const,
          action: () => Alert.alert('준비 중', '웰니스 설정 화면을 준비 중입니다.'),
        },
        {
          id: 'habits',
          title: '습관 관리',
          subtitle: '습관 추가, 수정, 삭제',
          icon: 'list-outline',
          type: 'navigation' as const,
          action: () => navigation.navigate('Checkin' as never),
        },
      ],
    },
    {
      title: '알림 설정',
      items: [
        {
          id: 'habitReminder',
          title: '습관 알림',
          subtitle: '습관 실행 시간 알림',
          icon: 'notifications-outline',
          type: 'switch' as const,
          value: notifications.habitReminder,
        },
        {
          id: 'aiCoaching',
          title: 'AI 코칭 메시지',
          subtitle: '개인화된 동기부여 메시지',
          icon: 'chatbubble-outline',
          type: 'switch' as const,
          value: notifications.aiCoaching,
        },
        {
          id: 'weeklyReport',
          title: '주간 리포트',
          subtitle: '진척도 요약 보고서',
          icon: 'bar-chart-outline',
          type: 'switch' as const,
          value: notifications.weeklyReport,
        },
        {
          id: 'marketing',
          title: '마케팅 정보',
          subtitle: '이벤트, 혜택 정보',
          icon: 'mail-outline',
          type: 'switch' as const,
          value: notifications.marketing,
        },
      ],
    },
    {
      title: '앱 정보',
      items: [
        {
          id: 'version',
          title: '버전 정보',
          subtitle: 'v1.0.0',
          icon: 'information-circle-outline',
          type: 'navigation' as const,
          action: () => Alert.alert('버전 정보', 'WellnessAI v1.0.0\n최신 버전입니다.'),
        },
        {
          id: 'terms',
          title: '이용약관',
          icon: 'document-text-outline',
          type: 'navigation' as const,
          action: () => Alert.alert('준비 중', '이용약관 화면을 준비 중입니다.'),
        },
        {
          id: 'privacy',
          title: '개인정보처리방침',
          icon: 'shield-outline',
          type: 'navigation' as const,
          action: () => Alert.alert('준비 중', '개인정보처리방침 화면을 준비 중입니다.'),
        },
        {
          id: 'support',
          title: '고객지원',
          subtitle: '문의하기, FAQ',
          icon: 'help-circle-outline',
          type: 'navigation' as const,
          action: () => Alert.alert('고객지원', '이메일: support@wellnessai.com\n운영시간: 평일 9-18시'),
        },
      ],
    },
    {
      title: '계정',
      items: [
        {
          id: 'logout',
          title: '로그아웃',
          icon: 'log-out-outline',
          type: 'action' as const,
          action: handleLogout,
        },
        {
          id: 'delete',
          title: '회원탈퇴',
          icon: 'person-remove-outline',
          type: 'action' as const,
          action: handleDeleteAccount,
        },
      ],
    },
  ];

  const handleNotificationToggle = (key: string, value: boolean) => {
    setNotifications(prev => ({
      ...prev,
      [key]: value,
    }));
    
    // TODO: 백엔드 API 호출하여 설정 저장
    console.log(`${key} 알림: ${value ? '켜짐' : '꺼짐'}`);
  };

  const handleEditProfile = () => {
    if (editName.trim().length < 2) {
      Alert.alert('오류', '이름은 2자 이상 입력해주세요.');
      return;
    }

    setUserProfile(prev => ({
      ...prev,
      name: editName.trim(),
    }));
    setIsEditModalVisible(false);
    
    // TODO: 백엔드 API 호출하여 프로필 저장
    Alert.alert('완료', '프로필이 수정되었습니다.');
  };

  async function handleLogout() {
    Alert.alert(
      '로그아웃',
      '정말 로그아웃하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '로그아웃',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('userToken');
              // 로그인 화면으로 이동 (네비게이션 스택 리셋)
              navigation.reset({
                index: 0,
                routes: [{ name: 'Login' as never }],
              } as never);
            } catch (error) {
              console.error('로그아웃 오류:', error);
              Alert.alert('오류', '로그아웃 중 문제가 발생했습니다.');
            }
          },
        },
      ]
    );
  }

  async function handleDeleteAccount() {
    Alert.alert(
      '회원탈퇴',
      '정말 탈퇴하시겠습니까?\n\n모든 데이터가 삭제되며, 복구할 수 없습니다.',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '탈퇴하기',
          style: 'destructive',
          onPress: () => {
            Alert.alert(
              '확인',
              '탈퇴 처리를 위해 고객센터로 연결됩니다.',
              [
                { text: '취소', style: 'cancel' },
                {
                  text: '연결하기',
                  onPress: () => {
                    Alert.alert('고객센터', '이메일: support@wellnessai.com\n평일 9-18시 운영');
                  },
                },
              ]
            );
          },
        },
      ]
    );
  }

  const renderSettingsItem = (item: SettingsItem) => {
    return (
      <TouchableOpacity
        key={item.id}
        style={styles.settingsItem}
        onPress={item.action}
        activeOpacity={item.type === 'switch' ? 1 : 0.7}
        disabled={item.type === 'switch'}
      >
        <View style={styles.settingsItemLeft}>
          <View style={styles.settingsIconContainer}>
            <Ionicons name={item.icon as any} size={20} color="#1C1C1E" />
          </View>
          <View style={styles.settingsTextContainer}>
            <Text style={[
              styles.settingsItemTitle,
              (item.id === 'logout' || item.id === 'delete') && styles.dangerText
            ]}>
              {item.title}
            </Text>
            {item.subtitle && (
              <Text style={styles.settingsItemSubtitle}>{item.subtitle}</Text>
            )}
          </View>
        </View>
        
        {item.type === 'switch' ? (
          <Switch
            value={item.value}
            onValueChange={(value) => handleNotificationToggle(item.id, value)}
            trackColor={{ false: '#F2F2F7', true: '#34C759' }}
            thumbColor={item.value ? 'white' : 'white'}
          />
        ) : (
          <Ionicons name="chevron-forward" size={16} color="#C7C7CC" />
        )}
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>마이페이지</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Profile Card */}
        <View style={styles.profileCard}>
          <View style={styles.profileHeader}>
            <View style={styles.avatarContainer}>
              <Text style={styles.avatarText}>
                {userProfile.name.charAt(0)}
              </Text>
            </View>
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>{userProfile.name}</Text>
              <Text style={styles.profileEmail}>{userProfile.email}</Text>
              <Text style={styles.joinDate}>{userProfile.joinDate} 가입</Text>
            </View>
          </View>
          
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{userProfile.streakCount}</Text>
              <Text style={styles.statLabel}>연속 일수</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{userProfile.completedHabits}</Text>
              <Text style={styles.statLabel}>완료한 습관</Text>
            </View>
          </View>
        </View>

        {/* Settings Sections */}
        {settingsSections.map((section, sectionIndex) => (
          <View key={sectionIndex} style={styles.settingsSection}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <View style={styles.settingsCard}>
              {section.items.map((item, itemIndex) => (
                <View key={item.id}>
                  {renderSettingsItem(item)}
                  {itemIndex < section.items.length - 1 && (
                    <View style={styles.itemDivider} />
                  )}
                </View>
              ))}
            </View>
          </View>
        ))}
      </ScrollView>

      {/* Edit Profile Modal */}
      <Modal
        visible={isEditModalVisible}
        animationType="slide"
        presentationStyle="formSheet"
        onRequestClose={() => setIsEditModalVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity
              onPress={() => setIsEditModalVisible(false)}
              style={styles.modalCancelButton}
            >
              <Text style={styles.modalCancelText}>취소</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>프로필 수정</Text>
            <TouchableOpacity
              onPress={handleEditProfile}
              style={styles.modalSaveButton}
            >
              <Text style={styles.modalSaveText}>저장</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.modalContent}>
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>이름</Text>
              <TextInput
                style={styles.formInput}
                value={editName}
                onChangeText={setEditName}
                placeholder="이름을 입력하세요"
                autoCapitalize="none"
                autoFocus
              />
            </View>
          </View>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  header: {
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
    textAlign: 'center',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  profileCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  avatarContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#34C759',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  avatarText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  profileEmail: {
    fontSize: 16,
    color: '#8E8E93',
    marginBottom: 2,
  },
  joinDate: {
    fontSize: 14,
    color: '#8E8E93',
  },
  statsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#F2F2F7',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#34C759',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#8E8E93',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#F2F2F7',
    marginHorizontal: 20,
  },
  settingsSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 12,
    marginLeft: 4,
  },
  settingsCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
  },
  settingsItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  settingsItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingsIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingsTextContainer: {
    flex: 1,
  },
  settingsItemTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 2,
  },
  settingsItemSubtitle: {
    fontSize: 14,
    color: '#8E8E93',
  },
  dangerText: {
    color: '#FF3B30',
  },
  itemDivider: {
    height: 1,
    backgroundColor: '#F2F2F7',
    marginLeft: 60,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  modalCancelButton: {
    padding: 4,
  },
  modalCancelText: {
    fontSize: 16,
    color: '#007AFF',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  modalSaveButton: {
    padding: 4,
  },
  modalSaveText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
  },
  modalContent: {
    padding: 20,
  },
  formGroup: {
    marginBottom: 20,
  },
  formLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  formInput: {
    backgroundColor: 'white',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1C1C1E',
    borderWidth: 1,
    borderColor: '#F2F2F7',
  },
});

export default ProfileScreen;