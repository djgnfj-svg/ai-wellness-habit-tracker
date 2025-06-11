# ⚙️ WellnessAI 기술 스택 및 아키텍처

> **현대적이고 확장 가능한 기술 스택으로 안정적인 서비스 구축**

---

## 🏗️ **시스템 아키텍처 개요**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web Admin     │    │   Landing Page  │
│  React Native   │    │     React       │    │    Next.js      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │                API Gateway                          │
         │              AWS ALB + CloudFront                  │
         └─────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │              Backend Services                       │
         │                  FastAPI                           │
         └─────────────────────────────────────────────────────┘
                                 │
    ┌────────────────┬───────────┼───────────┬─────────────────┐
    │                │           │           │                 │
┌───▼───┐    ┌──────▼─────┐ ┌───▼────┐ ┌───▼────┐    ┌──────▼─────┐
│ Redis │    │PostgreSQL  │ │S3 Bucket│ │AI/ML   │    │Third Party │
│ Cache │    │ Database   │ │ Storage │ │Services│    │  APIs      │
└───────┘    └────────────┘ └────────┘ └────────┘    └────────────┘
```

---

## 📱 **Frontend 기술 스택**

### **Mobile App - React Native**

#### **Core Framework**
- **React Native**: 0.73.x (최신 안정 버전)
- **Expo**: 50.x (개발 및 배포 간소화)
- **TypeScript**: 5.3.x (타입 안전성)

#### **State Management**
- **Zustand**: 4.x (가벼운 상태 관리)
- **React Query**: 5.x (서버 상태 관리)
- **AsyncStorage**: 로컬 데이터 저장

#### **UI/UX**
- **NativeBase**: 3.x (Native 컴포넌트 라이브러리)
- **React Native Reanimated**: 3.x (고성능 애니메이션)
- **Lottie**: 벡터 애니메이션
- **React Native Vector Icons**: 아이콘

#### **Navigation**
- **React Navigation**: 6.x (네이티브 네비게이션)
- **Deep Linking**: 앱 내 링크 지원

#### **Device Integration**
- **React Native Health**: 헬스 데이터 연동
- **Camera/Gallery**: 이미지 업로드
- **Push Notifications**: Firebase Cloud Messaging
- **Biometric Auth**: Face ID, Touch ID 지원

### **Web Admin - React**

#### **Core Framework**
- **React**: 18.x
- **TypeScript**: 5.3.x
- **Vite**: 5.x (빠른 빌드 도구)

#### **UI Framework**
- **Ant Design**: 5.x (관리자 UI)
- **Chart.js**: 데이터 시각화
- **React Table**: 테이블 컴포넌트

### **Landing Page - Next.js**

#### **Framework**
- **Next.js**: 14.x (App Router)
- **TypeScript**: 5.3.x
- **Tailwind CSS**: 3.x (스타일링)

#### **SEO & Performance**
- **Next SEO**: 메타데이터 관리
- **Google Analytics**: 4 (GA4)
- **Vercel**: 배포 및 CDN

---

## 🔧 **Backend 기술 스택**

### **API Server - FastAPI**

#### **Core Framework**
- **FastAPI**: 0.104.x (고성능 API 프레임워크)
- **Python**: 3.11.x
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증

#### **Database**
- **PostgreSQL**: 16.x (주 데이터베이스)
- **SQLAlchemy**: 2.x (ORM)
- **Alembic**: 데이터베이스 마이그레이션
- **Redis**: 7.x (캐싱, 세션)

#### **Authentication & Security**
- **JWT**: 토큰 기반 인증
- **bcrypt**: 비밀번호 해싱
- **OAuth 2.0**: 소셜 로그인 (카카오, 네이버, 구글)
- **Rate Limiting**: 요청 제한

#### **API Documentation**
- **OpenAPI 3.0**: 자동 API 문서 생성
- **Swagger UI**: 대화형 API 문서
- **Redoc**: 깔끔한 API 문서

### **Background Jobs**
- **Celery**: 비동기 작업 처리
- **Redis**: 메시지 브로커
- **Flower**: Celery 모니터링

---

## 🤖 **AI/ML 기술 스택**

### **AI Services**

#### **Language Models**
- **OpenAI GPT-4**: 개인화된 코칭 메시지
- **OpenAI GPT-3.5 Turbo**: 일반적인 조언
- **OpenAI Embeddings**: 텍스트 유사도 분석

#### **Machine Learning**
- **Python**: 3.11.x
- **Pandas**: 데이터 처리
- **NumPy**: 수치 계산
- **Scikit-learn**: 전통적 ML 알고리즘
- **TensorFlow Lite**: 모바일 ML 추론

#### **Data Analytics**
- **Apache Airflow**: 데이터 파이프라인
- **Jupyter Notebook**: 데이터 분석
- **Plotly**: 데이터 시각화

### **AI Features Architecture**

```python
# 개인화 AI 코칭 파이프라인
User Data → Context Analysis → Prompt Engineering → GPT-4 → Personalized Message

# 습관 추천 엔진
User Profile + Historical Data → ML Model → Habit Recommendations

# 성공률 예측
User Behavior Pattern → Time Series Analysis → Success Probability
```

---

## ☁️ **클라우드 인프라 (AWS)**

### **Compute**
- **ECS Fargate**: 컨테이너 기반 서비스 운영
- **Lambda**: 서버리스 함수 (이미지 처리, 알림)
- **API Gateway**: API 관리 및 보안

### **Database & Storage**
- **RDS PostgreSQL**: 관리형 데이터베이스
- **ElastiCache Redis**: 관리형 캐시
- **S3**: 정적 파일 저장 (이미지, 백업)
- **CloudFront**: CDN

### **Monitoring & Logging**
- **CloudWatch**: 로그 및 메트릭
- **X-Ray**: 분산 추적
- **AWS Config**: 리소스 모니터링

### **Security**
- **WAF**: 웹 애플리케이션 방화벽
- **Certificate Manager**: SSL/TLS 인증서
- **Secrets Manager**: 민감 정보 관리
- **IAM**: 권한 관리

---

## 🛠️ **개발 도구 및 DevOps**

### **Version Control**
- **Git**: 소스코드 관리
- **GitHub**: 코드 저장소
- **GitHub Actions**: CI/CD 파이프라인

### **Package Management**
- **Poetry**: Python 패키지 관리
- **npm/yarn**: Node.js 패키지 관리

### **Code Quality**
- **ESLint**: JavaScript/TypeScript 린팅
- **Prettier**: 코드 포매팅
- **Black**: Python 코드 포매팅
- **mypy**: Python 타입 체킹
- **Husky**: Git hooks

### **Testing**
- **Jest**: JavaScript 테스트
- **pytest**: Python 테스트
- **Detox**: React Native E2E 테스트
- **Codecov**: 코드 커버리지

### **Containerization**
- **Docker**: 컨테이너화
- **Docker Compose**: 로컬 개발 환경

### **Monitoring & Analytics**
- **Sentry**: 에러 트래킹
- **Mixpanel**: 사용자 행동 분석
- **Firebase Analytics**: 모바일 앱 분석

---

## 🔌 **Third-Party Integrations**

### **Payment**
- **아임포트**: 국내 결제 게이트웨이
- **Stripe**: 해외 결제 (추후 확장)

### **Social Login**
- **카카오 로그인**: 한국 사용자 주요 로그인
- **네이버 로그인**: 대안 로그인
- **Google OAuth**: 글로벌 확장 대비

### **Communication**
- **Firebase Cloud Messaging**: 푸시 알림
- **SendGrid**: 이메일 발송
- **Twilio**: SMS 발송 (추후 확장)

### **Health Data**
- **Apple HealthKit**: iOS 헬스 데이터
- **Google Fit**: Android 헬스 데이터
- **Samsung Health**: 삼성 헬스 데이터

### **Analytics & Marketing**
- **Google Analytics 4**: 웹 분석
- **Facebook Pixel**: 광고 추적
- **Amplitude**: 프로덕트 분석

---

## 📊 **데이터 아키텍처**

### **Data Flow**

```
Mobile App → API Gateway → FastAPI → PostgreSQL
     ↓
Analytics Events → Firebase Analytics → BigQuery → Dashboard
     ↓
AI Training Data → S3 → ML Pipeline → Updated Models
```

### **Database Schema 핵심 테이블**

```sql
-- 사용자 정보
users (id, email, profile_data, created_at)

-- 습관 정의
habits (id, name, category, difficulty_level)

-- 사용자 습관 추적
user_habits (id, user_id, habit_id, target_frequency, created_at)

-- 일일 체크인 기록
habit_logs (id, user_habit_id, logged_at, notes, mood_score)

-- AI 코칭 메시지
coaching_messages (id, user_id, message, sent_at, context)
```

---

## 🚀 **성능 최적화**

### **Frontend Optimization**
- **Code Splitting**: 번들 크기 최적화
- **Lazy Loading**: 필요시 컴포넌트 로드
- **Image Optimization**: WebP 포맷, 압축
- **Offline Support**: 오프라인 기능 지원

### **Backend Optimization**
- **Database Indexing**: 쿼리 성능 최적화
- **Redis Caching**: 자주 사용되는 데이터 캐싱
- **Connection Pooling**: 데이터베이스 연결 풀
- **Background Jobs**: 무거운 작업 비동기 처리

### **API Optimization**
- **GraphQL Subscription**: 실시간 데이터 (추후 고려)
- **REST API Versioning**: API 버전 관리
- **Rate Limiting**: 요청 제한으로 안정성 확보

---

## 🔒 **보안 전략**

### **Data Protection**
- **GDPR 준수**: 유럽 사용자 데이터 보호
- **개인정보보호법 준수**: 한국 개인정보 보호
- **End-to-End Encryption**: 민감 데이터 암호화
- **Data Anonymization**: 분석용 데이터 익명화

### **API Security**
- **JWT Token Rotation**: 토큰 만료 및 갱신
- **CORS Policy**: 크로스 오리진 정책
- **Input Validation**: 입력 데이터 검증
- **SQL Injection Prevention**: 파라미터화 쿼리

### **Infrastructure Security**
- **VPC**: 네트워크 격리
- **Security Groups**: 방화벽 규칙
- **WAF Rules**: 웹 공격 방어
- **DDoS Protection**: CloudFlare 보호

---

## 📈 **확장성 계획**

### **Phase 1: MVP (현재)**
- 기본적인 습관 추적 및 AI 코칭
- 단일 리전 (ap-northeast-2, 서울)
- 1만 명 사용자 지원

### **Phase 2: Growth (6개월 후)**
- 소셜 기능 추가
- 웨어러블 디바이스 연동
- 10만 명 사용자 지원
- Multi-AZ 배포

### **Phase 3: Scale (1년 후)**
- 글로벌 확장 (일본, 동남아)
- 마이크로서비스 아키텍처
- 100만 명 사용자 지원
- Multi-Region 배포

---

## 💰 **기술 비용 예상**

### **월 운영 비용** (사용자 수 기준)

| 사용자 수 | AWS 비용 | OpenAI API | 기타 서비스 | 총 비용 |
|----------|----------|------------|-------------|---------|
| 1,000명 | $200 | $100 | $50 | $350 |
| 10,000명 | $800 | $500 | $200 | $1,500 |
| 100,000명 | $5,000 | $3,000 | $1,000 | $9,000 |

### **개발 도구 비용** (연간)
- **GitHub Team**: $48/월
- **Sentry**: $26/월
- **Mixpanel**: $89/월
- **기타 도구**: $100/월
- **총 도구 비용**: $263/월

---

## 📋 **기술 스택 선택 이유**

### **React Native vs Flutter**
✅ **React Native 선택 이유:**
- 개발자 풀이 더 크고 채용이 용이
- JavaScript/TypeScript 생태계 활용
- 웹 개발자의 빠른 모바일 전환 가능
- Expo를 통한 빠른 개발 및 배포

### **FastAPI vs Django/Flask**
✅ **FastAPI 선택 이유:**
- 높은 성능 (비동기 처리)
- 자동 API 문서 생성
- 타입 힌팅 지원
- 현대적인 Python 기능 활용

### **PostgreSQL vs MongoDB**
✅ **PostgreSQL 선택 이유:**
- ACID 트랜잭션 지원
- 복잡한 쿼리 및 관계 처리
- JSON 데이터 타입 지원
- 성숙한 생태계

---

**🎯 목표: 안정적이고 확장 가능한 기술 기반으로 최고의 사용자 경험 제공**