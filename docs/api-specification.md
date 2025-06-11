# 🔌 WellnessAI API 명세서

> **RESTful API 설계 문서 - OpenAPI 3.0 표준**

---

## 📋 **API 개요**

### **Base URL**
- **Production**: `https://api.wellnessai.kr/v1`
- **Staging**: `https://api-staging.wellnessai.kr/v1`
- **Development**: `http://localhost:8000/v1`

### **Authentication**
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <jwt_token>`
- **Token Expiry**: Access Token (1시간), Refresh Token (30일)

### **Content Type**
- **Request**: `application/json`
- **Response**: `application/json`

### **Rate Limiting**
- **일반 사용자**: 1000 requests/hour
- **프리미엄 사용자**: 5000 requests/hour

---

## 🔐 **Authentication & User Management**

### **POST /auth/register**
사용자 회원가입

```json
// Request
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "name": "김웰니스",
  "birth_year": 1990,
  "gender": "female",
  "agreed_to_terms": true,
  "agreed_to_privacy": true
}

// Response (201 Created)
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "김웰니스",
    "created_at": "2025-06-11T12:00:00Z"
  },
  "tokens": {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "expires_in": 3600
  }
}
```

### **POST /auth/login**
사용자 로그인

```json
// Request
{
  "email": "user@example.com",
  "password": "securePassword123!"
}

// Response (200 OK)
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "김웰니스",
    "subscription_plan": "premium"
  },
  "tokens": {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "expires_in": 3600
  }
}
```

### **POST /auth/social/kakao**
카카오 소셜 로그인

```json
// Request
{
  "access_token": "kakao-access-token"
}

// Response (200 OK)
{
  "user": {
    "id": "uuid-string",
    "email": "user@kakao.com",
    "name": "김웰니스",
    "provider": "kakao"
  },
  "tokens": {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "expires_in": 3600
  }
}
```

### **POST /auth/refresh**
토큰 갱신

```json
// Request
{
  "refresh_token": "jwt-refresh-token"
}

// Response (200 OK)
{
  "access_token": "new-jwt-access-token",
  "expires_in": 3600
}
```

### **GET /users/me**
현재 사용자 정보 조회

```json
// Response (200 OK)
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "김웰니스",
  "birth_year": 1990,
  "gender": "female",
  "subscription_plan": "premium",
  "timezone": "Asia/Seoul",
  "created_at": "2025-06-11T12:00:00Z",
  "updated_at": "2025-06-11T12:00:00Z"
}
```

### **PUT /users/me**
사용자 정보 수정

```json
// Request
{
  "name": "김웰니스 수정",
  "timezone": "Asia/Seoul",
  "notification_settings": {
    "push_enabled": true,
    "email_enabled": false,
    "reminder_time": "09:00"
  }
}

// Response (200 OK)
{
  "id": "uuid-string",
  "name": "김웰니스 수정",
  "timezone": "Asia/Seoul",
  "updated_at": "2025-06-11T12:30:00Z"
}
```

---

## 📝 **Habit Management**

### **GET /habits**
사용 가능한 습관 목록 조회

```json
// Query Parameters
?category=exercise&difficulty=beginner&limit=20&offset=0

// Response (200 OK)
{
  "habits": [
    {
      "id": "habit-uuid-1",
      "name": "물 마시기",
      "description": "하루 8잔의 물 마시기",
      "category": "health",
      "difficulty": "beginner",
      "estimated_time": 5,
      "icon": "water-glass",
      "color": "#4FC3F7"
    },
    {
      "id": "habit-uuid-2", 
      "name": "10분 명상",
      "description": "매일 아침 10분 명상하기",
      "category": "mindfulness",
      "difficulty": "intermediate",
      "estimated_time": 10,
      "icon": "meditation",
      "color": "#AB47BC"
    }
  ],
  "total": 50,
  "has_more": true
}
```

### **GET /users/me/habits**
사용자의 현재 습관 목록

```json
// Response (200 OK)
{
  "habits": [
    {
      "id": "user-habit-uuid-1",
      "habit": {
        "id": "habit-uuid-1",
        "name": "물 마시기",
        "category": "health",
        "icon": "water-glass",
        "color": "#4FC3F7"
      },
      "target_frequency": "daily",
      "target_count": 8,
      "started_at": "2025-06-01T00:00:00Z",
      "current_streak": 10,
      "best_streak": 15,
      "completion_rate": 0.85,
      "status": "active"
    }
  ]
}
```

### **POST /users/me/habits**
새 습관 추가

```json
// Request
{
  "habit_id": "habit-uuid-1",
  "target_frequency": "daily", // daily, weekly, custom
  "target_count": 8,
  "reminder_times": ["09:00", "15:00", "21:00"],
  "notes": "건강한 하루를 위해 시작!"
}

// Response (201 Created)
{
  "id": "user-habit-uuid-1",
  "habit": {
    "id": "habit-uuid-1",
    "name": "물 마시기"
  },
  "target_frequency": "daily",
  "target_count": 8,
  "started_at": "2025-06-11T12:00:00Z",
  "status": "active"
}
```

### **PUT /users/me/habits/{habit_id}**
습관 설정 수정

```json
// Request
{
  "target_count": 10,
  "reminder_times": ["08:00", "14:00", "20:00"],
  "status": "paused"
}

// Response (200 OK)
{
  "id": "user-habit-uuid-1",
  "target_count": 10,
  "reminder_times": ["08:00", "14:00", "20:00"],
  "status": "paused",
  "updated_at": "2025-06-11T12:30:00Z"
}
```

---

## ✅ **Habit Tracking**

### **POST /users/me/habits/{habit_id}/logs**
습관 체크인

```json
// Request
{
  "completed_count": 1,
  "completed_at": "2025-06-11T09:30:00Z",
  "mood_score": 8, // 1-10 scale
  "energy_level": 7, // 1-10 scale
  "notes": "아침에 물 한 잔 마셨어요!",
  "location": "home", // home, office, gym, etc.
  "image_url": "https://s3.../progress-photo.jpg"
}

// Response (201 Created)
{
  "id": "log-uuid-1",
  "user_habit_id": "user-habit-uuid-1",
  "completed_count": 1,
  "completed_at": "2025-06-11T09:30:00Z",
  "mood_score": 8,
  "energy_level": 7,
  "streak_count": 11,
  "achievement_unlocked": {
    "id": "streak-10",
    "name": "물 마시기 10일 연속",
    "icon": "trophy"
  }
}
```

### **GET /users/me/habits/{habit_id}/logs**
습관 로그 조회

```json
// Query Parameters
?start_date=2025-06-01&end_date=2025-06-11&limit=50

// Response (200 OK)
{
  "logs": [
    {
      "id": "log-uuid-1",
      "completed_count": 1,
      "completed_at": "2025-06-11T09:30:00Z",
      "mood_score": 8,
      "energy_level": 7,
      "notes": "아침에 물 한 잔 마셨어요!"
    }
  ],
  "stats": {
    "total_logs": 25,
    "completion_rate": 0.85,
    "current_streak": 11,
    "average_mood": 7.5
  }
}
```

### **GET /users/me/dashboard**
대시보드 데이터

```json
// Response (200 OK)
{
  "today_summary": {
    "date": "2025-06-11",
    "total_habits": 5,
    "completed_habits": 3,
    "completion_rate": 0.6,
    "mood_average": 7.5,
    "energy_average": 8.0
  },
  "streak_summary": {
    "longest_current_streak": {
      "habit_name": "물 마시기",
      "streak_count": 11
    },
    "total_active_streaks": 3
  },
  "weekly_progress": [
    {
      "date": "2025-06-05",
      "completion_rate": 0.8
    },
    {
      "date": "2025-06-06", 
      "completion_rate": 0.6
    }
  ],
  "achievements": [
    {
      "id": "first-week",
      "name": "첫 주 완주",
      "description": "첫 주를 성공적으로 완주했습니다!",
      "earned_at": "2025-06-07T23:59:59Z",
      "icon": "calendar-week"
    }
  ]
}
```

---

## 🤖 **AI Coaching**

### **POST /ai/coaching/message**
AI 코칭 메시지 요청

```json
// Request
{
  "context": "morning_motivation",
  "user_data": {
    "current_mood": 6,
    "energy_level": 7,
    "recent_habits": ["water", "meditation"],
    "challenges": ["time_management", "motivation"]
  },
  "message_type": "motivation" // motivation, advice, celebration, challenge
}

// Response (200 OK)
{
  "message": {
    "id": "message-uuid-1",
    "content": "좋은 아침이에요! 어제 물 마시기와 명상을 꾸준히 하신 모습이 정말 멋져요. 💪 오늘도 작은 성취부터 시작해보면 어떨까요?",
    "type": "motivation",
    "tone": "encouraging",
    "personalization_score": 0.95
  },
  "suggested_actions": [
    {
      "action": "check_habit",
      "habit_id": "habit-uuid-1",
      "message": "물 한 잔으로 하루를 시작해보세요!"
    }
  ],
  "follow_up_scheduled": "2025-06-11T15:00:00Z"
}
```

### **GET /ai/coaching/messages**
AI 코칭 메시지 히스토리

```json
// Query Parameters
?limit=20&offset=0&type=motivation

// Response (200 OK)
{
  "messages": [
    {
      "id": "message-uuid-1",
      "content": "좋은 아침이에요! 어제 물 마시기와...",
      "type": "motivation",
      "sent_at": "2025-06-11T09:00:00Z",
      "user_reaction": "like" // like, love, helpful, null
    }
  ],
  "total": 150,
  "has_more": true
}
```

### **POST /ai/coaching/feedback**
AI 메시지에 대한 피드백

```json
// Request
{
  "message_id": "message-uuid-1",
  "reaction": "helpful", // like, love, helpful, not_helpful
  "feedback": "정말 도움이 되었어요!"
}

// Response (200 OK)
{
  "status": "feedback_recorded",
  "message": "피드백이 기록되었습니다."
}
```

---

## 📊 **Analytics & Insights**

### **GET /users/me/analytics/summary**
사용자 분석 요약

```json
// Query Parameters
?period=week&start_date=2025-06-01&end_date=2025-06-11

// Response (200 OK)
{
  "period": {
    "start_date": "2025-06-01",
    "end_date": "2025-06-11",
    "type": "week"
  },
  "overall_stats": {
    "total_habits": 5,
    "active_habits": 4,
    "average_completion_rate": 0.78,
    "total_check_ins": 35,
    "longest_streak": 11
  },
  "mood_insights": {
    "average_mood": 7.2,
    "mood_trend": "improving", // improving, stable, declining
    "best_mood_day": "2025-06-09",
    "correlation_with_habits": {
      "exercise": 0.8,
      "meditation": 0.6
    }
  },
  "habit_performance": [
    {
      "habit_name": "물 마시기",
      "completion_rate": 0.91,
      "streak": 11,
      "trend": "stable"
    }
  ],
  "recommendations": [
    {
      "type": "habit_suggestion",
      "message": "운동 후 기분이 좋아지는 패턴이 보여요. 운동 시간을 늘려보는 건 어떨까요?",
      "confidence": 0.85
    }
  ]
}
```

### **GET /users/me/analytics/habits/{habit_id}**
특정 습관 상세 분석

```json
// Response (200 OK)
{
  "habit": {
    "id": "habit-uuid-1",
    "name": "물 마시기"
  },
  "performance": {
    "total_days": 30,
    "completed_days": 27,
    "completion_rate": 0.9,
    "current_streak": 11,
    "best_streak": 15,
    "average_daily_count": 7.5
  },
  "patterns": {
    "best_completion_time": "09:00",
    "best_day_of_week": "Monday",
    "success_factors": [
      "morning_routine",
      "high_energy_level"
    ]
  },
  "correlations": {
    "mood_correlation": 0.7,
    "energy_correlation": 0.8,
    "other_habits": [
      {
        "habit_name": "명상",
        "correlation": 0.6
      }
    ]
  }
}
```

---

## 💰 **Subscription & Payment**

### **GET /subscription/plans**
구독 플랜 목록

```json
// Response (200 OK)
{
  "plans": [
    {
      "id": "basic",
      "name": "Basic",
      "price": 0,
      "currency": "KRW",
      "billing_cycle": "monthly",
      "features": [
        "기본 습관 추적",
        "제한된 AI 코칭",
        "기본 분석"
      ],
      "limits": {
        "max_habits": 3,
        "ai_messages_per_day": 5
      }
    },
    {
      "id": "premium",
      "name": "Premium", 
      "price": 9900,
      "currency": "KRW",
      "billing_cycle": "monthly",
      "features": [
        "무제한 습관 추적",
        "무제한 AI 코칭",
        "상세 분석 및 인사이트",
        "웨어러블 연동"
      ],
      "limits": {
        "max_habits": -1,
        "ai_messages_per_day": -1
      }
    }
  ]
}
```

### **POST /subscription/subscribe**
구독 시작

```json
// Request
{
  "plan_id": "premium",
  "payment_method": "card",
  "payment_token": "portone-payment-token"
}

// Response (201 Created)
{
  "subscription": {
    "id": "sub-uuid-1",
    "plan_id": "premium",
    "status": "active",
    "started_at": "2025-06-11T12:00:00Z",
    "next_billing_date": "2025-07-11T12:00:00Z",
    "amount": 9900,
    "currency": "KRW"
  }
}
```

---

## 🔔 **Notifications**

### **POST /notifications/register**
푸시 알림 토큰 등록

```json
// Request
{
  "device_token": "fcm-device-token",
  "platform": "ios", // ios, android
  "app_version": "1.0.0"
}

// Response (200 OK)
{
  "status": "registered",
  "device_id": "device-uuid-1"
}
```

### **GET /notifications**
알림 목록

```json
// Response (200 OK)
{
  "notifications": [
    {
      "id": "notif-uuid-1",
      "title": "습관 체크인 시간이에요!",
      "body": "물 마시기 습관을 체크인해보세요.",
      "type": "habit_reminder",
      "read": false,
      "created_at": "2025-06-11T09:00:00Z",
      "data": {
        "habit_id": "habit-uuid-1",
        "action": "check_habit"
      }
    }
  ]
}
```

---

## 📁 **File Upload**

### **POST /upload/image**
이미지 업로드

```json
// Request (multipart/form-data)
file: <image-file>
type: "progress_photo" // progress_photo, avatar, habit_icon

// Response (201 Created)
{
  "url": "https://cdn.wellnessai.kr/images/uuid-filename.jpg",
  "thumbnail_url": "https://cdn.wellnessai.kr/images/thumbnails/uuid-filename.jpg",
  "file_size": 2048576,
  "mime_type": "image/jpeg"
}
```

---

## ❌ **Error Responses**

### **Error Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 데이터가 올바르지 않습니다.",
    "details": [
      {
        "field": "email",
        "message": "유효한 이메일 주소를 입력해주세요."
      }
    ],
    "request_id": "req-uuid-123"
  }
}
```

### **Common Error Codes**

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | 입력 데이터 유효성 검사 실패 |
| 401 | `UNAUTHORIZED` | 인증이 필요하거나 토큰이 유효하지 않음 |
| 403 | `FORBIDDEN` | 권한이 없음 |
| 404 | `NOT_FOUND` | 리소스를 찾을 수 없음 |
| 409 | `CONFLICT` | 리소스 충돌 (중복 이메일 등) |
| 429 | `RATE_LIMIT_EXCEEDED` | 요청 제한 초과 |
| 500 | `INTERNAL_ERROR` | 서버 내부 오류 |

---

## 📈 **API Versioning**

### **Version Strategy**
- **URL Versioning**: `/v1/`, `/v2/`
- **Backward Compatibility**: 최소 1년간 이전 버전 지원
- **Deprecation Notice**: 6개월 전 공지

### **Version History**
- **v1.0** (2025년 9월): 초기 MVP API
- **v1.1** (2025년 12월): 소셜 기능 추가
- **v2.0** (2026년 3월): 웨어러블 연동

---

## 🧪 **Testing**

### **Test Accounts**
```json
// 개발/스테이징 환경 테스트 계정
{
  "email": "test@wellnessai.kr",
  "password": "TestPassword123!",
  "subscription": "premium"
}
```

### **Mock Data**
- Postman Collection 제공
- Swagger UI에서 "Try it out" 기능
- 개발 환경에서 시드 데이터 자동 생성

---

**🎯 목표: 개발자 친화적이고 확장 가능한 API로 최고의 개발 경험 제공**