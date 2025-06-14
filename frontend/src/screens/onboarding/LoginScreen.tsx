import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const LoginScreen = () => {
  const navigation = useNavigation();
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [agreedToPrivacy, setAgreedToPrivacy] = useState(false);

  const handleKakaoLogin = async () => {
    if (!agreedToTerms || !agreedToPrivacy) {
      Alert.alert('알림', '이용약관과 개인정보처리방침에 동의해주세요.');
      return;
    }

    try {
      // TODO: 실제 카카오 로그인 구현
      // 현재는 임시로 토큰 저장
      await AsyncStorage.setItem('userToken', 'temp_kakao_token');
      await AsyncStorage.setItem('hasLaunched', 'true');
      
      // 신규 사용자라면 프로필 설정으로, 기존 사용자라면 메인으로
      navigation.navigate('ProfileSetup' as never);
    } catch (error) {
      console.error('카카오 로그인 오류:', error);
      Alert.alert('오류', '로그인 중 문제가 발생했습니다.');
    }
  };

  const handleNaverLogin = async () => {
    if (!agreedToTerms || !agreedToPrivacy) {
      Alert.alert('알림', '이용약관과 개인정보처리방침에 동의해주세요.');
      return;
    }

    try {
      // TODO: 실제 네이버 로그인 구현
      await AsyncStorage.setItem('userToken', 'temp_naver_token');
      await AsyncStorage.setItem('hasLaunched', 'true');
      navigation.navigate('ProfileSetup' as never);
    } catch (error) {
      console.error('네이버 로그인 오류:', error);
      Alert.alert('오류', '로그인 중 문제가 발생했습니다.');
    }
  };

  const handleGoogleLogin = async () => {
    if (!agreedToTerms || !agreedToPrivacy) {
      Alert.alert('알림', '이용약관과 개인정보처리방침에 동의해주세요.');
      return;
    }

    try {
      // TODO: 실제 구글 로그인 구현
      await AsyncStorage.setItem('userToken', 'temp_google_token');
      await AsyncStorage.setItem('hasLaunched', 'true');
      navigation.navigate('ProfileSetup' as never);
    } catch (error) {
      console.error('구글 로그인 오류:', error);
      Alert.alert('오류', '로그인 중 문제가 발생했습니다.');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>간편 로그인</Text>
        </View>

        {/* Login Buttons */}
        <View style={styles.loginContainer}>
          {/* Kakao Login */}
          <TouchableOpacity
            style={[styles.loginButton, styles.kakaoButton]}
            onPress={handleKakaoLogin}
            activeOpacity={0.8}
          >
            <View style={styles.buttonContent}>
              <View style={styles.logoContainer}>
                <Text style={styles.kakaoLogo}>💬</Text>
              </View>
              <Text style={styles.kakaoButtonText}>카카오 로그인</Text>
              <Text style={styles.buttonSubtext}>🥳 3초만에 시작하기</Text>
            </View>
          </TouchableOpacity>

          {/* Naver Login */}
          <TouchableOpacity
            style={[styles.loginButton, styles.naverButton]}
            onPress={handleNaverLogin}
            activeOpacity={0.8}
          >
            <View style={styles.buttonContent}>
              <View style={styles.logoContainer}>
                <Text style={styles.naverLogo}>N</Text>
              </View>
              <Text style={styles.naverButtonText}>네이버 로그인</Text>
            </View>
          </TouchableOpacity>

          {/* Google Login */}
          <TouchableOpacity
            style={[styles.loginButton, styles.googleButton]}
            onPress={handleGoogleLogin}
            activeOpacity={0.8}
          >
            <View style={styles.buttonContent}>
              <View style={styles.logoContainer}>
                <Text style={styles.googleLogo}>G</Text>
              </View>
              <Text style={styles.googleButtonText}>구글 로그인</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Terms Agreement */}
        <View style={styles.termsContainer}>
          <TouchableOpacity
            style={styles.checkboxContainer}
            onPress={() => setAgreedToTerms(!agreedToTerms)}
          >
            <View style={[styles.checkbox, agreedToTerms && styles.checkedBox]}>
              {agreedToTerms && (
                <Ionicons name="checkmark" size={14} color="white" />
              )}
            </View>
            <Text style={styles.checkboxText}>이용약관 동의</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.checkboxContainer}
            onPress={() => setAgreedToPrivacy(!agreedToPrivacy)}
          >
            <View style={[styles.checkbox, agreedToPrivacy && styles.checkedBox]}>
              {agreedToPrivacy && (
                <Ionicons name="checkmark" size={14} color="white" />
              )}
            </View>
            <Text style={styles.checkboxText}>개인정보처리방침 동의</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1C1C1E',
  },
  loginContainer: {
    marginBottom: 40,
  },
  loginButton: {
    paddingVertical: 18,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  kakaoButton: {
    backgroundColor: '#FEE500',
  },
  naverButton: {
    backgroundColor: '#03C75A',
  },
  googleButton: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#DADCE0',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  logoContainer: {
    position: 'absolute',
    left: 0,
  },
  kakaoLogo: {
    fontSize: 20,
  },
  naverLogo: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  googleLogo: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4285F4',
  },
  kakaoButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#191919',
  },
  naverButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  googleButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  buttonSubtext: {
    fontSize: 14,
    color: '#191919',
    marginLeft: 8,
  },
  termsContainer: {
    alignItems: 'center',
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#C7C7CC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  checkedBox: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
  },
  checkboxText: {
    fontSize: 16,
    color: '#1C1C1E',
  },
});

export default LoginScreen;