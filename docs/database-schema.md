# 🗄️ WellnessAI 데이터베이스 스키마

> **PostgreSQL 기반 데이터베이스 설계 문서**

---

## 📋 **스키마 개요**

### **Database Info**
- **Engine**: PostgreSQL 16.x
- **Character Set**: UTF-8
- **Timezone**: UTC (애플리케이션에서 로컬 시간으로 변환)
- **Connection Pool**: 10-50 connections

### **Naming Conventions**
- **Tables**: `snake_case` (예: `user_habits`)
- **Columns**: `snake_case` (예: `created_at`)
- **Indexes**: `idx_{table}_{column}` (예: `idx_users_email`)
- **Foreign Keys**: `fk_{table}_{column}` (예: `fk_user_habits_user_id`)

---

## 👥 **Users & Authentication**

### **users**
사용자 기본 정보

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL for social login only users
    name VARCHAR(100) NOT NULL,
    birth_year INTEGER,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    timezone VARCHAR(50) DEFAULT 'Asia/Seoul',
    
    -- Profile
    avatar_url TEXT,
    bio TEXT,
    
    -- Settings
    notification_settings JSONB DEFAULT '{}',
    privacy_settings JSONB DEFAULT '{}',
    
    -- Terms & Privacy
    agreed_to_terms BOOLEAN DEFAULT FALSE,
    agreed_to_privacy BOOLEAN DEFAULT FALSE,
    agreed_to_marketing BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);
```

### **user_social_accounts**
소셜 로그인 연결 정보

```sql
CREATE TABLE user_social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'kakao', 'naver', 'google', 'apple'
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_user_social_accounts_user_id ON user_social_accounts(user_id);
CREATE INDEX idx_user_social_accounts_provider ON user_social_accounts(provider);
```

### **user_sessions**
사용자 세션 관리

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
```

---

## 📝 **Habits Management**

### **habit_categories**
습관 카테고리

```sql
CREATE TABLE habit_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL, -- English name for future use
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7), -- Hex color code
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO habit_categories (name, name_en, icon, color) VALUES
('건강', 'health', 'heart', '#E53E3E'),
('운동', 'exercise', 'dumbbell', '#38A169'),
('마음챙김', 'mindfulness', 'brain', '#805AD5'),
('학습', 'learning', 'book', '#3182CE'),
('생산성', 'productivity', 'target', '#D69E2E'),
('관계', 'relationships', 'users', '#DD6B20'),
('창의성', 'creativity', 'palette', '#ED64A6');
```

### **habits**
습관 템플릿

```sql
CREATE TABLE habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES habit_categories(id),
    
    -- Metadata
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    estimated_time_minutes INTEGER, -- Estimated time in minutes
    default_frequency VARCHAR(20) DEFAULT 'daily', -- daily, weekly, custom
    default_target_count INTEGER DEFAULT 1,
    
    -- Visual
    icon VARCHAR(50),
    color VARCHAR(7),
    
    -- Instructions
    instructions JSONB, -- Step-by-step instructions
    tips JSONB, -- Tips for success
    
    -- Status
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_habits_category_id ON habits(category_id);
CREATE INDEX idx_habits_difficulty_level ON habits(difficulty_level);
CREATE INDEX idx_habits_is_featured ON habits(is_featured);
```

### **user_habits**
사용자가 추가한 습관

```sql
CREATE TABLE user_habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    habit_id UUID NOT NULL REFERENCES habits(id),
    
    -- Configuration
    target_frequency VARCHAR(20) DEFAULT 'daily', -- daily, weekly, custom
    target_count INTEGER DEFAULT 1,
    reminder_times JSONB DEFAULT '[]', -- Array of time strings ["09:00", "15:00"]
    
    -- Customization
    custom_name VARCHAR(200), -- User can override habit name
    notes TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    
    -- Stats (cached for performance)
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    total_completions INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paused_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, habit_id)
);

CREATE INDEX idx_user_habits_user_id ON user_habits(user_id);
CREATE INDEX idx_user_habits_status ON user_habits(status);
CREATE INDEX idx_user_habits_started_at ON user_habits(started_at);
```

### **habit_logs**
습관 체크인 기록

```sql
CREATE TABLE habit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_habit_id UUID NOT NULL REFERENCES user_habits(id) ON DELETE CASCADE,
    
    -- Completion data
    completed_count INTEGER NOT NULL DEFAULT 1,
    target_count INTEGER NOT NULL, -- Target count at the time of logging
    completed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Context
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    location VARCHAR(50), -- 'home', 'office', 'gym', etc.
    weather VARCHAR(50),
    
    -- User input
    notes TEXT,
    image_urls JSONB DEFAULT '[]', -- Progress photos
    
    -- Streak info (snapshot at time of logging)
    streak_count INTEGER NOT NULL DEFAULT 1,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_habit_logs_user_habit_id ON habit_logs(user_habit_id);
CREATE INDEX idx_habit_logs_completed_at ON habit_logs(completed_at);
CREATE INDEX idx_habit_logs_created_at ON habit_logs(created_at);
```

---

## 🤖 **AI Coaching**

### **coaching_messages**
AI 코칭 메시지

```sql
CREATE TABLE coaching_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Message content
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- 'motivation', 'advice', 'celebration', 'challenge', 'reminder'
    tone VARCHAR(50), -- 'encouraging', 'gentle', 'energetic', 'thoughtful'
    
    -- Context
    context JSONB, -- User context used to generate message
    personalization_score FLOAT, -- 0.0 to 1.0, how personalized the message is
    
    -- AI model info
    ai_model VARCHAR(50), -- 'gpt-4', 'gpt-3.5-turbo'
    prompt_version VARCHAR(20),
    
    -- User interaction
    user_reaction VARCHAR(20), -- 'like', 'love', 'helpful', 'not_helpful'
    user_feedback TEXT,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_coaching_messages_user_id ON coaching_messages(user_id);
CREATE INDEX idx_coaching_messages_sent_at ON coaching_messages(sent_at);
CREATE INDEX idx_coaching_messages_message_type ON coaching_messages(message_type);
```

### **ai_prompt_templates**
AI 프롬프트 템플릿

```sql
CREATE TABLE ai_prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    template TEXT NOT NULL, -- Jinja2 template
    variables JSONB, -- Required variables and their types
    version VARCHAR(20) NOT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 💰 **Subscription & Billing**

### **subscription_plans**
구독 플랜

```sql
CREATE TABLE subscription_plans (
    id VARCHAR(50) PRIMARY KEY, -- 'basic', 'premium', 'pro'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Pricing
    price INTEGER NOT NULL, -- Price in KRW cents (9900 KRW = 990000)
    currency VARCHAR(3) DEFAULT 'KRW',
    billing_cycle VARCHAR(20) NOT NULL, -- 'monthly', 'yearly'
    
    -- Features
    features JSONB NOT NULL,
    limits JSONB NOT NULL, -- Usage limits
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default plans
INSERT INTO subscription_plans (id, name, price, features, limits) VALUES
('basic', 'Basic', 0, '["기본 습관 추적", "제한된 AI 코칭"]', '{"max_habits": 3, "ai_messages_per_day": 5}'),
('premium', 'Premium', 990000, '["무제한 습관 추적", "무제한 AI 코칭", "상세 분석"]', '{"max_habits": -1, "ai_messages_per_day": -1}');
```

### **user_subscriptions**
사용자 구독 정보

```sql
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id VARCHAR(50) NOT NULL REFERENCES subscription_plans(id),
    
    -- Subscription status
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'canceled', 'expired', 'pending')),
    
    -- Billing
    amount INTEGER NOT NULL, -- Amount paid in currency cents
    currency VARCHAR(3) DEFAULT 'KRW',
    
    -- Dates
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    canceled_at TIMESTAMP WITH TIME ZONE,
    
    -- Payment gateway info
    payment_gateway VARCHAR(50), -- 'portone', 'stripe'
    external_subscription_id VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
```

### **payment_transactions**
결제 거래 기록

```sql
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    subscription_id UUID REFERENCES user_subscriptions(id),
    
    -- Transaction info
    transaction_type VARCHAR(20) NOT NULL, -- 'payment', 'refund', 'chargeback'
    status VARCHAR(20) NOT NULL, -- 'pending', 'completed', 'failed', 'canceled'
    
    -- Amount
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'KRW',
    
    -- Payment gateway
    payment_gateway VARCHAR(50) NOT NULL,
    gateway_transaction_id VARCHAR(255),
    payment_method VARCHAR(50), -- 'card', 'transfer', 'virtual_account'
    
    -- Metadata
    gateway_response JSONB,
    failure_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_status ON payment_transactions(status);
```

---

## 🏆 **Achievements & Gamification**

### **achievements**
성취/배지 정의

```sql
CREATE TABLE achievements (
    id VARCHAR(50) PRIMARY KEY, -- 'first_week', 'streak_30', 'early_bird'
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    
    -- Visual
    icon VARCHAR(50) NOT NULL,
    color VARCHAR(7),
    rarity VARCHAR(20) DEFAULT 'common', -- 'common', 'rare', 'epic', 'legendary'
    
    -- Criteria
    criteria JSONB NOT NULL, -- Conditions to unlock
    points INTEGER DEFAULT 0, -- Points awarded
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **user_achievements**
사용자가 획득한 성취

```sql
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id VARCHAR(50) NOT NULL REFERENCES achievements(id),
    
    -- Context when earned
    context JSONB, -- What triggered the achievement
    points_earned INTEGER DEFAULT 0,
    
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_earned_at ON user_achievements(earned_at);
```

---

## 🔔 **Notifications**

### **notification_devices**
사용자 디바이스 정보

```sql
CREATE TABLE notification_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Device info
    device_token VARCHAR(500) NOT NULL UNIQUE,
    platform VARCHAR(20) NOT NULL, -- 'ios', 'android', 'web'
    app_version VARCHAR(20),
    device_model VARCHAR(100),
    os_version VARCHAR(50),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notification_devices_user_id ON notification_devices(user_id);
CREATE INDEX idx_notification_devices_platform ON notification_devices(platform);
```

### **notifications**
알림 메시지

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'habit_reminder', 'achievement', 'coaching', 'system'
    
    -- Targeting
    target_platform VARCHAR(20), -- If null, send to all platforms
    
    -- Data payload
    data JSONB, -- Additional data for deep linking
    
    -- Status
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    
    -- Delivery info
    delivery_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
    failure_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_scheduled_for ON notifications(scheduled_for);
CREATE INDEX idx_notifications_notification_type ON notifications(notification_type);
```

---

## 📊 **Analytics & Insights**

### **user_analytics**
사용자 분석 데이터 (일일 집계)

```sql
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Daily stats
    total_habits INTEGER DEFAULT 0,
    completed_habits INTEGER DEFAULT 0,
    completion_rate FLOAT DEFAULT 0.0,
    
    -- Mood & energy
    avg_mood_score FLOAT,
    avg_energy_level FLOAT,
    
    -- Engagement
    app_opens INTEGER DEFAULT 0,
    session_duration_minutes INTEGER DEFAULT 0,
    ai_messages_received INTEGER DEFAULT 0,
    
    -- Streaks
    active_streaks INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, date)
);

CREATE INDEX idx_user_analytics_user_id_date ON user_analytics(user_id, date);
```

### **app_events**
앱 사용 이벤트 로깅

```sql
CREATE TABLE app_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Event info
    event_type VARCHAR(100) NOT NULL, -- 'app_open', 'habit_check', 'ai_message_read'
    event_data JSONB,
    
    -- Context
    session_id UUID,
    screen_name VARCHAR(100),
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamps
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_app_events_user_id ON app_events(user_id);
CREATE INDEX idx_app_events_event_type ON app_events(event_type);
CREATE INDEX idx_app_events_occurred_at ON app_events(occurred_at);
```

---

## 📁 **File Storage**

### **uploaded_files**
업로드된 파일 메타데이터

```sql
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- File info
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- Storage
    storage_provider VARCHAR(50) DEFAULT 'aws_s3', -- 'aws_s3', 'cloudinary'
    storage_path TEXT NOT NULL,
    url TEXT NOT NULL,
    thumbnail_url TEXT,
    
    -- Context
    upload_context VARCHAR(100), -- 'avatar', 'habit_log', 'progress_photo'
    related_entity_id UUID, -- ID of related entity (habit_log, etc.)
    
    -- Status
    is_processed BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX idx_uploaded_files_upload_context ON uploaded_files(upload_context);
```

---

## 🔗 **Database Relationships**

### **Key Relationships**

```sql
-- User -> User Habits (1:N)
-- User -> Habit Logs (1:N through User Habits)
-- User -> Coaching Messages (1:N)
-- User -> Subscription (1:1 current)
-- User -> Achievements (M:N through User Achievements)
-- User -> Notifications (1:N)

-- Habit Category -> Habits (1:N)
-- Habit -> User Habits (1:N)
-- User Habit -> Habit Logs (1:N)
```

---

## 📈 **Performance Optimizations**

### **Partitioning**

```sql
-- Partition habit_logs by month for better performance
CREATE TABLE habit_logs_y2025m06 PARTITION OF habit_logs
FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

-- Partition app_events by month
CREATE TABLE app_events_y2025m06 PARTITION OF app_events  
FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
```

### **Materialized Views**

```sql
-- User statistics summary
CREATE MATERIALIZED VIEW user_stats_summary AS
SELECT 
    u.id,
    u.name,
    COUNT(uh.id) as total_habits,
    AVG(uh.current_streak) as avg_streak,
    SUM(uh.total_completions) as total_completions
FROM users u
LEFT JOIN user_habits uh ON u.id = uh.user_id
WHERE u.is_active = true
GROUP BY u.id, u.name;

-- Refresh materialized view daily
CREATE INDEX idx_user_stats_summary_id ON user_stats_summary(id);
```

### **Caching Strategy**

```sql
-- Cache frequently accessed data in Redis:
-- user:{user_id}:profile (1 hour TTL)
-- user:{user_id}:habits (30 minutes TTL)  
-- user:{user_id}:dashboard (15 minutes TTL)
-- habits:featured (1 day TTL)
-- plans:active (1 day TTL)
```

---

## 🔒 **Security & Privacy**

### **Data Encryption**
- **PII Fields**: email, name 등 개인정보는 application level encryption
- **Sensitive Data**: password_hash, tokens 등은 강력한 해싱/암호화
- **File Storage**: S3에서 encryption at rest

### **Data Retention**
```sql
-- Data retention policies
-- Delete old app_events after 1 year
-- Anonymize deleted user data after 30 days
-- Keep aggregated analytics data indefinitely

-- Example retention job
DELETE FROM app_events 
WHERE occurred_at < NOW() - INTERVAL '1 year';
```

### **Audit Trail**
```sql
-- Add audit fields to sensitive tables
ALTER TABLE users ADD COLUMN updated_by UUID;
ALTER TABLE user_subscriptions ADD COLUMN updated_by UUID;

-- Create audit log table for critical operations
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    user_id UUID,
    ip_address INET,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🧪 **Test Data**

### **Seed Data Script**
```sql
-- Insert test categories and habits
-- Insert test users with various subscription levels
-- Insert sample habit logs with patterns
-- Insert AI coaching messages
-- Insert achievements and user achievements

-- This helps with development and testing
```

---

**🎯 목표: 확장 가능하고 성능 최적화된 데이터베이스로 안정적인 서비스 제공**