# WellnessAI Backend User Module

AI 기반 웰니스 습관 추적 플랫폼의 백엔드 사용자 관리 모듈입니다.

## 📋 구현된 기능

### ✅ 완성된 기능들

#### 1. 사용자 인증 (Authentication)
- **소셜 로그인**: 카카오, 네이버, 구글
- **JWT 토큰 시스템**: Access Token + Refresh Token
- **토큰 갱신**: 자동 토큰 갱신 로직
- **로그아웃**: 안전한 로그아웃 처리
- **계정 탈퇴**: 사용자 데이터 비활성화

#### 2. 사용자 프로필 관리
- **기본 프로필**: 이메일, 닉네임, 프로필 이미지, 출생년도, 성별
- **웰니스 프로필**: 피트니스 레벨, 목표, 운동 선호도, 건강 상태
- **개인화 데이터**: 성격 유형, 동기부여 스타일, 커뮤니케이션 선호도

#### 3. 보안 기능
- **비밀번호 해싱**: bcrypt 암호화
- **Rate Limiting**: API 요청 제한 (구조만 구현)
- **입력 검증**: Pydantic 모델 검증
- **예외 처리**: 커스텀 예외 시스템

## 🏗️ 프로젝트 구조

```
backend/
├── app/
│   ├── api/                    # API 엔드포인트
│   │   ├── dependencies.py     # 공통 의존성 (인증, DB 세션)
│   │   └── v1/
│   │       ├── api.py          # 라우터 통합
│   │       └── endpoints/
│   │           ├── auth.py     # 인증 API
│   │           └── users.py    # 사용자 API
│   ├── core/                   # 핵심 설정
│   │   ├── config.py          # 환경 설정
│   │   ├── database.py        # DB 연결 설정
│   │   ├── security.py        # JWT, 암호화
│   │   └── exceptions.py      # 커스텀 예외
│   ├── models/                # SQLAlchemy 모델
│   │   ├── base.py           # 기본 모델
│   │   └── user.py           # 사용자 관련 모델
│   ├── schemas/               # Pydantic 스키마
│   │   ├── auth.py           # 인증 스키마
│   │   ├── common.py         # 공통 스키마
│   │   └── user.py           # 사용자 스키마
│   ├── services/             # 비즈니스 로직
│   │   ├── auth_service.py   # 인증 서비스
│   │   └── user_service.py   # 사용자 서비스
│   ├── utils/                # 유틸리티
│   │   ├── helpers.py        # 도움 함수
│   │   └── validators.py     # 검증 함수
│   └── main.py               # FastAPI 앱 진입점
├── main.py                   # 메인 실행 파일
├── requirements.txt          # 패키지 의존성
└── .env.example             # 환경변수 예시
```

## 🚀 실행 방법

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
# 기본 설정
APP_NAME="WellnessAI"
DEBUG=True
API_V1_STR="/api/v1"

# 보안
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_HOURS=1
REFRESH_TOKEN_EXPIRE_DAYS=30

# 데이터베이스
DATABASE_URL="postgresql+asyncpg://user:password@localhost/wellnessai"

# Redis (선택사항)
REDIS_URL="redis://localhost:6379"

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 소셜 로그인 (선택사항)
KAKAO_CLIENT_ID="your-kakao-client-id"
KAKAO_CLIENT_SECRET="your-kakao-client-secret"
NAVER_CLIENT_ID="your-naver-client-id"
NAVER_CLIENT_SECRET="your-naver-client-secret"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

### 3. 데이터베이스 설정

PostgreSQL 데이터베이스를 설정하고 Alembic으로 마이그레이션을 실행하세요:

```bash
# Alembic 초기화 (이미 완료됨)
# alembic init alembic

# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Create user tables"

# 마이그레이션 실행
alembic upgrade head
```

### 4. 서버 실행

```bash
# 개발 서버 실행
python main.py

# 또는 직접 uvicorn 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면 다음 URL에서 확인할 수 있습니다:
- API 문서: http://localhost:8000/docs
- 대체 API 문서: http://localhost:8000/redoc
- 헬스 체크: http://localhost:8000/health

## 📚 API 엔드포인트

### 인증 API (`/api/v1/auth`)

```http
POST /auth/kakao/login     # 카카오 로그인
POST /auth/naver/login     # 네이버 로그인
POST /auth/google/login    # 구글 로그인
POST /auth/refresh         # 토큰 갱신
POST /auth/logout          # 로그아웃
GET  /auth/me             # 현재 사용자 정보
DELETE /auth/account      # 계정 탈퇴
```

### 사용자 API (`/api/v1/users`)

```http
GET  /users/profile              # 사용자 프로필 조회
PUT  /users/profile              # 사용자 프로필 업데이트
GET  /users/wellness-profile     # 웰니스 프로필 조회
PUT  /users/wellness-profile     # 웰니스 프로필 업데이트
GET  /users/personalization      # 개인화 데이터 조회
PUT  /users/personalization      # 개인화 데이터 업데이트
```

## 🔧 개발 도구

### 코드 포맷팅

```bash
# Black 포맷팅
black app/

# isort 임포트 정리
isort app/
```

### 테스트 실행

```bash
# pytest 실행
pytest

# 커버리지와 함께
pytest --cov=app
```

## 📝 다음 단계

현재 사용자 관리 모듈이 완성되었습니다. 다음으로 구현할 기능들:

1. **습관 관리 모듈**: 습관 CRUD, 카테고리, 추천 시스템
2. **추적 시스템**: 일일 체크인, 스트릭, 진척도 분석
3. **AI 코칭**: OpenAI 연동, 개인화 메시지
4. **알림 시스템**: FCM 푸시 알림, 이메일 알림
5. **분석/통계**: 대시보드, 리포트, 인사이트
6. **결제/구독**: 아임포트 연동, 구독 관리

## 🛠️ 기술 스택

- **웹 프레임워크**: FastAPI 0.104+
- **데이터베이스**: PostgreSQL + SQLAlchemy 2.0
- **인증**: JWT (python-jose)
- **비밀번호 해싱**: bcrypt
- **HTTP 클라이언트**: httpx (소셜 로그인)
- **검증**: Pydantic v2
- **비동기**: async/await

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues에 등록해 주세요.
