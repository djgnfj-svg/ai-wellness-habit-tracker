# 🛠️ WellnessAI 기능 정의서

> **Python/FastAPI 백엔드 기반 상세 기능 명세**

---

## 📋 **기능 개요**

WellnessAI는 **7개 핵심 모듈**로 구성된 AI 기반 웰니스 습관 추적 플랫폼입니다.

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  사용자 관리     │   │   습관 관리      │   │   추적 시스템    │
│ User Management │   │ Habit Management│   │ Tracking System │
└─────────────────┘   └─────────────────┘   └─────────────────┘
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   AI 코칭       │   │  분석/통계      │   │   알림 시스템    │
│  AI Coaching    │   │   Analytics     │   │ Notification    │
└─────────────────┘   └─────────────────┘   └─────────────────┘
┌─────────────────┐
│   결제/구독      │
│  Payment/Sub    │
└─────────────────┘
```

---

## 🔐 **1. 사용자 관리 모듈 (User Management)**

### **1.1 사용자 인증 (Authentication)**

#### **소셜 로그인**
- **카카오 로그인** (OAuth 2.0)
  - 카카오 API 연동
  - 프로필 이미지, 이메일 자동 가져오기
  - 토큰 관리 (Access Token, Refresh Token)
  
- **네이버 로그인** (OAuth 2.0)
  - 네이버 API 연동
  - 백업 로그인 옵션

- **구글 로그인** (OAuth 2.0)
  - 글로벌 확장 대비
  - Google Fit 연동 준비

#### **JWT 토큰 시스템**
- **Access Token**: 1시간 만료
- **Refresh Token**: 30일 만료
- 자동 토큰 갱신 로직
- 디바이스별 토큰 관리

#### **보안 기능**
- 비밀번호 해싱 (bcrypt)
- Rate Limiting (IP별 요청 제한)
- 디바이스 등록/해제
- 로그인 히스토리 추적

### **1.2 사용자 프로필 (User Profile)**

#### **기본 정보**
```python
class UserProfile:
    user_id: UUID
    nickname: str
    email: str
    profile_image_url: Optional[str]
    birth_year: Optional[int]
    gender: Optional[Gender]
    timezone: str = "Asia/Seoul"
```

#### **웰니스 설정**
```python
class WellnessProfile:
    fitness_level: FitnessLevel  # 초급/중급/고급
    primary_goals: List[WellnessGoal]  # 체중관리, 수면개선, 스트레스관리 등
    available_time_slots: List[TimeSlot]  # 운동 가능 시간대
    preferred_workout_types: List[WorkoutType]
    health_conditions: List[HealthCondition]  # 알레르기, 부상 이력 등
```

#### **개인화 데이터**
```python
class PersonalizationData:
    personality_type: Optional[str]  # MBTI 등
    motivation_style: MotivationStyle  # 경쟁형/성취형/관계형
    communication_preference: CommunicationStyle  # 친근함/전문적/간결함
    challenge_preference: ChallengeLevel  # 도전적/안정적/점진적
```

---

## 📝 **2. 습관 관리 모듈 (Habit Management)**

### **2.1 습관 카테고리 시스템**

#### **카테고리 구조**
```python
class HabitCategory:
    id: UUID
    name: str
    icon: str
    color_code: str
    parent_category_id: Optional[UUID]  # 대분류/소분류 구조
    
# 예시 카테고리
FITNESS = "운동"
├── CARDIO = "유산소"
├── STRENGTH = "근력운동"
└── FLEXIBILITY = "스트레칭"

NUTRITION = "영양"
├── MEAL_TIMING = "식사시간"
├── WATER_INTAKE = "수분섭취"
└── SUPPLEMENTS = "영양제"

MENTAL_HEALTH = "정신건강"
├── MEDITATION = "명상"
├── JOURNALING = "일기쓰기"
└── GRATITUDE = "감사표현"
```

### **2.2 습관 정의 (Habit Definition)**

#### **습관 템플릿**
```python
class HabitTemplate:
    id: UUID
    name: str
    description: str
    category_id: UUID
    difficulty_level: int  # 1-5
    estimated_time_minutes: int
    recommended_frequency: FrequencyType
    success_criteria: str
    tips: List[str]
    ai_coaching_prompts: List[str]
```

#### **사용자별 습관**
```python
class UserHabit:
    id: UUID
    user_id: UUID
    habit_template_id: UUID
    custom_name: Optional[str]  # 사용자 커스텀 이름
    target_frequency: FrequencyConfig
    reminder_settings: ReminderConfig
    reward_points: int
    created_at: datetime
    is_active: bool
    
class FrequencyConfig:
    type: FrequencyType  # DAILY, WEEKLY, MONTHLY
    count: int  # 주 3회, 일 2회 등
    specific_days: Optional[List[Weekday]]  # 특정 요일
    time_slots: Optional[List[TimeSlot]]  # 특정 시간대
```

### **2.3 습관 추천 엔진**

#### **개인화 추천 로직**
```python
class HabitRecommendationEngine:
    def recommend_habits(self, user_profile: UserProfile) -> List[HabitTemplate]:
        # 1. 사용자 목표 기반 필터링
        # 2. 현재 활성 습관과 균형 고려
        # 3. 난이도 조절 (점진적 증가)
        # 4. 시간 가용성 고려
        # 5. 개인 성향 반영
        pass
        
    def calculate_habit_compatibility(self, user: User, habit: HabitTemplate) -> float:
        # 호환성 점수 계산 (0.0 ~ 1.0)
        pass
```

---

## 📊 **3. 습관 추적 시스템 (Tracking System)**

### **3.1 일일 체크인 (Daily Check-in)**

#### **체크인 데이터 구조**
```python
class HabitLog:
    id: UUID
    user_habit_id: UUID
    logged_at: datetime
    completion_status: CompletionStatus  # COMPLETED, PARTIAL, SKIPPED
    completion_percentage: int  # 0-100
    duration_minutes: Optional[int]
    intensity_level: Optional[int]  # 1-5
    mood_before: Optional[int]  # 1-10
    mood_after: Optional[int]  # 1-10
    notes: Optional[str]
    location: Optional[str]
    weather_condition: Optional[str]
    energy_level: Optional[int]  # 1-5
    
class CompletionEvidence:
    log_id: UUID
    evidence_type: EvidenceType  # PHOTO, VIDEO, TIMER, GPS
    file_url: Optional[str]
    metadata: Dict[str, Any]
```

#### **자동 추적 기능**
```python
class AutoTrackingService:
    def integrate_health_data(self, user_id: UUID):
        # Apple Health, Google Fit 데이터 동기화
        pass
        
    def detect_activity_completion(self, user_id: UUID, habit_id: UUID) -> bool:
        # GPS, 가속도계 등을 활용한 자동 감지
        pass
        
    def smart_reminder_timing(self, user_habit: UserHabit) -> datetime:
        # 최적 리마인더 시간 계산
        pass
```

### **3.2 스트릭 (Streak) 시스템**

#### **스트릭 계산 로직**
```python
class StreakCalculator:
    def calculate_current_streak(self, user_habit_id: UUID) -> int:
        # 현재 연속 달성 일수
        pass
        
    def calculate_longest_streak(self, user_habit_id: UUID) -> int:
        # 최장 연속 달성 기록
        pass
        
    def predict_streak_risk(self, user_habit_id: UUID) -> float:
        # 스트릭 중단 위험도 예측 (0.0 ~ 1.0)
        pass
        
    def get_streak_recovery_suggestions(self, user_habit_id: UUID) -> List[str]:
        # 스트릭 회복을 위한 제안
        pass
```

### **3.3 진척도 분석**

#### **통계 계산**
```python
class ProgressAnalyzer:
    def calculate_completion_rate(self, user_habit_id: UUID, period: TimePeriod) -> float:
        # 완료율 계산
        pass
        
    def analyze_consistency_pattern(self, user_habit_id: UUID) -> ConsistencyPattern:
        # 일관성 패턴 분석
        pass
        
    def identify_optimal_timing(self, user_habit_id: UUID) -> List[TimeSlot]:
        # 최적 실행 시간대 분석
        pass
        
    def calculate_difficulty_adjustment(self, user_habit_id: UUID) -> int:
        # 난이도 조정 제안 (-2 ~ +2)
        pass
```

---

## 🤖 **4. AI 코칭 모듈 (AI Coaching)**

### **4.1 개인화 코칭 엔진**

#### **컨텍스트 수집**
```python
class CoachingContext:
    user_profile: UserProfile
    recent_logs: List[HabitLog]
    streak_status: Dict[UUID, int]
    mood_trends: List[MoodEntry]
    weather_data: WeatherInfo
    calendar_events: List[CalendarEvent]
    energy_patterns: EnergyPattern
    
class ContextAnalyzer:
    def analyze_current_situation(self, user_id: UUID) -> CoachingContext:
        # 현재 상황 종합 분석
        pass
        
    def identify_coaching_opportunities(self, context: CoachingContext) -> List[CoachingOpportunity]:
        # 코칭 필요 상황 감지
        pass
```

#### **메시지 생성 시스템**
```python
class AICoachingService:
    def generate_personalized_message(
        self, 
        context: CoachingContext,
        message_type: MessageType
    ) -> CoachingMessage:
        # OpenAI GPT-4 API 활용
        prompt = self.build_coaching_prompt(context, message_type)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return self.format_coaching_message(response)
        
    def build_coaching_prompt(self, context: CoachingContext, msg_type: MessageType) -> str:
        # 상황별 프롬프트 생성
        pass
```

#### **메시지 타입별 로직**
```python
class MessageType:
    MORNING_MOTIVATION = "morning_motivation"      # 아침 동기부여
    HABIT_REMINDER = "habit_reminder"             # 습관 리마인더  
    ENCOURAGEMENT = "encouragement"               # 격려 메시지
    STREAK_CELEBRATION = "streak_celebration"     # 스트릭 축하
    FAILURE_RECOVERY = "failure_recovery"         # 실패 극복
    WEEKLY_REFLECTION = "weekly_reflection"       # 주간 회고
    GOAL_ADJUSTMENT = "goal_adjustment"           # 목표 조정
    PROGRESS_INSIGHT = "progress_insight"         # 진척도 인사이트
```

### **4.2 스마트 알림 시스템**

#### **알림 최적화**
```python
class SmartNotificationEngine:
    def optimize_notification_timing(self, user_id: UUID) -> NotificationSchedule:
        # 사용자 행동 패턴 기반 최적 시간 계산
        pass
        
    def personalize_notification_content(
        self, 
        user_id: UUID, 
        notification_type: NotificationType
    ) -> str:
        # 개인화된 알림 메시지 생성
        pass
        
    def calculate_notification_frequency(self, user_id: UUID, habit_id: UUID) -> FrequencyConfig:
        # 개인별 최적 알림 빈도 계산
        pass
```

---

## 📈 **5. 분석/통계 모듈 (Analytics)**

### **5.1 개인 대시보드**

#### **핵심 지표 계산**
```python
class PersonalAnalytics:
    def calculate_wellness_score(self, user_id: UUID) -> float:
        # 종합 웰니스 점수 (0-100)
        habit_completion = self.get_habit_completion_rate(user_id)
        consistency = self.get_consistency_score(user_id)
        improvement = self.get_improvement_trend(user_id)
        return (habit_completion * 0.4 + consistency * 0.3 + improvement * 0.3)
        
    def generate_weekly_report(self, user_id: UUID) -> WeeklyReport:
        # 주간 성과 리포트
        pass
        
    def identify_improvement_areas(self, user_id: UUID) -> List[ImprovementArea]:
        # 개선 필요 영역 식별
        pass
```

#### **트렌드 분석**
```python
class TrendAnalyzer:
    def analyze_mood_habit_correlation(self, user_id: UUID) -> Dict[UUID, float]:
        # 기분-습관 상관관계 분석
        pass
        
    def detect_pattern_changes(self, user_id: UUID) -> List[PatternChange]:
        # 행동 패턴 변화 감지
        pass
        
    def predict_future_performance(self, user_id: UUID, days: int) -> PredictionResult:
        # 미래 성과 예측
        pass
```

### **5.2 인사이트 생성**

#### **AI 기반 인사이트**
```python
class InsightGenerator:
    def generate_personalized_insights(self, user_id: UUID) -> List[Insight]:
        # 개인화된 인사이트 생성
        pass
        
    def suggest_habit_optimizations(self, user_id: UUID) -> List[OptimizationSuggestion]:
        # 습관 최적화 제안
        pass
        
    def create_motivational_content(self, user_id: UUID) -> MotivationalContent:
        # 동기부여 콘텐츠 생성
        pass
```

---

## 🔔 **6. 알림 시스템 (Notification System)**

### **6.1 다중 채널 알림**

#### **푸시 알림 (Firebase FCM)**
```python
class PushNotificationService:
    def send_habit_reminder(self, user_id: UUID, habit: UserHabit):
        # 습관 리마인더 푸시
        pass
        
    def send_streak_alert(self, user_id: UUID, streak_data: StreakAlert):
        # 스트릭 관련 알림
        pass
        
    def send_ai_coaching_message(self, user_id: UUID, message: CoachingMessage):
        # AI 코칭 메시지
        pass
```

#### **이메일 알림 (SendGrid)**
```python
class EmailNotificationService:
    def send_weekly_report(self, user_id: UUID, report: WeeklyReport):
        # 주간 리포트 이메일
        pass
        
    def send_achievement_certificate(self, user_id: UUID, achievement: Achievement):
        # 성취 인증서 이메일
        pass
```

### **6.2 알림 개인화**

#### **학습 기반 최적화**
```python
class NotificationLearningEngine:
    def learn_user_response_patterns(self, user_id: UUID):
        # 사용자 반응 패턴 학습
        pass
        
    def optimize_notification_strategy(self, user_id: UUID) -> NotificationStrategy:
        # 알림 전략 최적화
        pass
        
    def predict_notification_effectiveness(
        self, 
        user_id: UUID, 
        notification: Notification
    ) -> float:
        # 알림 효과 예측
        pass
```

---

## 💳 **7. 결제/구독 모듈 (Payment & Subscription)**

### **7.1 구독 관리**

#### **구독 플랜 구조**
```python
class SubscriptionPlan:
    id: UUID
    name: str  # Basic, Premium, Pro
    price_monthly: int  # 원 단위
    price_yearly: int   # 원 단위 (할인 적용)
    features: List[Feature]
    ai_message_limit: Optional[int]  # None = 무제한
    
class UserSubscription:
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: SubscriptionStatus  # ACTIVE, EXPIRED, CANCELLED
    started_at: datetime
    expires_at: datetime
    auto_renewal: bool
    payment_method_id: UUID
```

#### **결제 처리 (아임포트)**
```python
class PaymentService:
    def process_subscription_payment(
        self, 
        user_id: UUID, 
        plan_id: UUID,
        payment_method: PaymentMethod
    ) -> PaymentResult:
        # 아임포트 API 연동
        pass
        
    def handle_payment_webhook(self, webhook_data: WebhookData):
        # 결제 완료/실패 웹훅 처리
        pass
        
    def process_refund(self, subscription_id: UUID, reason: str) -> RefundResult:
        # 환불 처리
        pass
```

### **7.2 사용량 관리**

#### **API 사용량 추적**
```python
class UsageTracker:
    def track_ai_message_usage(self, user_id: UUID, message_type: MessageType):
        # AI 메시지 사용량 추적
        pass
        
    def check_feature_access(self, user_id: UUID, feature: Feature) -> bool:
        # 기능 접근 권한 확인
        pass
        
    def calculate_usage_analytics(self, user_id: UUID) -> UsageAnalytics:
        # 사용량 분석
        pass
```

---

## 🎯 **구현 우선순위**

### **Phase 1: 핵심 기능 (MVP)**
1. ✅ 사용자 인증 (카카오 로그인)
2. ✅ 기본 습관 관리 (CRUD)
3. ✅ 습관 추적 (체크인, 스트릭)
4. ✅ 기본 AI 코칭 (OpenAI 연동)
5. ✅ 푸시 알림 기본 기능

### **Phase 2: 개인화 강화**
1. ✅ 개인화 프로필 시스템
2. ✅ 스마트 알림 최적화
3. ✅ 분석/인사이트 기능
4. ✅ 웨어러블 연동 준비

### **Phase 3: 비즈니스 기능**
1. ✅ 결제/구독 시스템
2. ✅ 관리자 대시보드
3. ✅ 고급 분석 기능
4. ✅ A/B 테스트 시스템

---

## 🔧 **기술 구현 고려사항**

### **성능 최적화**
- **Redis 캐싱**: 자주 조회되는 사용자 데이터
- **Database Indexing**: 쿼리 성능 최적화
- **Celery Background Jobs**: 무거운 AI 작업 비동기 처리
- **Connection Pooling**: DB 연결 풀 관리

### **보안**
- **JWT Token Validation**: 모든 API 엔드포인트 보호
- **Rate Limiting**: API 요청 제한 (Redis 기반)
- **Input Validation**: Pydantic 모델 활용
- **CORS Policy**: 도메인별 접근 제어

### **모니터링**
- **Sentry**: 에러 추적
- **CloudWatch**: 시스템 메트릭
- **Custom Metrics**: 비즈니스 KPI 추적
- **Health Check**: 서비스 상태 모니터링

---

**🎯 목표: 사용자가 진짜로 습관을 만들 수 있는 똑똑한 AI 코치 시스템 구축**