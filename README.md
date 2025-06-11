# 🌱 WellnessAI - AI 웰니스 습관 추적기

> **당신만의 AI 웰니스 코치가 24시간 함께합니다**

20-30대 재택근무 여성을 위한 개인 맞춤형 웰니스 습관 형성 솔루션

---

## 🎯 **프로젝트 개요**

**WellnessAI**는 AI 기술을 활용해 개인 맞춤형 웰니스 코칭과 습관 형성을 지원하는 모바일 앱입니다.

### **핵심 가치**
- 🤖 **AI 기반 개인화**: 맥락적 상황 인식을 통한 진짜 맞춤형 코칭
- 🇰🇷 **한국 시장 특화**: K-뷰티 문화와 재택근무 환경에 최적화
- 📈 **높은 유지율**: 업계 평균 12% → 목표 40% 달성

### **타겟 고객**
25-35세 재택근무 여성 | 연봉 3,500만원 이상 | 자기계발 관심 높음

### **비즈니스 목표**
- **1년차**: 다운로드 5만건, 월 활성 사용자 1만명, 월매출 3,600만원
- **3년차**: 다운로드 50만건, 월 활성 사용자 10만명, 월매출 4.8억원

---

## 📚 **프로젝트 문서**

### **핵심 4대 문서**

1. **[📋 사업 기획서](./docs/01-BUSINESS_PLAN.md)**
   - 해결하려는 문제와 솔루션
   - 타겟 고객 및 시장 분석
   - 수익 모델 및 비즈니스 목표
   - 차별화 전략

2. **[🛠️ 기능 정의서](./docs/02-FEATURE_SPECIFICATION.md)**
   - Python/FastAPI 기반 상세 기능 명세
   - 7개 핵심 모듈 (사용자관리, 습관관리, 추적시스템, AI코칭 등)
   - 구현 우선순위 및 기술 고려사항

3. **[📱 화면 설계서](./docs/03-SCREEN_DESIGN.md)**
   - 사용자 여정 및 네비게이션 구조
   - 주요 화면별 상세 설계
   - UI/UX 가이드라인

4. **[🔌 API 명세서](./docs/04-API_SPECIFICATION.md)**
   - FastAPI 기반 RESTful API 명세
   - 인증, 사용자, 습관, 추적, AI코칭, 분석, 알림, 결제 API
   - 요청/응답 형식 및 에러 처리

---

## 🏗️ **기술 스택**

### **Frontend**
- **Mobile**: React Native + Expo + TypeScript
- **Web Admin**: React + TypeScript + Ant Design
- **Landing**: Next.js + Tailwind CSS

### **Backend**
- **API**: FastAPI + Python 3.11
- **Database**: PostgreSQL + Redis
- **AI**: OpenAI GPT-4 + Custom ML Models

### **Infrastructure**
- **Cloud**: AWS (ECS, RDS, ElastiCache, S3)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry + CloudWatch

---

## 🚀 **빠른 시작**

### **개발 환경 설정**

```bash
# 저장소 클론
git clone https://github.com/djgnfj-svg/ai-wellness-habit-tracker.git
cd ai-wellness-habit-tracker

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키들을 추가하세요

# 백엔드 개발 환경 (추후 구현)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 프론트엔드 개발 환경 (추후 구현)  
cd frontend
npm install
expo start
```

### **주요 환경 변수**

```env
# AI 서비스
OPENAI_API_KEY=sk-your-openai-api-key

# 소셜 로그인
KAKAO_CLIENT_ID=your-kakao-app-id
NAVER_CLIENT_ID=your-naver-client-id
GOOGLE_CLIENT_ID=your-google-client-id

# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/wellnessai_dev

# AWS 설정
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=wellnessai-uploads
```

---

## 📂 **프로젝트 구조** (계획)

```
ai-wellness-habit-tracker/
├── 📋 docs/                     # 프로젝트 문서
│   ├── 01-BUSINESS_PLAN.md       # 사업 기획서
│   ├── 02-FEATURE_SPECIFICATION.md # 기능 정의서
│   ├── 03-SCREEN_DESIGN.md       # 화면 설계서
│   └── 04-API_SPECIFICATION.md   # API 명세서
├── 📱 frontend/                  # React Native 앱 (개발 예정)
│   ├── src/
│   ├── components/
│   └── screens/
├── 🔧 backend/                   # FastAPI 서버 (개발 예정)
│   ├── app/
│   ├── models/
│   ├── routers/
│   └── services/
├── 🤖 ai-services/              # AI/ML 서비스 (개발 예정)
│   ├── coaching/
│   ├── recommendations/
│   └── analytics/
├── 🌐 web-admin/                # 관리자 웹 (개발 예정)
└── 📄 .env.example              # 환경변수 템플릿
```

---

## 🎯 **개발 우선순위**

### **Phase 1: MVP 핵심 기능 (2개월)**
- ✅ 카카오 로그인
- ✅ 기본 습관 관리 (CRUD)
- ✅ 습관 추적 시스템
- ✅ AI 코칭 기본 기능
- ✅ 푸시 알림

### **Phase 2: 개인화 강화 (1개월)**
- ✅ 개인화 프로필 시스템
- ✅ 스마트 알림 최적화
- ✅ 분석/인사이트 기능

### **Phase 3: 비즈니스 기능 (1개월)**
- ✅ 결제/구독 시스템
- ✅ 관리자 대시보드
- ✅ 고급 분석 기능

---

## 🤝 **기여하기**

### **개발 환경 요구사항**
- **Python**: 3.11+
- **Node.js**: 18+
- **React Native CLI**: 최신 버전
- **PostgreSQL**: 14+
- **Redis**: 7+

### **개발 가이드라인**
- **코드 스타일**: Black (Python), Prettier (JavaScript/TypeScript)
- **커밋 메시지**: [Conventional Commits](https://www.conventionalcommits.org/) 규칙 준수
- **브랜치**: `feature/기능명`, `fix/버그명` 형식
- **PR 리뷰**: 최소 1명 승인 필요

### **이슈 리포팅**
- **버그 리포트**: [Issues](https://github.com/djgnfj-svg/ai-wellness-habit-tracker/issues) 탭 활용
- **기능 제안**: Discussion 탭에서 논의 후 Issue 생성
- **보안 취약점**: 이메일로 직접 연락

---

## 📊 **현재 진행 상황**

### **완료된 작업**
- ✅ 프로젝트 기획 및 문서화
- ✅ 기술 스택 선정
- ✅ UI/UX 설계
- ✅ API 명세 작성
- ✅ 개발 환경 설정 가이드

### **진행 중인 작업**
- 🔄 MVP 백엔드 개발 착수
- 🔄 프론트엔드 개발 환경 구성
- 🔄 AI 코칭 모델 프로토타입

### **예정된 작업**
- 📅 베타 테스트 사용자 모집 (8월)
- 📅 앱스토어 출시 준비 (9월)
- 📅 마케팅 캠페인 시작 (9월)

---

## 🏆 **성과 지표**

### **개발 지표**
- **코드 커버리지**: 목표 80%+
- **API 응답 시간**: 평균 200ms 이하
- **앱 크래시율**: 0.1% 이하

### **비즈니스 지표**
- **사용자 유지율**: 30일 기준 30%+
- **앱스토어 평점**: 4.5점+
- **월 활성 사용자**: 단계별 목표 달성

---

## 📞 **연락처**

- **프로젝트 관리자**: [GitHub Profile](https://github.com/djgnfj-svg)
- **이슈 및 문의**: [GitHub Issues](https://github.com/djgnfj-svg/ai-wellness-habit-tracker/issues)
- **이메일**: (추후 공개)

---

## 📜 **라이선스**

이 프로젝트는 MIT 라이선스 하에 공개됩니다. 자세한 내용은 [LICENSE](./LICENSE) 파일을 참조하세요.

---

**🎯 목표: 2025년 한국 웰니스 앱 시장의 새로운 스탠다드 되기**

> *"혼자서도 건강한 습관을 만들 수 있어요. WellnessAI가 24시간 당신을 응원할게요! 💪"*