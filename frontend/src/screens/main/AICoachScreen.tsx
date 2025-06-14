import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  TextInput,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';

interface ChatMessage {
  id: string;
  type: 'ai' | 'user';
  message: string;
  timestamp: Date;
  isTyping?: boolean;
}

interface CoachingCard {
  id: string;
  type: 'motivation' | 'reminder' | 'insight' | 'celebration';
  title: string;
  message: string;
  emoji: string;
  action?: string;
}

const AICoachScreen = () => {
  const navigation = useNavigation();
  const scrollViewRef = useRef<ScrollView>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      message: '안녕하세요, 현아님! 오늘 하루는 어떠셨나요? 물 6잔이나 마시셨네요, 정말 대단해요! 💧',
      timestamp: new Date(Date.now() - 10 * 60 * 1000),
    },
    {
      id: '2',
      type: 'ai', 
      message: '점심시간이 다가오고 있어요. 15분 정도 산책하시면 오후 업무에 더 집중할 수 있을 거예요. 어떠세요?',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
    },
  ]);

  const [coachingCards] = useState<CoachingCard[]>([
    {
      id: '1',
      type: 'motivation',
      title: '오늘의 동기부여',
      message: '벌써 7일 연속 습관을 지키고 계시네요! 꾸준함이 가장 큰 힘이에요.',
      emoji: '🔥',
      action: '더 알아보기',
    },
    {
      id: '2',
      type: 'reminder',
      title: '스트레칭 알림',
      message: '2시간 동안 앉아계셨어요. 목과 어깨를 위해 간단한 스트레칭은 어떨까요?',
      emoji: '🤸‍♀️',
      action: '스트레칭 시작',
    },
    {
      id: '3',
      type: 'insight',
      title: '주간 인사이트',
      message: '이번 주 명상을 한 날에 스트레스 지수가 평균 30% 낮았어요!',
      emoji: '📊',
      action: '상세 보기',
    },
  ]);

  const getCoachingCardStyle = (type: string) => {
    switch (type) {
      case 'motivation':
        return { backgroundColor: '#FFF8DC', borderColor: '#FFD700' };
      case 'reminder':
        return { backgroundColor: '#E3F2FD', borderColor: '#2196F3' };
      case 'insight':
        return { backgroundColor: '#F3E5F5', borderColor: '#9C27B0' };
      case 'celebration':
        return { backgroundColor: '#E8F5E8', borderColor: '#4CAF50' };
      default:
        return { backgroundColor: '#F5F5F5', borderColor: '#CCCCCC' };
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      message: inputMessage.trim(),
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // 메시지 전송 후 스크롤
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);

    // 임시 AI 응답 (실제로는 백엔드 API 호출)
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        message: generateAIResponse(inputMessage),
        timestamp: new Date(),
      };
      
      setChatMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
      
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }, 1500);
  };

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('피곤') || input.includes('힘들')) {
      return '많이 피곤하시군요. 깊게 숨을 들이마시고 천천히 내쉬어 보세요. 5분만 휴식을 취하시는 것도 좋겠어요. 💙';
    }
    
    if (input.includes('스트레스') || input.includes('답답')) {
      return '스트레스 받으실 때는 창밖을 보거나 간단한 목 돌리기를 해보세요. 현아님만의 마음 진정법이 있으신가요?';
    }
    
    if (input.includes('운동') || input.includes('스트레칭')) {
      return '좋은 생각이에요! 지금 날씨가 좋으니 실내 운동보다는 10분 정도 바깥 공기를 마시며 걷는 건 어떨까요? 🚶‍♀️';
    }
    
    if (input.includes('물') || input.includes('수분')) {
      return '물 마시기를 신경쓰고 계시는군요! 목표까지 조금 더 화이팅이에요. 레몬을 한 조각 넣으면 더 맛있게 드실 수 있어요! 🍋';
    }
    
    return '말씀해주셔서 감사해요! 현아님의 건강한 일상을 위해 항상 응원하고 있어요. 더 궁금한 것이 있으시면 언제든 물어보세요! 😊';
  };

  const handleCoachingCardPress = (card: CoachingCard) => {
    switch (card.type) {
      case 'motivation':
        Alert.alert('동기부여', '꾸준함이 습관을 만들고, 습관이 인생을 바꿉니다. 현아님의 노력이 정말 멋져요!');
        break;
      case 'reminder':
        Alert.alert('스트레칭', '어깨를 뒤로 돌리고, 목을 좌우로 천천히 돌려보세요. 3분이면 충분해요!');
        break;
      case 'insight':
        navigation.navigate('Stats' as never);
        break;
      default:
        break;
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false,
    });
  };

  useEffect(() => {
    // 화면 로드 시 맨 아래로 스크롤
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: false });
    }, 100);
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Ionicons name="chevron-back" size={24} color="#1C1C1E" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>AI 코치</Text>
        <View style={styles.headerRight}>
          <View style={styles.onlineIndicator} />
          <Text style={styles.onlineText}>온라인</Text>
        </View>
      </View>

      <KeyboardAvoidingView 
        style={styles.content}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          ref={scrollViewRef}
          style={styles.scrollContainer}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {/* Coaching Cards */}
          <View style={styles.coachingCardsContainer}>
            <Text style={styles.sectionTitle}>오늘의 코칭 카드</Text>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.cardsContent}
            >
              {coachingCards.map((card) => (
                <TouchableOpacity
                  key={card.id}
                  style={[
                    styles.coachingCard,
                    getCoachingCardStyle(card.type),
                  ]}
                  onPress={() => handleCoachingCardPress(card)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.cardEmoji}>{card.emoji}</Text>
                  <Text style={styles.cardTitle}>{card.title}</Text>
                  <Text style={styles.cardMessage}>{card.message}</Text>
                  {card.action && (
                    <Text style={styles.cardAction}>{card.action} →</Text>
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          {/* Chat Messages */}
          <View style={styles.chatContainer}>
            <Text style={styles.sectionTitle}>실시간 대화</Text>
            <View style={styles.messagesContainer}>
              {chatMessages.map((message) => (
                <View key={message.id} style={styles.messageWrapper}>
                  {message.type === 'ai' ? (
                    <View style={styles.aiMessageContainer}>
                      <View style={styles.aiAvatar}>
                        <Text style={styles.aiAvatarText}>🤖</Text>
                      </View>
                      <View style={styles.messageContent}>
                        <View style={styles.aiMessageBubble}>
                          <Text style={styles.aiMessageText}>{message.message}</Text>
                        </View>
                        <Text style={styles.messageTime}>{formatTime(message.timestamp)}</Text>
                      </View>
                    </View>
                  ) : (
                    <View style={styles.userMessageContainer}>
                      <View style={styles.messageContent}>
                        <View style={styles.userMessageBubble}>
                          <Text style={styles.userMessageText}>{message.message}</Text>
                        </View>
                        <Text style={styles.messageTime}>{formatTime(message.timestamp)}</Text>
                      </View>
                    </View>
                  )}
                </View>
              ))}
              
              {isTyping && (
                <View style={styles.messageWrapper}>
                  <View style={styles.aiMessageContainer}>
                    <View style={styles.aiAvatar}>
                      <Text style={styles.aiAvatarText}>🤖</Text>
                    </View>
                    <View style={styles.messageContent}>
                      <View style={styles.typingBubble}>
                        <Text style={styles.typingText}>답변을 준비 중입니다...</Text>
                      </View>
                    </View>
                  </View>
                </View>
              )}
            </View>
          </View>
        </ScrollView>

        {/* Input Area */}
        <View style={styles.inputContainer}>
          <View style={styles.inputWrapper}>
            <TextInput
              style={styles.textInput}
              value={inputMessage}
              onChangeText={setInputMessage}
              placeholder="궁금한 것을 물어보세요..."
              placeholderTextColor="#8E8E93"
              multiline
              maxLength={500}
            />
            <TouchableOpacity
              style={[
                styles.sendButton,
                inputMessage.trim() ? styles.sendButtonActive : styles.sendButtonInactive
              ]}
              onPress={sendMessage}
              disabled={!inputMessage.trim() || isTyping}
            >
              <Ionicons 
                name="send" 
                size={20} 
                color={inputMessage.trim() ? 'white' : '#8E8E93'} 
              />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
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
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1C1C1E',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    width: 40,
    justifyContent: 'flex-end',
  },
  onlineIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
    marginRight: 4,
  },
  onlineText: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '500',
  },
  content: {
    flex: 1,
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  coachingCardsContainer: {
    paddingTop: 20,
    paddingBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginHorizontal: 20,
    marginBottom: 16,
  },
  cardsContent: {
    paddingHorizontal: 20,
    gap: 12,
  },
  coachingCard: {
    width: 200,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginRight: 12,
  },
  cardEmoji: {
    fontSize: 24,
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  cardMessage: {
    fontSize: 14,
    color: '#1C1C1E',
    lineHeight: 20,
    marginBottom: 12,
  },
  cardAction: {
    fontSize: 14,
    fontWeight: '600',
    color: '#007AFF',
  },
  chatContainer: {
    flex: 1,
    paddingBottom: 20,
  },
  messagesContainer: {
    paddingHorizontal: 20,
  },
  messageWrapper: {
    marginBottom: 16,
  },
  aiMessageContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  userMessageContainer: {
    flexDirection: 'row-reverse',
    alignItems: 'flex-start',
  },
  aiAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  aiAvatarText: {
    fontSize: 16,
  },
  messageContent: {
    flex: 1,
    maxWidth: '80%',
  },
  aiMessageBubble: {
    backgroundColor: 'white',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userMessageBubble: {
    backgroundColor: '#34C759',
    borderRadius: 18,
    borderBottomRightRadius: 4,
    padding: 12,
    alignSelf: 'flex-end',
  },
  aiMessageText: {
    fontSize: 16,
    color: '#1C1C1E',
    lineHeight: 22,
  },
  userMessageText: {
    fontSize: 16,
    color: 'white',
    lineHeight: 22,
  },
  typingBubble: {
    backgroundColor: '#F2F2F7',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    padding: 12,
  },
  typingText: {
    fontSize: 16,
    color: '#8E8E93',
    fontStyle: 'italic',
  },
  messageTime: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 4,
    marginHorizontal: 12,
  },
  inputContainer: {
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#F2F2F7',
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#F2F2F7',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    minHeight: 40,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: '#1C1C1E',
    maxHeight: 100,
    paddingVertical: 4,
  },
  sendButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  sendButtonActive: {
    backgroundColor: '#34C759',
  },
  sendButtonInactive: {
    backgroundColor: 'transparent',
  },
});

export default AICoachScreen;