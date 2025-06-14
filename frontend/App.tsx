import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import screens
import WelcomeScreen from './src/screens/onboarding/WelcomeScreen';
import ProblemScreen from './src/screens/onboarding/ProblemScreen';
import LoginScreen from './src/screens/onboarding/LoginScreen';
import ProfileSetupScreen from './src/screens/onboarding/ProfileSetupScreen';
import WellnessGoalsScreen from './src/screens/onboarding/WellnessGoalsScreen';
import LifestylePatternScreen from './src/screens/onboarding/LifestylePatternScreen';

import HomeScreen from './src/screens/main/HomeScreen';
import StatsScreen from './src/screens/main/StatsScreen';
import CheckinScreen from './src/screens/main/CheckinScreen';
import AICoachScreen from './src/screens/main/AICoachScreen';
import ProfileScreen from './src/screens/main/ProfileScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Bottom Tab Navigator
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Stats') {
            iconName = focused ? 'bar-chart' : 'bar-chart-outline';
          } else if (route.name === 'Checkin') {
            iconName = focused ? 'add-circle' : 'add-circle-outline';
          } else if (route.name === 'AICoach') {
            iconName = focused ? 'chatbubble' : 'chatbubble-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'home-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#34C759',
        tabBarInactiveTintColor: '#8E8E93',
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopWidth: 1,
          borderTopColor: '#F2F2F7',
          height: 90,
          paddingBottom: 20,
          paddingTop: 10,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ title: '홈' }}
      />
      <Tab.Screen 
        name="Stats" 
        component={StatsScreen}
        options={{ title: '통계' }}
      />
      <Tab.Screen 
        name="Checkin" 
        component={CheckinScreen}
        options={{ title: '체크인' }}
      />
      <Tab.Screen 
        name="AICoach" 
        component={AICoachScreen}
        options={{ title: 'AI코치' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: '마이' }}
      />
    </Tab.Navigator>
  );
}

// Main App Component
export default function App() {
  const [isFirstLaunch, setIsFirstLaunch] = useState<boolean | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    checkAppLaunchStatus();
  }, []);

  const checkAppLaunchStatus = async () => {
    try {
      const hasLaunched = await AsyncStorage.getItem('hasLaunched');
      const userToken = await AsyncStorage.getItem('userToken');
      
      setIsFirstLaunch(hasLaunched === null);
      setIsLoggedIn(userToken !== null);
    } catch (error) {
      console.error('Error checking app launch status:', error);
      setIsFirstLaunch(true);
      setIsLoggedIn(false);
    }
  };

  // Show loading screen while checking status
  if (isFirstLaunch === null || isLoggedIn === null) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#34C759' }}>
        <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>WellnessAI</Text>
        <Text style={{ color: 'white', fontSize: 16, marginTop: 10 }}>로딩 중...</Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator 
        screenOptions={{ headerShown: false }}
        initialRouteName={isLoggedIn ? "Main" : (isFirstLaunch ? "Welcome" : "Login")}
      >
        {/* Onboarding Flow */}
        <Stack.Screen name="Welcome" component={WelcomeScreen} />
        <Stack.Screen name="Problem" component={ProblemScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="ProfileSetup" component={ProfileSetupScreen} />
        <Stack.Screen name="WellnessGoals" component={WellnessGoalsScreen} />
        <Stack.Screen name="LifestylePattern" component={LifestylePatternScreen} />
        
        {/* Main App */}
        <Stack.Screen name="Main" component={MainTabNavigator} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}