# 🛠️ WellnessAI 개발 가이드

> **개발 환경 설정부터 배포까지 - 개발자를 위한 완벽 가이드**

---

## 🚀 **개발 환경 설정**

### **Prerequisites**
- **Node.js**: 18.x 이상
- **Python**: 3.11.x
- **Docker & Docker Compose**: 최신 버전
- **Git**: 2.30 이상
- **PostgreSQL**: 16.x (로컬 개발용)
- **Redis**: 7.x (로컬 개발용)

### **Repository 클론 및 초기 설정**

```bash
# 1. Repository 클론
git clone https://github.com/djgnfj-svg/ai-wellness-habit-tracker.git
cd ai-wellness-habit-tracker

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 에디터로 열어 필요한 값들 설정

# 3. Docker로 개발 환경 실행 (권장)
docker-compose up -d

# 또는 로컬 환경 설정
# PostgreSQL, Redis 설치 및 실행 후
# 아래 스크립트 실행
./scripts/setup-dev.sh
```

### **프로젝트 구조**

```
ai-wellness-habit-tracker/
├── 📁 backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/                # API 라우터
│   │   ├── core/               # 핵심 설정, 보안
│   │   ├── models/             # SQLAlchemy 모델
│   │   ├── schemas/            # Pydantic 스키마
│   │   ├── services/           # 비즈니스 로직
│   │   ├── utils/              # 유틸리티 함수
│   │   └── main.py             # FastAPI 앱 진입점
│   ├── tests/                  # 백엔드 테스트
│   ├── migrations/             # DB 마이그레이션
│   ├── requirements.txt        # Python 의존성
│   └── Dockerfile
│
├── 📁 frontend/                # React Native 앱
│   ├── src/
│   │   ├── components/         # 재사용 컴포넌트
│   │   ├── screens/            # 화면 컴포넌트
│   │   ├── navigation/         # 네비게이션
│   │   ├── services/           # API 호출
│   │   ├── hooks/              # 커스텀 훅
│   │   ├── utils/              # 유틸리티
│   │   └── types/              # TypeScript 타입
│   ├── __tests__/              # 프론트엔드 테스트
│   ├── package.json
│   └── Dockerfile
│
├── 📁 web-admin/               # React 관리자 웹
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── 📁 ai-services/             # AI/ML 서비스
│   ├── coaching/               # AI 코칭 서비스
│   ├── analytics/              # 데이터 분석
│   ├── models/                 # ML 모델
│   └── requirements.txt
│
├── 📁 docs/                    # 프로젝트 문서
├── 📁 scripts/                 # 개발/배포 스크립트
├── 📁 .github/                 # GitHub Actions
├── docker-compose.yml          # 개발 환경 컨테이너
├── docker-compose.prod.yml     # 프로덕션 환경
└── .env.example                # 환경변수 예시
```

---

## 📝 **코딩 컨벤션**

### **Python (Backend)**

#### **코드 스타일**
```python
# Black 포맷터 사용 (88자 제한)
# isort로 import 정리
# flake8으로 린팅

# 함수명: snake_case
def create_user_habit(user_id: str, habit_data: dict) -> UserHabit:
    pass

# 클래스명: PascalCase  
class UserService:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_HABITS_PER_USER = 50

# 파일명: snake_case.py
# user_service.py, habit_controller.py
```

#### **타입 힌팅**
```python
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# 모든 함수에 타입 힌팅 필수
def get_user_habits(
    user_id: UUID, 
    status: Optional[str] = None
) -> List[UserHabit]:
    pass

# Pydantic 모델 사용
class CreateHabitRequest(BaseModel):
    name: str
    category_id: UUID
    target_frequency: str = "daily"
```

#### **에러 처리**
```python
from app.core.exceptions import NotFoundError, ValidationError

# 커스텀 예외 사용
if not user:
    raise NotFoundError("User not found")

# 로깅
import logging
logger = logging.getLogger(__name__)

try:
    result = some_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### **TypeScript (Frontend)**

#### **코드 스타일**
```typescript
// Prettier + ESLint 사용
// 함수명: camelCase
const getUserHabits = async (userId: string): Promise<UserHabit[]> => {
  // ...
}

// 컴포넌트명: PascalCase
const HabitCard: React.FC<HabitCardProps> = ({ habit }) => {
  // ...
}

// 상수: UPPER_SNAKE_CASE
const MAX_HABIT_NAME_LENGTH = 100;

// 파일명: PascalCase.tsx (컴포넌트), camelCase.ts (유틸리티)
// HabitCard.tsx, userService.ts
```

#### **타입 정의**
```typescript
// 인터페이스: PascalCase
interface UserHabit {
  id: string;
  name: string;
  category: HabitCategory;
  currentStreak: number;
}

// 타입 별칭: PascalCase
type HabitStatus = 'active' | 'paused' | 'completed';

// API 응답 타입
interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}
```

#### **React Hooks**
```typescript
// 커스텀 훅: use로 시작
const useUserHabits = (userId: string) => {
  const [habits, setHabits] = useState<UserHabit[]>([]);
  const [loading, setLoading] = useState(true);
  
  // useEffect, API 호출 등
  
  return { habits, loading, refetch };
};
```

### **Git 커밋 컨벤션**

```bash
# 형식: type(scope): subject

# Types:
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 스타일 변경 (포맷팅, 세미콜론 등)
refactor: 리팩토링
test: 테스트 추가/수정
chore: 빌드 과정 또는 보조 도구 변경

# 예시:
feat(auth): add social login with Kakao
fix(habits): resolve streak calculation bug
docs(api): update authentication endpoints
test(habits): add unit tests for habit service
```

---

## 🌿 **Git 워크플로우**

### **브랜치 전략**

```bash
main                    # 프로덕션 브랜치
├── develop            # 개발 통합 브랜치
│   ├── feature/auth-social-login
│   ├── feature/habit-tracking
│   └── feature/ai-coaching
├── release/v1.0.0     # 릴리즈 준비 브랜치
└── hotfix/critical-bug # 긴급 수정 브랜치
```

### **개발 워크플로우**

```bash
# 1. 새 기능 개발 시작
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 개발 진행
git add .
git commit -m "feat(scope): add new feature"

# 3. 중간 푸시 (백업 목적)
git push origin feature/new-feature

# 4. 개발 완료 후 PR 생성
# GitHub에서 feature/new-feature → develop PR 생성

# 5. 코드 리뷰 후 머지
# develop 브랜치로 머지 후 feature 브랜치 삭제

# 6. 릴리즈 준비
git checkout -b release/v1.0.0 develop
# 버전 업데이트, 버그 수정 등
git checkout main
git merge release/v1.0.0
git tag v1.0.0
```

---

## 🧪 **테스트 가이드**

### **Backend 테스트 (pytest)**

#### **테스트 구조**
```python
# tests/conftest.py - 테스트 설정
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
```

#### **단위 테스트**
```python
# tests/test_habit_service.py
def test_create_habit_success(test_user):
    service = HabitService()
    habit_data = {
        "name": "Daily Water",
        "category_id": "health-category-id"
    }
    
    result = service.create_habit(test_user["id"], habit_data)
    
    assert result.name == "Daily Water"
    assert result.status == "active"
```

#### **API 테스트**
```python
# tests/test_api_habits.py
def test_create_habit_endpoint(client, auth_headers):
    response = client.post(
        "/v1/users/me/habits",
        json={"name": "Daily Water", "category_id": "uuid"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Daily Water"
```

#### **테스트 실행**
```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app --cov-report=html

# 특정 테스트만 실행
pytest tests/test_habits.py::test_create_habit

# 빠른 테스트 (DB 관련 제외)
pytest -m "not slow"
```

### **Frontend 테스트 (Jest + Testing Library)**

#### **컴포넌트 테스트**
```typescript
// __tests__/components/HabitCard.test.tsx
import { render, screen } from '@testing-library/react-native';
import { HabitCard } from '../../src/components/HabitCard';

describe('HabitCard', () => {
  const mockHabit = {
    id: '1',
    name: 'Daily Water',
    currentStreak: 5
  };

  it('displays habit name and streak', () => {
    render(<HabitCard habit={mockHabit} />);
    
    expect(screen.getByText('Daily Water')).toBeOnTheScreen();
    expect(screen.getByText('5일 연속')).toBeOnTheScreen();
  });
});
```

#### **Hook 테스트**
```typescript
// __tests__/hooks/useUserHabits.test.ts
import { renderHook } from '@testing-library/react-hooks';
import { useUserHabits } from '../../src/hooks/useUserHabits';

jest.mock('../../src/services/api');

describe('useUserHabits', () => {
  it('fetches user habits on mount', async () => {
    const { result, waitForNextUpdate } = renderHook(() => 
      useUserHabits('user-1')
    );
    
    expect(result.current.loading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.habits).toHaveLength(2);
    expect(result.current.loading).toBe(false);
  });
});
```

---

## 🔧 **개발 도구 설정**

### **VS Code 설정**

#### **필수 확장**
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode-remote.remote-containers"
  ]
}
```

#### **설정**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### **Pre-commit Hooks**

```bash
# 설치
pip install pre-commit
pre-commit install

# .pre-commit-config.yaml에 설정된 훅들:
# - Black (Python 포맷팅)
# - isort (Import 정리)
# - flake8 (Python 린팅)
# - Prettier (JS/TS 포맷팅)
# - ESLint (JS/TS 린팅)
```

---

## 🗃️ **데이터베이스 관리**

### **마이그레이션**

```bash
# 새 마이그레이션 생성
cd backend
alembic revision --autogenerate -m "Add user habits table"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1

# 마이그레이션 히스토리
alembic history --verbose
```

### **시드 데이터**

```bash
# 개발용 시드 데이터 생성
python scripts/seed_data.py

# 특정 데이터만 시드
python scripts/seed_data.py --only habits,categories
```

### **데이터베이스 백업/복원**

```bash
# 백업
pg_dump wellnessai_dev > backup.sql

# 복원
psql wellnessai_dev < backup.sql

# Docker 환경에서
docker exec -t postgres pg_dump -U postgres wellnessai > backup.sql
```

---

## 🚀 **로컬 개발 서버 실행**

### **Docker Compose 사용 (권장)**

```bash
# 모든 서비스 실행
docker-compose up

# 특정 서비스만 실행
docker-compose up backend postgres redis

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend

# 서비스 재시작
docker-compose restart backend
```

### **개별 서비스 실행**

```bash
# Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (React Native)
cd frontend
npm install
npm start

# Web Admin (React)
cd web-admin  
npm install
npm run dev
```

---

## 🧩 **API 개발 가이드**

### **새 API 엔드포인트 추가**

```python
# 1. 스키마 정의 (backend/app/schemas/habits.py)
class CreateHabitRequest(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: UUID
    target_frequency: str = "daily"

class HabitResponse(BaseModel):
    id: UUID
    name: str
    category: HabitCategoryResponse
    created_at: datetime

# 2. 서비스 로직 (backend/app/services/habit_service.py)
class HabitService:
    async def create_habit(
        self, user_id: UUID, habit_data: CreateHabitRequest
    ) -> UserHabit:
        # 비즈니스 로직 구현
        pass

# 3. API 라우터 (backend/app/api/v1/habits.py)
@router.post("/", response_model=HabitResponse, status_code=201)
async def create_habit(
    habit_data: CreateHabitRequest,
    current_user: User = Depends(get_current_user),
    habit_service: HabitService = Depends()
):
    return await habit_service.create_habit(current_user.id, habit_data)

# 4. 테스트 작성 (tests/test_habits.py)
def test_create_habit_success(client, auth_headers):
    # 테스트 코드
    pass
```

### **API 문서 자동 생성**

```bash
# 개발 서버 실행 후 접속
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 📱 **모바일 앱 개발 가이드**

### **새 화면 추가**

```typescript
// 1. 타입 정의 (src/types/navigation.ts)
export type RootStackParamList = {
  HabitDetail: { habitId: string };
  // ...
};

// 2. 화면 컴포넌트 (src/screens/HabitDetailScreen.tsx)
import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';

type Props = {
  route: RouteProp<RootStackParamList, 'HabitDetail'>;
  navigation: StackNavigationProp<RootStackParamList>;
};

export const HabitDetailScreen: React.FC<Props> = ({ route, navigation }) => {
  const { habitId } = route.params;
  // ...
};

// 3. 네비게이션에 추가 (src/navigation/AppNavigator.tsx)
<Stack.Screen 
  name="HabitDetail" 
  component={HabitDetailScreen}
  options={{ title: '습관 상세' }}
/>
```

### **API 호출**

```typescript
// src/services/api/habitService.ts
export const habitService = {
  async getUserHabits(): Promise<UserHabit[]> {
    const response = await api.get('/users/me/habits');
    return response.data.habits;
  },

  async createHabit(habitData: CreateHabitRequest): Promise<UserHabit> {
    const response = await api.post('/users/me/habits', habitData);
    return response.data;
  }
};

// 컴포넌트에서 사용
const { data: habits, isLoading } = useQuery(
  ['userHabits'], 
  habitService.getUserHabits
);
```

---

## 🔍 **디버깅 가이드**

### **Backend 디버깅**

```python
# 로그 레벨 설정
import logging
logging.basicConfig(level=logging.DEBUG)

# 디버거 사용
import pdb; pdb.set_trace()

# 또는 VS Code 디버거 설정 (.vscode/launch.json)
{
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/backend/app/main.py",
  "console": "integratedTerminal"
}
```

### **Frontend 디버깅**

```typescript
// React Native Debugger 사용
// Flipper 연동 (네트워크, 로그, 레이아웃 검사)

// 로그 출력
console.log('Debug info:', { habitId, user });

// React Developer Tools
// Redux DevTools (상태 관리 시)
```

### **데이터베이스 디버깅**

```sql
-- 쿼리 성능 분석
EXPLAIN ANALYZE SELECT * FROM user_habits WHERE user_id = 'uuid';

-- 느린 쿼리 로그 확인
-- PostgreSQL 설정에서 log_min_duration_statement 설정

-- 인덱스 사용 확인
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats WHERE tablename = 'user_habits';
```

---

## 📋 **코드 리뷰 체크리스트**

### **일반**
- [ ] 커밋 메시지가 컨벤션을 따르는가?
- [ ] 코드가 가독성이 좋은가?
- [ ] 적절한 주석이 있는가?
- [ ] 하드코딩된 값이 없는가?

### **Backend**
- [ ] 타입 힌팅이 모든 함수에 있는가?
- [ ] 에러 처리가 적절한가?
- [ ] 데이터베이스 쿼리가 최적화되었는가?
- [ ] 보안 이슈가 없는가? (SQL 인젝션, XSS 등)
- [ ] API 응답 형식이 일관성 있는가?

### **Frontend**
- [ ] 컴포넌트가 재사용 가능한가?
- [ ] 불필요한 리렌더링이 없는가?
- [ ] 접근성 (a11y)을 고려했는가?
- [ ] 로딩 상태와 에러 상태를 처리했는가?
- [ ] 메모리 누수가 없는가?

### **테스트**
- [ ] 새로운 기능에 대한 테스트가 있는가?
- [ ] 테스트 커버리지가 적절한가?
- [ ] Edge case를 고려했는가?

---

## 🚚 **배포 가이드**

### **Staging 배포**

```bash
# 1. develop 브랜치에서 테스트
git checkout develop
git pull origin develop

# 2. 도커 이미지 빌드
docker build -t wellnessai-backend:staging ./backend
docker build -t wellnessai-frontend:staging ./frontend

# 3. 스테이징 환경에 배포
docker-compose -f docker-compose.staging.yml up -d

# 4. 마이그레이션 실행
docker-compose exec backend alembic upgrade head

# 5. 헬스체크
curl http://staging.api.wellnessai.kr/health
```

### **Production 배포**

```bash
# 1. 릴리즈 브랜치 생성
git checkout -b release/v1.0.0 develop

# 2. 버전 업데이트
# package.json, pyproject.toml 등에서 버전 업데이트

# 3. main 브랜치로 머지
git checkout main
git merge release/v1.0.0
git tag v1.0.0
git push origin main --tags

# 4. GitHub Actions가 자동으로 배포 진행
# 또는 수동 배포 스크립트 실행
./scripts/deploy-production.sh
```

---

## 🆘 **트러블슈팅**

### **자주 발생하는 문제들**

#### **Backend 관련**
```bash
# 1. 데이터베이스 연결 오류
# 해결: .env 파일의 DATABASE_URL 확인

# 2. 마이그레이션 오류
alembic downgrade -1  # 이전 버전으로 롤백
alembic upgrade head  # 다시 업그레이드

# 3. Redis 연결 오류  
# 해결: Redis 서버 상태 확인
redis-cli ping
```

#### **Frontend 관련**
```bash
# 1. Metro 캐시 문제
npx react-native start --reset-cache

# 2. iOS 빌드 오류
cd ios && pod install && cd ..

# 3. Android 빌드 오류
cd android && ./gradlew clean && cd ..
```

#### **Docker 관련**
```bash
# 1. 컨테이너 재시작
docker-compose restart service-name

# 2. 볼륨 초기화
docker-compose down -v
docker-compose up -d

# 3. 이미지 재빌드
docker-compose build --no-cache service-name
```

### **로그 확인**

```bash
# Backend 로그
docker-compose logs -f backend

# Database 로그
docker-compose logs -f postgres

# 모든 서비스 로그
docker-compose logs -f

# 특정 시간 이후 로그
docker-compose logs --since="2025-06-11T12:00:00" backend
```

---

## 📚 **추가 리소스**

### **문서**
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [React Native 공식 문서](https://reactnative.dev/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [Docker 가이드](https://docs.docker.com/)

### **유용한 도구**
- **Postman**: API 테스트
- **pgAdmin**: PostgreSQL 관리
- **Redis Commander**: Redis 관리
- **Flipper**: React Native 디버깅
- **Sentry**: 에러 트래킹

### **팀 커뮤니케이션**
- **Slack**: `#dev-backend`, `#dev-frontend`, `#dev-general`
- **GitHub Issues**: 버그 리포트, 기능 요청
- **GitHub Projects**: 태스크 관리
- **Figma**: 디자인 시스템

---

**🎯 목표: 효율적이고 일관성 있는 개발 환경으로 최고 품질의 코드 작성**