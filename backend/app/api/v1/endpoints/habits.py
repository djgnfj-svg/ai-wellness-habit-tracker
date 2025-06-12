"""
습관 관련 API 엔드포인트
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.dependencies import get_db, get_current_user, standard_rate_limit
from app.schemas.habit import (
    # Categories
    HabitCategoryResponse, HabitCategoryCreate, HabitCategoryUpdate,
    # Templates  
    HabitTemplateResponse, HabitTemplateListResponse, HabitTemplateSearchParams,
    HabitTemplateCreate, HabitTemplateUpdate,
    # User Habits
    UserHabitResponse, UserHabitCreate, UserHabitUpdate, UserHabitFilterParams,
    # Logs
    HabitLogResponse, HabitLogCreate, HabitLogUpdate,
    # Dashboard
    DashboardData,
    # Common
    StandardResponse
)
from app.services.habit_service import HabitService
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.habit import DifficultyLevel, FrequencyType

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
    categories = await habit_service.get_categories(include_inactive=include_inactive)
    return [HabitCategoryResponse.model_validate(cat) for cat in categories]


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
    
    return HabitCategoryResponse.model_validate(category)


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
    """습관 템플릿 목록 조회"""
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
    
    templates, total_count = await habit_service.get_habit_templates(search_params)
    
    return HabitTemplateListResponse(
        habits=[HabitTemplateResponse.model_validate(t) for t in templates],
        total_count=total_count,
        has_next=(page * limit) < total_count,
        page=page,
        limit=limit
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
    
    return HabitTemplateResponse.model_validate(template)


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
    """사용자의 습관 목록 조회"""
    habit_service = HabitService(db)
    
    filter_params = UserHabitFilterParams(
        category_id=category_id,
        is_active=is_active,
        priority=priority,
        has_reminder=has_reminder
    )
    
    try:
        habits = await habit_service.get_user_habits(current_user.id, filter_params)
        return [UserHabitResponse.model_validate(habit) for habit in habits]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"습관 목록 조회 실패: {str(e)}"
        )


@router.post("/user/habits", response_model=UserHabitResponse, status_code=status.HTTP_201_CREATED)
async def create_user_habit(
    habit_data: UserHabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """새로운 사용자 습관 생성"""
    habit_service = HabitService(db)
    
    try:
        habit = await habit_service.create_user_habit(current_user.id, habit_data)
        return UserHabitResponse.model_validate(habit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"습관 생성 실패: {str(e)}"
        )


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
    
    return UserHabitResponse.model_validate(habit)


@router.put("/user/habits/{habit_id}", response_model=UserHabitResponse)
async def update_user_habit(
    habit_id: UUID,
    habit_update: UserHabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 습관 업데이트"""
    habit_service = HabitService(db)
    
    try:
        habit = await habit_service.update_user_habit(current_user.id, habit_id, habit_update)
        return UserHabitResponse.model_validate(habit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"습관 업데이트 실패: {str(e)}"
        )


@router.delete("/user/habits/{habit_id}", response_model=StandardResponse)
async def delete_user_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """사용자 습관 삭제 (비활성화)"""
    habit_service = HabitService(db)
    
    try:
        success = await habit_service.delete_user_habit(current_user.id, habit_id)
        if success:
            return StandardResponse(message="습관이 삭제되었습니다")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="습관 삭제에 실패했습니다"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"습관 삭제 실패: {str(e)}"
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
    """습관 체크인 (실행 로그 생성)"""
    habit_service = HabitService(db)
    
    try:
        log = await habit_service.create_habit_log(current_user.id, log_data)
        return HabitLogResponse.model_validate(log)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"체크인 실패: {str(e)}"
        )


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
    """습관 실행 로그 목록 조회"""
    habit_service = HabitService(db)
    
    try:
        logs = await habit_service.get_habit_logs(
            user_id=current_user.id,
            habit_id=habit_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return [HabitLogResponse.model_validate(log) for log in logs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"로그 조회 실패: {str(e)}"
        )


@router.get("/tracking/today", response_model=DashboardData)
async def get_today_dashboard(
    target_date: Optional[date] = Query(None, description="조회할 날짜 (기본: 오늘)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """오늘의 습관 현황 대시보드"""
    habit_service = HabitService(db)
    
    if target_date is None:
        target_date = date.today()
    
    try:
        dashboard_data = await habit_service.get_daily_dashboard(current_user.id, target_date)
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"대시보드 데이터 조회 실패: {str(e)}"
        )


# =====================================================================
# 관리자 API (추후 권한 체크 추가 예정)
# =====================================================================

@router.post("/admin/categories", response_model=HabitCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_category(
    category_data: HabitCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 추후 관리자 권한 체크 추가
    _: None = Depends(standard_rate_limit)
):
    """습관 카테고리 생성 (관리자용)"""
    habit_service = HabitService(db)
    
    try:
        category = await habit_service.create_category(category_data)
        return HabitCategoryResponse.model_validate(category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"카테고리 생성 실패: {str(e)}"
        )


@router.post("/admin/templates", response_model=HabitTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_template(
    template_data: HabitTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 추후 관리자 권한 체크 추가
    _: None = Depends(standard_rate_limit)
):
    """습관 템플릿 생성 (관리자용)"""
    habit_service = HabitService(db)
    
    try:
        template = await habit_service.create_habit_template(template_data)
        return HabitTemplateResponse.model_validate(template)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"템플릿 생성 실패: {str(e)}"
        )


# =====================================================================
# 통계 및 분석 API (추후 확장)
# =====================================================================

@router.get("/stats/summary")
async def get_habit_statistics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
):
    """습관 통계 요약"""
    habit_service = HabitService(db)
    
    try:
        statistics = await habit_service.get_habit_statistics_summary(current_user.id)
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"통계 조회 실패: {str(e)}"
        )


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
        return [HabitTemplateResponse.model_validate(template) for template in recommendations]
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
