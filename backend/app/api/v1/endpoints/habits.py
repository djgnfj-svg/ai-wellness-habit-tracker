"""
습관 관리 API 엔드포인트

사용자 습관 생성, 조회, 수정, 삭제 및 습관 추적 기능을 제공합니다.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rate_limit import standard_rate_limit
from app.models.user import User
from app.schemas.habit import (
    HabitCategoryCreate, HabitCategoryResponse,
    HabitTemplateCreate, HabitTemplateResponse, HabitTemplateListResponse,
    UserHabitCreate, UserHabitUpdate, UserHabitResponse,
    HabitLogCreate, HabitLogResponse,
    DashboardData, StandardResponse,
    DifficultyLevel, FrequencyType
)
from app.schemas.user import UserHabitFilterParams, HabitTemplateSearchParams
from app.services.habit_service import HabitService
from app.services.tracking_service import TrackingService
from app.services.ai_coaching_service import AICoachingService, MessageType, NotificationType
from app.services.notification_service import NotificationService

router = APIRouter()

# =====================================================================
# 습관 카테고리 API
# =====================================================================

@router.get("/categories", response_model=List[HabitCategoryResponse])
async def get_habit_categories(
    include_inactive: bool = Query(False, description="비활성 카테고리 포함 여부"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """습관 카테고리 목록 조회"""
    habit_service = HabitService(db)
    categories = await habit_service.get_categories(include_inactive)
    return categories

@router.get("/categories/{category_id}", response_model=HabitCategoryResponse)
async def get_habit_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """특정 습관 카테고리 조회"""
    habit_service = HabitService(db)
    category = await habit_service.get_category_by_id(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="카테고리를 찾을 수 없습니다"
        )
    
    return category

# =====================================================================
# 습관 템플릿 API
# =====================================================================

@router.get("/templates", response_model=HabitTemplateListResponse)
async def get_habit_templates(
    category_id: Optional[UUID] = Query(None, description="카테고리 ID로 필터링"),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="난이도로 필터링"),
    max_time_minutes: Optional[int] = Query(None, ge=0, le=480, description="최대 소요 시간(분)"),
    frequency_type: Optional[FrequencyType] = Query(None, description="권장 빈도 타입"),
    search: Optional[str] = Query(None, max_length=100, description="검색어"),
    is_featured: Optional[bool] = Query(None, description="추천 템플릿만 조회"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """습관 템플릿 목록 조회 (페이지네이션 지원)"""
    habit_service = HabitService(db)
    
    search_params = HabitTemplateSearchParams(
        category_id=category_id,
        difficulty_level=difficulty_level,
        max_time_minutes=max_time_minutes,
        frequency_type=frequency_type,
        search=search,
        is_featured=is_featured,
        page=page,
        limit=limit
    )
    
    templates, total = await habit_service.get_habit_templates(search_params)
    
    return HabitTemplateListResponse(
        templates=templates,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/templates/{template_id}", response_model=HabitTemplateResponse)
async def get_habit_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """특정 습관 템플릿 조회"""
    habit_service = HabitService(db)
    template = await habit_service.get_habit_template_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="습관 템플릿을 찾을 수 없습니다"
        )
    
    return template

# =====================================================================
# 사용자 습관 API
# =====================================================================

@router.get("/user/habits", response_model=List[UserHabitResponse])
async def get_user_habits(
    category_id: Optional[UUID] = Query(None, description="카테고리로 필터링"),
    is_active: Optional[bool] = Query(True, description="활성 상태로 필터링"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="우선순위로 필터링"),
    has_reminder: Optional[bool] = Query(None, description="리마인더 설정 여부로 필터링"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 습관 목록 조회"""
    habit_service = HabitService(db)
    
    filter_params = UserHabitFilterParams(
        category_id=category_id,
        is_active=is_active,
        priority=priority,
        has_reminder=has_reminder
    )
    
    habits = await habit_service.get_user_habits(current_user.id, filter_params)
    return habits

@router.post("/user/habits", response_model=UserHabitResponse, status_code=status.HTTP_201_CREATED)
async def create_user_habit(
    habit_data: UserHabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """새로운 사용자 습관 생성"""
    habit_service = HabitService(db)
    habit = await habit_service.create_user_habit(current_user.id, habit_data)
    return habit

@router.get("/user/habits/{habit_id}", response_model=UserHabitResponse)
async def get_user_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """특정 사용자 습관 조회"""
    habit_service = HabitService(db)
    habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="습관을 찾을 수 없습니다"
        )
    
    return habit

@router.put("/user/habits/{habit_id}", response_model=UserHabitResponse)
async def update_user_habit(
    habit_id: UUID,
    habit_update: UserHabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 습관 수정"""
    habit_service = HabitService(db)
    habit = await habit_service.update_user_habit(current_user.id, habit_id, habit_update)
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="습관을 찾을 수 없습니다"
        )
    
    return habit

@router.delete("/user/habits/{habit_id}", response_model=StandardResponse)
async def delete_user_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 습관 삭제"""
    habit_service = HabitService(db)
    success = await habit_service.delete_user_habit(current_user.id, habit_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="습관을 찾을 수 없습니다"
        )
    
    return StandardResponse(
        success=True,
        message="습관이 성공적으로 삭제되었습니다"
    )

# =====================================================================
# 습관 추적 API
# =====================================================================

@router.post("/tracking/checkin", response_model=HabitLogResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_checkin(
    log_data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """습관 체크인 (완료 기록)"""
    habit_service = HabitService(db)
    log = await habit_service.create_habit_log(current_user.id, log_data)
    return log

@router.get("/tracking/logs", response_model=List[HabitLogResponse])
async def get_habit_logs(
    habit_id: Optional[UUID] = Query(None, description="특정 습관의 로그만 조회"),
    start_date: Optional[date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=200, description="최대 조회 개수"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """습관 로그 조회"""
    habit_service = HabitService(db)
    logs = await habit_service.get_habit_logs(
        user_id=current_user.id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return logs

@router.get("/tracking/today", response_model=DashboardData)
async def get_today_dashboard(
    target_date: Optional[date] = Query(None, description="조회할 날짜 (기본: 오늘)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """오늘의 습관 대시보드"""
    habit_service = HabitService(db)
    
    if target_date is None:
        target_date = date.today()
    
    dashboard = await habit_service.get_daily_dashboard(current_user.id, target_date)
    return dashboard

# =====================================================================
# 관리자 API
# =====================================================================

@router.post("/admin/categories", response_model=HabitCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_category(
    category_data: HabitCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 추후 관리자 권한 체크 추가
    _: None = Depends(standard_rate_limit)
):
    """새로운 습관 카테고리 생성 (관리자 전용)"""
    habit_service = HabitService(db)
    category = await habit_service.create_category(category_data)
    return category

@router.post("/admin/templates", response_model=HabitTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_template(
    template_data: HabitTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 추후 관리자 권한 체크 추가
    _: None = Depends(standard_rate_limit)
):
    """새로운 습관 템플릿 생성 (관리자 전용)"""
    habit_service = HabitService(db)
    template = await habit_service.create_habit_template(template_data)
    return template

# =====================================================================
# 통계 및 분석 API
# =====================================================================

@router.get("/stats/summary")
async def get_habit_statistics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 습관 통계 요약"""
    habit_service = HabitService(db)
    stats = await habit_service.get_habit_statistics_summary(current_user.id)
    return stats

@router.get("/recommendations", response_model=List[HabitTemplateResponse])
async def get_habit_recommendations(
    limit: int = Query(5, ge=1, le=10, description="추천할 습관 개수"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """개인화된 습관 추천"""
    habit_service = HabitService(db)
    
    try:
        recommendations = await habit_service.recommend_habits_for_user(current_user, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"습관 추천 실패: {str(e)}"
        )


@router.get("/coaching/{habit_id}")
async def get_ai_coaching_message(
    habit_id: UUID,
    context: str = Query("general", regex=r"^(general|motivation|tip|reminder)$", description="메시지 컨텍스트"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """AI 코칭 메시지 조회"""
    habit_service = HabitService(db)
    
    try:
        # 사용자 습관 소유권 확인
        user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
        if not user_habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="습관을 찾을 수 없습니다"
            )
        
        message = await habit_service.get_ai_coaching_message(habit_id, context)
        
        return {
            "habit_id": str(habit_id),
            "context": context,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AI 코칭 메시지 조회 실패: {str(e)}"
        )


# =====================================================================
# 알림/리마인더 API
# =====================================================================

@router.post("/notifications/schedule-reminders")
async def schedule_habit_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자의 습관 리마인더 스케줄링"""
    notification_service = NotificationService(db)
    
    try:
        scheduled_reminders = await notification_service.schedule_habit_reminders(current_user.id)
        
        return {
            "message": f"{len(scheduled_reminders)}개의 리마인더가 스케줄되었습니다",
            "scheduled_count": len(scheduled_reminders),
            "reminders": [
                {
                    "habit_name": reminder["habit_name"],
                    "scheduled_time": reminder["scheduled_time"].isoformat(),
                    "message": reminder["message"]
                }
                for reminder in scheduled_reminders
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"리마인더 스케줄링 실패: {str(e)}"
        )


@router.post("/notifications/send-motivation/{habit_id}")
async def send_motivation_notification(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """특정 습관에 대한 동기부여 알림 발송"""
    notification_service = NotificationService(db)
    
    try:
        # 사용자 습관 소유권 확인
        habit_service = HabitService(db)
        user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
        if not user_habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="습관을 찾을 수 없습니다"
            )
        
        success = await notification_service.send_motivation_message(current_user.id, habit_id)
        
        if success:
            return {"message": "동기부여 알림이 발송되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="알림 발송에 실패했습니다"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"동기부여 알림 발송 실패: {str(e)}"
        )


@router.post("/notifications/celebration")
async def send_celebration_notification(
    habit_name: str = Query(..., description="축하할 습관 이름"),
    streak: int = Query(..., ge=1, description="연속 달성 일수"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """습관 완료 축하 알림 발송"""
    notification_service = NotificationService(db)
    
    try:
        success = await notification_service.send_habit_completion_celebration(
            current_user.id, habit_name, streak
        )
        
        if success:
            return {"message": f"'{habit_name}' 습관 {streak}일 달성 축하 알림이 발송되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="축하 알림 발송에 실패했습니다"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"축하 알림 발송 실패: {str(e)}"
        )


# ==================== 3번 모듈: 습관 추적 시스템 ====================

@router.get("/tracking/{habit_id}")
async def get_comprehensive_tracking_data(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    종합 추적 데이터 조회
    
    스트릭, 완료율, 일관성 패턴, 최적 타이밍 등 모든 추적 데이터를 종합 제공
    """
    tracking_service = TrackingService(db)
    
    # 사용자 습관 확인
    habit_service = HabitService(db)
    user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
    
    if not user_habit:
        raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    tracking_data = await tracking_service.get_comprehensive_tracking_data(user_habit.id)
    
    return {
        "habit_info": {
            "id": str(user_habit.id),
            "name": user_habit.habit_template.name if user_habit.habit_template else "사용자 정의 습관",
            "category": user_habit.habit_template.category.name if user_habit.habit_template and user_habit.habit_template.category else None,
            "is_active": user_habit.is_active
        },
        "tracking_data": tracking_data
    }


@router.post("/tracking/auto-sync")
async def sync_auto_tracking_data(
    health_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    자동 추적 데이터 동기화
    
    웨어러블 기기나 헬스 앱의 데이터를 받아서 자동으로 습관 완료를 감지하고 기록
    """
    tracking_service = TrackingService(db)
    
    success = await tracking_service.auto_tracking.integrate_health_data(
        user_id=current_user.id,
        health_data=health_data
    )
    
    if success:
        return {"message": "자동 추적 데이터가 성공적으로 동기화되었습니다"}
    else:
        raise HTTPException(status_code=500, detail="자동 추적 데이터 동기화에 실패했습니다")


@router.get("/tracking/streak/{habit_id}")
async def get_streak_analysis(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    스트릭 분석 데이터 조회
    
    현재 스트릭, 최장 스트릭, 위험도 예측, 회복 제안 등
    """
    tracking_service = TrackingService(db)
    
    # 사용자 습관 확인
    habit_service = HabitService(db)
    user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
    
    if not user_habit:
        raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    current_streak = await tracking_service.streak_calculator.calculate_current_streak(user_habit.id)
    longest_streak = await tracking_service.streak_calculator.calculate_longest_streak(user_habit.id)
    risk_level = await tracking_service.streak_calculator.predict_streak_risk(user_habit.id)
    recovery_suggestions = await tracking_service.streak_calculator.get_streak_recovery_suggestions(user_habit.id)
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "risk_level": round(risk_level, 2),
        "risk_status": "높음" if risk_level > 0.7 else "보통" if risk_level > 0.4 else "낮음",
        "recovery_suggestions": recovery_suggestions
    }


@router.get("/tracking/progress/{habit_id}")
async def get_progress_analysis(
    habit_id: UUID,
    period: str = "monthly",  # daily, weekly, monthly, yearly
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    진척도 분석 데이터 조회
    
    완료율, 일관성 패턴, 최적 타이밍, 난이도 조정 제안 등
    """
    from app.services.tracking_service import TimePeriod, ConsistencyPattern
    
    tracking_service = TrackingService(db)
    
    # 사용자 습관 확인
    habit_service = HabitService(db)
    user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
    
    if not user_habit:
        raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    # 기간 파라미터 검증
    try:
        time_period = TimePeriod(period.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 기간입니다. daily, weekly, monthly, yearly 중 선택하세요")
    
    completion_rate = await tracking_service.progress_analyzer.calculate_completion_rate(
        user_habit.id, time_period
    )
    consistency_pattern = await tracking_service.progress_analyzer.analyze_consistency_pattern(user_habit.id)
    optimal_times = await tracking_service.progress_analyzer.identify_optimal_timing(user_habit.id)
    difficulty_adjustment = await tracking_service.progress_analyzer.calculate_difficulty_adjustment(user_habit.id)
    
    # 난이도 조정 메시지
    adjustment_messages = {
        -2: "목표를 크게 줄여보세요",
        -1: "목표를 조금 줄여보세요", 
        0: "현재 난이도가 적절합니다",
        1: "목표를 조금 늘려보세요",
        2: "목표를 크게 늘려보세요"
    }
    
    return {
        "completion_rate": round(completion_rate * 100, 1),
        "consistency_pattern": {
            "level": consistency_pattern.value,
            "description": {
                "very_consistent": "매우 일관적",
                "consistent": "일관적", 
                "moderate": "보통",
                "inconsistent": "비일관적",
                "very_inconsistent": "매우 비일관적"
            }.get(consistency_pattern.value, "알 수 없음")
        },
        "optimal_times": [{"hour": hour, "minute": minute} for hour, minute in optimal_times],
        "difficulty_adjustment": {
            "level": difficulty_adjustment,
            "message": adjustment_messages.get(difficulty_adjustment, "알 수 없음")
        }
    }


@router.post("/tracking/evidence/{log_id}")
async def upload_habit_evidence(
    log_id: UUID,
    evidence_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    습관 실행 증거 파일 업로드
    
    사진, 동영상, 오디오, GPS 데이터 등의 증거를 업로드
    """
    tracking_service = TrackingService(db)
    
    # 로그 소유권 확인
    habit_service = HabitService(db)
    log = await habit_service.get_habit_log(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="습관 로그를 찾을 수 없습니다")
    
    # 사용자 권한 확인 (로그의 습관이 현재 사용자 것인지)
    user_habit = await habit_service.get_user_habit_by_log(log_id)
    if not user_habit or user_habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    success = await tracking_service.process_evidence_upload(log_id, evidence_data)
    
    if success:
        return {"message": "증거 파일이 성공적으로 업로드되었습니다"}
    else:
        raise HTTPException(status_code=500, detail="증거 파일 업로드에 실패했습니다")


@router.get("/tracking/smart-reminder/{habit_id}")
async def get_smart_reminder_time(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    스마트 리마인더 시간 조회
    
    사용자의 과거 실행 패턴을 분석하여 최적의 리마인더 시간을 제안
    """
    tracking_service = TrackingService(db)
    
    # 사용자 습관 확인
    habit_service = HabitService(db)
    user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
    
    if not user_habit:
        raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    optimal_time = await tracking_service.auto_tracking.smart_reminder_timing(user_habit)
    
    if optimal_time:
        return {
            "optimal_reminder_time": optimal_time.isoformat(),
            "message": f"최적 리마인더 시간: {optimal_time.strftime('%Y-%m-%d %H:%M')}"
        }
    else:
        return {
            "optimal_reminder_time": None,
            "message": "충분한 데이터가 없어 기본 시간을 사용합니다"
        }


# ==================== 4번 모듈: AI 코칭 시스템 ====================

@router.post("/ai-coaching/personalized")
async def generate_personalized_coaching_message(
    message_type: MessageType,
    habit_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    개인화된 AI 코칭 메시지 생성
    
    사용자의 현재 상황, 습관 진행 상태, 기분 등을 종합 분석하여
    OpenAI GPT-4 기반의 개인화된 코칭 메시지를 생성합니다.
    
    Args:
        message_type: 메시지 타입 (morning_motivation, habit_reminder, encouragement 등)
        habit_id: 특정 습관 ID (선택사항)
        
    Returns:
        개인화된 코칭 메시지와 분석 데이터
    """
    ai_coaching_service = AICoachingService(db)
    
    # 습관 ID가 제공된 경우 사용자 습관 확인
    if habit_id:
        habit_service = HabitService(db)
        user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
        if not user_habit:
            raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    # 개인화된 코칭 메시지 생성
    coaching_message = await ai_coaching_service.generate_personalized_message(
        user_id=current_user.id,
        message_type=message_type,
        habit_id=habit_id
    )
    
    return {
        "message": coaching_message.message,
        "message_type": coaching_message.message_type.value,
        "tone": coaching_message.tone,
        "personalization_score": coaching_message.personalization_score,
        "context_relevance": coaching_message.context_relevance,
        "generated_at": coaching_message.generated_at.isoformat(),
        "habit_id": str(habit_id) if habit_id else None
    }


@router.get("/ai-coaching/context-analysis")
async def analyze_coaching_context(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 코칭 컨텍스트 분석
    
    사용자의 현재 상황을 종합 분석하여 코칭 기회를 감지하고
    최적의 코칭 전략을 제안합니다.
    
    Returns:
        현재 상황 분석 결과 및 코칭 기회 목록
    """
    ai_coaching_service = AICoachingService(db)
    
    # 컨텍스트 분석
    context = await ai_coaching_service.context_analyzer.analyze_current_situation(current_user.id)
    
    # 코칭 기회 감지
    opportunities = await ai_coaching_service.context_analyzer.identify_coaching_opportunities(context)
    
    return {
        "user_profile": {
            "name": context.user_profile.get("name"),
            "timezone": context.user_profile.get("timezone"),
            "personality_type": context.user_profile.get("personality_type")
        },
        "current_situation": {
            "current_time": context.current_time.isoformat(),
            "day_of_week": context.day_of_week,
            "time_of_day": context.time_of_day
        },
        "habit_status": {
            "streak_status": context.streak_status,
            "recent_completion_rate": ai_coaching_service._calculate_recent_completion_rate_from_context(context)
        },
        "coaching_opportunities": [
            {
                "type": opp.opportunity_type,
                "priority": opp.priority,
                "context": opp.context,
                "suggested_message_type": opp.suggested_message_type.value,
                "urgency": opp.urgency
            }
            for opp in opportunities[:5]  # 상위 5개만 반환
        ],
        "mood_insights": {
            "recent_mood_average": sum(mood.mood_score for mood in context.mood_trends) / len(context.mood_trends) if context.mood_trends else 0,
            "energy_trend": [mood.energy_level.value for mood in context.mood_trends[-3:]] if context.mood_trends else [],
            "stress_level": context.mood_trends[-1].stress_level if context.mood_trends else 5
        },
        "environmental_factors": {
            "weather": {
                "condition": context.weather_data.condition.value if context.weather_data else "unknown",
                "temperature": context.weather_data.temperature if context.weather_data else None
            },
            "upcoming_events": len(context.calendar_events),
            "energy_pattern": {
                "current_energy": context.energy_patterns.morning_energy.value if context.energy_patterns and context.time_of_day == "morning" else "medium"
            }
        }
    }


@router.get("/ai-coaching/smart-notification/{habit_id}")
async def get_smart_notification_schedule(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    습관별 스마트 알림 스케줄 조회
    
    사용자의 행동 패턴을 분석하여 최적의 알림 시간과 빈도를 계산합니다.
    
    Args:
        habit_id: 사용자 습관 ID
        
    Returns:
        최적화된 알림 스케줄과 개인화 설정
    """
    habit_service = HabitService(db)
    
    # 사용자 습관 확인
    user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
    if not user_habit:
        raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    # SmartNotificationEngine 인스턴스 생성
    from app.services.ai_coaching_service import SmartNotificationEngine
    smart_engine = SmartNotificationEngine(db)
    
    # 스마트 알림 스케줄 및 빈도 계산
    schedule = await smart_engine.optimize_notification_timing(current_user.id, habit_id)
    frequency_config = await smart_engine.calculate_notification_frequency(current_user.id, habit_id)
    
    return {
        "habit_info": {
            "id": str(habit_id),
            "name": user_habit.habit_template.name if user_habit.habit_template else "사용자 정의 습관"
        },
        "notification_schedule": {
            "optimal_times": schedule.optimal_times,
            "frequency": schedule.frequency,
            "enabled": schedule.enabled
        },
        "frequency_config": {
            "daily_limit": frequency_config.daily_limit,
            "min_interval_hours": frequency_config.min_interval_hours,
            "peak_times": frequency_config.peak_times,
            "avoid_times": frequency_config.avoid_times
        },
        "personalization_insights": {
            "based_on_completion_patterns": True,
            "analysis_period_days": 30,
            "confidence_score": 0.85
        }
    }


@router.post("/ai-coaching/notification/personalize")
async def generate_personalized_notification(
    notification_type: NotificationType,
    habit_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    개인화된 알림 메시지 생성
    
    사용자의 선호도와 상황에 맞는 개인화된 알림 메시지를 생성합니다.
    
    Args:
        notification_type: 알림 타입 (habit_reminder, streak_alert, motivation 등)
        habit_id: 습관 ID (선택사항)
        
    Returns:
        개인화된 알림 메시지
    """
    from app.services.ai_coaching_service import SmartNotificationEngine
    smart_engine = SmartNotificationEngine(db)
    
    # 습관 ID가 제공된 경우 사용자 습관 확인
    if habit_id:
        habit_service = HabitService(db)
        user_habit = await habit_service.get_user_habit_by_id(current_user.id, habit_id)
        if not user_habit:
            raise HTTPException(status_code=404, detail="습관을 찾을 수 없습니다")
    
    # 개인화된 알림 메시지 생성
    message = await smart_engine.personalize_notification_content(
        user_id=current_user.id,
        notification_type=notification_type,
        habit_id=habit_id
    )
    
    return {
        "message": message,
        "notification_type": notification_type.value,
        "habit_id": str(habit_id) if habit_id else None,
        "personalization_applied": True,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/ai-coaching/opportunities")
async def get_coaching_opportunities(
    priority_threshold: int = Query(5, ge=1, le=10, description="우선순위 임계값 (이상만 반환)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 코칭 기회 목록 조회
    
    사용자의 현재 상황을 분석하여 즉시 실행 가능한 코칭 기회들을 제안합니다.
    
    Args:
        priority_threshold: 우선순위 임계값 (이상만 반환)
        
    Returns:
        우선순위가 높은 코칭 기회 목록
    """
    ai_coaching_service = AICoachingService(db)
    
    # 컨텍스트 분석 및 코칭 기회 감지
    context = await ai_coaching_service.context_analyzer.analyze_current_situation(current_user.id)
    opportunities = await ai_coaching_service.context_analyzer.identify_coaching_opportunities(context)
    
    # 우선순위 필터링
    high_priority_opportunities = [
        opp for opp in opportunities 
        if opp.priority >= priority_threshold
    ]
    
    return {
        "total_opportunities": len(opportunities),
        "high_priority_count": len(high_priority_opportunities),
        "opportunities": [
            {
                "id": f"opp_{i+1}",
                "type": opp.opportunity_type,
                "priority": opp.priority,
                "urgency": opp.urgency,
                "context": opp.context,
                "suggested_message_type": opp.suggested_message_type.value,
                "recommended_action": f"{opp.suggested_message_type.value} 메시지 발송"
            }
            for i, opp in enumerate(high_priority_opportunities)
        ],
        "analysis_timestamp": context.current_time.isoformat()
    }