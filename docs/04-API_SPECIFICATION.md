# 🔌 WellnessAI API 명세서

> **FastAPI 기반 RESTful API 상세 명세**

---

## 📋 **API 개요**

### **Base URL**
```
Development: https://api-dev.wellnessai.kr/v1
Production:  https://api.wellnessai.kr/v1
```

### **인증 방식**
- **JWT Bearer Token** (Access Token)
- **Refresh Token** 자동 갱신
- **OAuth 2.0** (카카오, 네이버, 구글)

### **공통 응답 형식**
```json
{
  "success": true,
  "data": {...},
  "message": "성공 메시지",
  "timestamp": "2025-06-11T13:00:00Z"
}

// 에러 응답
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다.",
    "details": {...}
  },
  "timestamp": "2025-06-11T13:00:00Z"
}
```

### **HTTP 상태 코드**
- `200` OK - 성공
- `201` Created - 생성 성공
- `400` Bad Request - 잘못된 요청
- `401` Unauthorized - 인증 필요
- `403` Forbidden - 권한 없음
- `404` Not Found - 리소스 없음
- `422` Unprocessable Entity - 유효성 검사 실패
- `429` Too Many Requests - 요청 제한 초과
- `500` Internal Server Error - 서버 오류

---

## 🔐 **1. Authentication API**

### **1.1 소셜 로그인**

#### **카카오 로그인**
```http
POST /auth/kakao/login
Content-Type: application/json

{
  "access_token": "카카오_액세스_토큰",
  "device_info": {
    "device_id": "unique_device_id",
    "device_type": "ios|android",
    "os_version": "iOS 17.0",
    "app_version": "1.0.0"
  }
}
```

**응답**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_string",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_uuid",
      "email": "user@example.com",
      "nickname": "사용자",
      "profile_image_url": "https://...",
      "is_new_user": true
    }
  }
}
```

#### **토큰 갱신**
```http
POST /auth/refresh
Authorization: Bearer {refresh_token}
```

#### **로그아웃**
```http
POST /auth/logout
Authorization: Bearer {access_token}

{
  "device_id": "unique_device_id"
}
```

### **1.2 토큰 검증**
```http
GET /auth/me
Authorization: Bearer {access_token}
```

---

## 👤 **2. Users API**

### **2.1 사용자 프로필 조회**
```http
GET /users/profile
Authorization: Bearer {access_token}
```

**응답**
```json
{
  "success": true,
  "data": {
    "id": "user_uuid",
    "email": "user@example.com",
    "nickname": "현아",
    "profile_image_url": "https://...",
    "birth_year": 1995,
    "gender": "female",
    "timezone": "Asia/Seoul",
    "wellness_profile": {
      "fitness_level": "beginner",
      "primary_goals": ["weight_management", "stress_relief"],
      "available_time_slots": [
        {"day": "monday", "start_time": "12:00", "end_time": "13:00"}
      ],
      "health_conditions": ["none"]
    },
    "subscription": {
      "plan": "basic",
      "expires_at": null,
      "features": ["basic_tracking", "limited_ai_coaching"]
    },
    "created_at": "2025-06-01T09:00:00Z",
    "updated_at": "2025-06-11T13:00:00Z"
  }
}
```

### **2.2 프로필 업데이트**
```http
PUT /users/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nickname": "새로운닉네임",
  "birth_year": 1995,
  "wellness_profile": {
    "fitness_level": "intermediate",
    "primary_goals": ["weight_management", "sleep_improvement"],
    "available_time_slots": [...]
  }
}
```

### **2.3 사용자 삭제 (탈퇴)**
```http
DELETE /users/profile
Authorization: Bearer {access_token}

{
  "reason": "사용하지 않음",
  "feedback": "선택적 피드백"
}
```

---

## 📝 **3. Habits API**

### **3.1 습관 카테고리 목록**
```http
GET /habits/categories
```

**응답**
```json
{
  "success": true,
  "data": [
    {
      "id": "category_uuid",
      "name": "운동",
      "icon": "💪",
      "color_code": "#34C759",
      "subcategories": [
        {
          "id": "sub_uuid",
          "name": "유산소",
          "icon": "🏃‍♀️"
        }
      ]
    }
  ]
}
```

### **3.2 습관 템플릿 목록**
```http
GET /habits/templates
Query Parameters:
- category_id: string (optional)
- difficulty_level: integer (optional, 1-5)
- search: string (optional)
- limit: integer (default: 20)
- offset: integer (default: 0)
```

**응답**
```json
{
  "success": true,
  "data": {
    "habits": [
      {
        "id": "template_uuid",
        "name": "물 8잔 마시기",
        "description": "하루 2L 물 섭취로 건강한 수분 보충",
        "category": {
          "id": "category_uuid",
          "name": "영양"
        },
        "difficulty_level": 2,
        "estimated_time_minutes": 0,
        "recommended_frequency": {
          "type": "daily",
          "count": 8
        },
        "success_criteria": "하루 8잔의 물을 마시기",
        "tips": ["아침에 물 한 잔으로 시작", "식사 전 물 마시기"],
        "compatibility_score": 0.85
      }
    ],
    "total_count": 150,
    "has_next": true
  }
}
```

### **3.3 사용자 습관 목록**
```http
GET /users/habits
Authorization: Bearer {access_token}
Query Parameters:
- status: string (active|inactive|all, default: active)
- category_id: string (optional)
```

**응답**
```json
{
  "success": true,
  "data": [
    {
      "id": "user_habit_uuid",
      "habit_template": {
        "id": "template_uuid",
        "name": "물 8잔 마시기",
        "category": {...}
      },
      "custom_name": null,
      "target_frequency": {
        "type": "daily",
        "count": 8,
        "specific_days": null
      },
      "reminder_settings": {
        "enabled": true,
        "times": ["08:00", "12:00", "16:00", "20:00"]
      },
      "current_streak": 7,
      "longest_streak": 12,
      "total_completions": 45,
      "is_active": true,
      "created_at": "2025-06-01T09:00:00Z"
    }
  ]
}
```

### **3.4 습관 추가**
```http
POST /users/habits
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "habit_template_id": "template_uuid",
  "custom_name": "나만의 물 마시기",
  "target_frequency": {
    "type": "daily",
    "count": 6
  },
  "reminder_settings": {
    "enabled": true,
    "times": ["09:00", "13:00", "17:00"]
  }
}
```

### **3.5 습관 수정**
```http
PUT /users/habits/{habit_id}
Authorization: Bearer {access_token}
```

### **3.6 습관 삭제**
```http
DELETE /users/habits/{habit_id}
Authorization: Bearer {access_token}
```

---

## 📊 **4. Tracking API**

### **4.1 오늘의 습관 현황**
```http
GET /tracking/today
Authorization: Bearer {access_token}
Query Parameters:
- date: string (YYYY-MM-DD, optional, default: today)
```

**응답**
```json
{
  "success": true,
  "data": {
    "date": "2025-06-11",
    "overall_completion_rate": 0.6,
    "total_habits": 5,
    "completed_habits": 3,
    "habits": [
      {
        "user_habit_id": "habit_uuid",
        "habit_name": "물 8잔 마시기",
        "target": 8,
        "completed": 6,
        "completion_rate": 0.75,
        "status": "in_progress",
        "next_reminder": "16:00",
        "logs": [
          {
            "id": "log_uuid",
            "logged_at": "2025-06-11T08:00:00Z",
            "completion_percentage": 100,
            "notes": "아침 물 한 잔"
          }
        ]
      }
    ],
    "mood_average": 7.5,
    "ai_insights": [
      "오늘 물 섭취량이 목표에 가까워요! 💪",
      "점심 시간에 산책을 추천드려요 🚶‍♀️"
    ]
  }
}
```

### **4.2 습관 체크인**
```http
POST /tracking/checkin
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

{
  "user_habit_id": "habit_uuid",
  "completion_status": "completed",
  "completion_percentage": 100,
  "duration_minutes": 15,
  "intensity_level": 3,
  "mood_before": 6,
  "mood_after": 8,
  "notes": "공원에서 15분 산책했어요!",
  "location": "올림픽공원",
  "evidence_file": (파일 업로드, optional)
}
```

**응답**
```json
{
  "success": true,
  "data": {
    "log_id": "log_uuid",
    "streak_updated": true,
    "new_streak": 8,
    "points_earned": 50,
    "achievements_unlocked": [
      {
        "id": "streak_7",
        "name": "일주일 챌린지",
        "description": "7일 연속 달성!"
      }
    ],
    "ai_response": "훌륭해요! 꾸준히 하고 계시네요 🎉"
  }
}
```

### **4.3 습관 로그 수정**
```http
PUT /tracking/logs/{log_id}
Authorization: Bearer {access_token}
```

### **4.4 습관 로그 삭제**
```http
DELETE /tracking/logs/{log_id}
Authorization: Bearer {access_token}
```

### **4.5 진척도 조회**
```http
GET /tracking/progress
Authorization: Bearer {access_token}
Query Parameters:
- habit_id: string (optional, 특정 습관)
- period: string (week|month|year, default: week)
- start_date: string (YYYY-MM-DD)
- end_date: string (YYYY-MM-DD)
```

---

## 🤖 **5. AI Coaching API**

### **5.1 AI 코칭 메시지 요청**
```http
POST /ai/coaching/message
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message_type": "habit_reminder",
  "context": {
    "habit_id": "habit_uuid",
    "current_mood": 7,
    "current_situation": "점심시간",
    "weather": "맑음"
  },
  "user_message": "오늘 운동하기 싫어요" // optional
}
```

**응답**
```json
{
  "success": true,
  "data": {
    "message_id": "message_uuid",
    "content": "이해해요! 그럴 때는 가벼운 스트레칭 5분부터 시작해보는 건 어떨까요? 😊",
    "message_type": "encouragement",
    "suggestions": [
      {
        "text": "5분 스트레칭",
        "action": "start_habit",
        "habit_id": "stretch_habit_id"
      },
      {
        "text": "내일 하기",
        "action": "reschedule"
      }
    ],
    "tone": "친근함",
    "created_at": "2025-06-11T13:00:00Z"
  }
}
```

### **5.2 AI 채팅**
```http
POST /ai/chat
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message": "오늘 스트레스를 많이 받았어요",
  "context": {
    "current_mood": 4,
    "recent_activities": ["work", "meeting"],
    "time_of_day": "evening"
  }
}
```

### **5.3 개인화 코칭 설정**
```http
PUT /ai/coaching/settings
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "communication_style": "friendly", // friendly|professional|casual
  "coaching_frequency": "normal", // low|normal|high
  "motivation_type": "positive", // positive|challenge|gentle
  "preferred_message_times": ["09:00", "12:00", "18:00"]
}
```

### **5.4 AI 메시지 히스토리**
```http
GET /ai/messages
Authorization: Bearer {access_token}
Query Parameters:
- limit: integer (default: 20)
- offset: integer (default: 0)
- message_type: string (optional)
```

---

## 📈 **6. Analytics API**

### **6.1 개인 대시보드 데이터**
```http
GET /analytics/dashboard
Authorization: Bearer {access_token}
Query Parameters:
- period: string (week|month|year, default: week)
```

**응답**
```json
{
  "success": true,
  "data": {
    "period": "week",
    "start_date": "2025-06-05",
    "end_date": "2025-06-11",
    "wellness_score": 85,
    "score_change": 12,
    "habit_completion_rate": 0.72,
    "consistency_score": 0.68,
    "improvement_trend": 0.15,
    "habit_stats": [
      {
        "habit_id": "habit_uuid",
        "habit_name": "물 마시기",
        "completion_rate": 0.9,
        "current_streak": 12,
        "total_completions": 6
      }
    ],
    "mood_trend": {
      "average": 7.2,
      "trend": "improving",
      "data_points": [
        {"date": "2025-06-05", "mood": 6.5},
        {"date": "2025-06-06", "mood": 7.0}
      ]
    },
    "achievements": [
      {
        "id": "streak_7",
        "name": "일주일 챌린지",
        "unlocked_at": "2025-06-11T10:00:00Z"
      }
    ]
  }
}
```

### **6.2 주간/월간 리포트**
```http
GET /analytics/report
Authorization: Bearer {access_token}
Query Parameters:
- type: string (weekly|monthly)
- date: string (YYYY-MM-DD, 기준일)
```

### **6.3 습관별 상세 분석**
```http
GET /analytics/habits/{habit_id}/details
Authorization: Bearer {access_token}
Query Parameters:
- period: string (month|quarter|year)
```

### **6.4 인사이트 생성**
```http
POST /analytics/insights
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "analysis_type": "habit_optimization", // habit_optimization|mood_correlation|pattern_analysis
  "habits": ["habit_uuid1", "habit_uuid2"], // optional
  "period_days": 30
}
```

---

## 🔔 **7. Notifications API**

### **7.1 알림 설정 조회**
```http
GET /notifications/settings
Authorization: Bearer {access_token}
```

**응답**
```json
{
  "success": true,
  "data": {
    "push_notifications": {
      "enabled": true,
      "habit_reminders": true,
      "ai_coaching": true,
      "achievement_alerts": true,
      "weekly_reports": false
    },
    "email_notifications": {
      "enabled": true,
      "weekly_reports": true,
      "achievement_certificates": true,
      "account_updates": true
    },
    "notification_schedule": {
      "quiet_hours": {
        "start": "22:00",
        "end": "08:00"
      },
      "weekend_settings": "same_as_weekday"
    }
  }
}
```

### **7.2 알림 설정 업데이트**
```http
PUT /notifications/settings
Authorization: Bearer {access_token}
```

### **7.3 디바이스 토큰 등록**
```http
POST /notifications/devices
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "device_token": "fcm_device_token",
  "platform": "ios", // ios|android
  "device_id": "unique_device_id"
}
```

### **7.4 알림 히스토리**
```http
GET /notifications/history
Authorization: Bearer {access_token}
Query Parameters:
- limit: integer (default: 20)
- offset: integer (default: 0)
- type: string (optional)
```

---

## 💳 **8. Payments API**

### **8.1 구독 플랜 목록**
```http
GET /payments/plans
```

**응답**
```json
{
  "success": true,
  "data": [
    {
      "id": "basic",
      "name": "Basic",
      "price_monthly": 0,
      "price_yearly": 0,
      "features": [
        "최대 3개 습관",
        "기본 AI 코칭 (일 3회)",
        "기본 통계"
      ],
      "ai_message_limit": 3,
      "is_current": true
    },
    {
      "id": "premium",
      "name": "Premium",
      "price_monthly": 9900,
      "price_yearly": 99000,
      "features": [
        "무제한 습관",
        "무제한 AI 코칭",
        "상세 분석 리포트",
        "웨어러블 연동"
      ],
      "ai_message_limit": null,
      "discount_rate": 16
    }
  ]
}
```

### **8.2 결제 정보**
```http
POST /payments/checkout
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "plan_id": "premium",
  "billing_cycle": "monthly", // monthly|yearly
  "payment_method": "iamport",
  "promo_code": "WELCOME50" // optional
}
```

**응답**
```json
{
  "success": true,
  "data": {
    "payment_id": "payment_uuid",
    "merchant_uid": "order_id_1234567890",
    "amount": 4950, // 할인 적용된 금액
    "original_amount": 9900,
    "currency": "KRW",
    "iamport_config": {
      "pg": "kakaopay",
      "pay_method": "card",
      "merchant_uid": "order_id_1234567890",
      "name": "WellnessAI Premium 구독",
      "amount": 4950,
      "buyer_email": "user@example.com",
      "buyer_name": "사용자"
    }
  }
}
```

### **8.3 결제 완료 처리**
```http
POST /payments/complete
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "payment_id": "payment_uuid",
  "imp_uid": "imp_1234567890",
  "merchant_uid": "order_id_1234567890"
}
```

### **8.4 구독 상태 조회**
```http
GET /payments/subscription
Authorization: Bearer {access_token}
```

### **8.5 구독 취소**
```http
POST /payments/subscription/cancel
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reason": "만족하지 않음",
  "feedback": "기능이 부족해요"
}
```

---

## 🛠️ **9. Admin API (관리자용)**

### **9.1 사용자 관리**
```http
GET /admin/users
Authorization: Bearer {admin_access_token}
Query Parameters:
- page: integer (default: 1)
- limit: integer (default: 50)
- search: string (email or nickname)
- subscription: string (basic|premium|pro)
- status: string (active|inactive)
```

### **9.2 시스템 통계**
```http
GET /admin/statistics
Authorization: Bearer {admin_access_token}
Query Parameters:
- period: string (day|week|month)
- date: string (YYYY-MM-DD)
```

### **9.3 AI 코칭 로그**
```http
GET /admin/ai/logs
Authorization: Bearer {admin_access_token}
Query Parameters:
- user_id: string (optional)
- date_from: string (YYYY-MM-DD)
- date_to: string (YYYY-MM-DD)
```

---

## 🚀 **실시간 기능 (WebSocket)**

### **실시간 알림**
```
WebSocket Endpoint: wss://api.wellnessai.kr/v1/ws/notifications

Connection:
- Authentication: JWT token in query parameter
- Protocols: WebSocket

Message Types:
- habit_reminder
- ai_coaching_message
- achievement_unlocked
- streak_milestone
```

---

## 📊 **Rate Limiting**

### **기본 제한**
- **인증된 사용자**: 1000 requests/hour
- **Premium 사용자**: 2000 requests/hour
- **AI API**: 50 requests/hour (Basic), 무제한 (Premium)

### **제한 헤더**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1623456789
```

---

## 🔧 **개발자 도구**

### **API 문서**
- **Swagger UI**: `https://api.wellnessai.kr/docs`
- **ReDoc**: `https://api.wellnessai.kr/redoc`
- **OpenAPI JSON**: `https://api.wellnessai.kr/openapi.json`

### **테스트 환경**
- **개발 서버**: `https://api-dev.wellnessai.kr/v1`
- **테스트 계정**: 개발자에게 문의

### **SDK (추후 제공)**
- **JavaScript/TypeScript SDK**
- **React Native SDK**
- **Swift SDK**
- **Kotlin SDK**

---

**🎯 목표: 개발하기 쉽고 확장 가능한 RESTful API 제공**