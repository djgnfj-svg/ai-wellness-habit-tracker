"""
알림 서비스
습관 리마인더, 푸시 알림, 이메일 알림 등을 관리합니다.

주요 기능:
- 습관 리마인더 스케줄링
- 알림 발송 (콘솔, 푸시, 이메일)
- 알림 설정 관리
- 알림 히스토리 추적
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload
import asyncio
import logging

from app.models.habit import UserHabit, HabitLog, CompletionStatus
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    알림 서비스 클래스
    
    습관 리마인더와 각종 알림을 관리합니다.
    현재는 콘솔 로그 기반이며, 추후 실제 푸시/이메일 연동 가능합니다.
    """
    
    def __init__(self, db: AsyncSession):
        """
        서비스 초기화
        
        Args:
            db: 비동기 데이터베이스 세션
        """
        self.db = db

    async def schedule_habit_reminders(self, user_id: UUID, target_date: datetime = None) -> List[Dict[str, Any]]:
        """
        사용자의 습관 리마인더 스케줄링
        
        Args:
            user_id: 사용자 ID
            target_date: 대상 날짜 (기본: 오늘)
            
        Returns:
            List[Dict]: 스케줄된 리마인더 목록
        """
        if target_date is None:
            target_date = datetime.now()
        
        # 사용자의 활성 습관 조회 (리마인더 설정된 것만)
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(
            and_(
                UserHabit.user_id == user_id,
                UserHabit.is_active == True,
                UserHabit.reminder_settings['enabled'].astext.cast(bool) == True
            )
        )
        
        result = await self.db.execute(stmt)
        habits_with_reminders = result.scalars().all()
        
        scheduled_reminders = []
        
        for habit in habits_with_reminders:
            reminder_times = habit.reminder_settings.get('times', [])
            
            for time_str in reminder_times:
                try:
                    # 시간 파싱
                    hour, minute = map(int, time_str.split(':'))
                    reminder_datetime = target_date.replace(
                        hour=hour, 
                        minute=minute, 
                        second=0, 
                        microsecond=0
                    )
                    
                    # 이미 지난 시간이면 다음날로
                    if reminder_datetime <= datetime.now():
                        reminder_datetime += timedelta(days=1)
                    
                    # 해당 시간에 이미 완료했는지 확인
                    is_completed = await self._is_habit_completed_today(habit.id, target_date.date())
                    
                    if not is_completed:
                        reminder_data = {
                            'habit_id': habit.id,
                            'habit_name': habit.custom_name or habit.habit_template.name,
                            'user_id': user_id,
                            'scheduled_time': reminder_datetime,
                            'message': habit.reminder_settings.get('message') or f"{habit.custom_name or habit.habit_template.name} 실천 시간입니다!",
                            'type': 'habit_reminder'
                        }
                        
                        scheduled_reminders.append(reminder_data)
                        
                        # 실제 알림 스케줄링 (현재는 로그만)
                        await self._schedule_notification(reminder_data)
                        
                except ValueError as e:
                    logger.warning(f"잘못된 리마인더 시간 형식: {time_str}, 습관 ID: {habit.id}")
                    continue
        
        return scheduled_reminders

    async def send_immediate_notification(
        self, 
        user_id: UUID, 
        message: str, 
        notification_type: str = "general",
        habit_id: Optional[UUID] = None
    ) -> bool:
        """
        즉시 알림 발송
        
        Args:
            user_id: 사용자 ID
            message: 알림 메시지
            notification_type: 알림 타입
            habit_id: 관련 습관 ID (선택)
            
        Returns:
            bool: 발송 성공 여부
        """
        try:
            notification_data = {
                'user_id': user_id,
                'message': message,
                'type': notification_type,
                'habit_id': habit_id,
                'sent_at': datetime.now(),
                'delivery_method': 'console'  # 현재는 콘솔만
            }
            
            # 실제 알림 발송
            success = await self._send_notification(notification_data)
            
            # 알림 히스토리 저장 (추후 구현)
            # await self._save_notification_history(notification_data, success)
            
            return success
            
        except Exception as e:
            logger.error(f"알림 발송 실패: {str(e)}")
            return False

    async def send_habit_completion_celebration(self, user_id: UUID, habit_name: str, streak: int) -> bool:
        """
        습관 완료 축하 알림
        
        Args:
            user_id: 사용자 ID
            habit_name: 습관 이름
            streak: 연속 달성 일수
            
        Returns:
            bool: 발송 성공 여부
        """
        if streak == 1:
            message = f"🎉 '{habit_name}' 습관을 완료했습니다! 좋은 시작이에요!"
        elif streak == 7:
            message = f"🔥 '{habit_name}' 습관 7일 연속 달성! 일주일 완주 축하드려요!"
        elif streak == 30:
            message = f"🏆 '{habit_name}' 습관 30일 연속 달성! 한 달 완주 대단해요!"
        elif streak % 10 == 0:
            message = f"✨ '{habit_name}' 습관 {streak}일 연속 달성! 꾸준함이 빛나고 있어요!"
        else:
            message = f"💪 '{habit_name}' 습관 {streak}일 연속 달성! 계속 화이팅!"
        
        return await self.send_immediate_notification(
            user_id=user_id,
            message=message,
            notification_type="celebration"
        )

    async def send_motivation_message(self, user_id: UUID, habit_id: UUID) -> bool:
        """
        동기부여 메시지 발송
        
        Args:
            user_id: 사용자 ID
            habit_id: 습관 ID
            
        Returns:
            bool: 발송 성공 여부
        """
        # 습관 정보 조회
        stmt = select(UserHabit).options(
            joinedload(UserHabit.habit_template)
        ).where(UserHabit.id == habit_id)
        
        result = await self.db.execute(stmt)
        habit = result.scalar_one_or_none()
        
        if not habit:
            return False
        
        # AI 코칭 메시지에서 동기부여 메시지 선택
        ai_prompts = habit.habit_template.ai_coaching_prompts
        motivation_messages = [
            prompt for prompt in ai_prompts 
            if any(word in prompt.lower() for word in ["동기", "격려", "화이팅", "할 수 있어"])
        ]
        
        if not motivation_messages:
            motivation_messages = [
                f"'{habit.custom_name or habit.habit_template.name}' 습관 실천 시간이에요! 💪",
                "작은 실천이 큰 변화를 만듭니다! ✨",
                "오늘도 좋은 습관으로 하루를 시작해보세요! 🌟"
            ]
        
        import random
        message = random.choice(motivation_messages)
        
        return await self.send_immediate_notification(
            user_id=user_id,
            message=message,
            notification_type="motivation",
            habit_id=habit_id
        )

    async def _is_habit_completed_today(self, habit_id: UUID, target_date: datetime.date) -> bool:
        """오늘 습관이 완료되었는지 확인"""
        stmt = select(HabitLog).where(
            and_(
                HabitLog.user_habit_id == habit_id,
                HabitLog.logged_at >= datetime.combine(target_date, time.min),
                HabitLog.logged_at < datetime.combine(target_date + timedelta(days=1), time.min),
                HabitLog.completion_status == CompletionStatus.COMPLETED
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def _schedule_notification(self, reminder_data: Dict[str, Any]) -> bool:
        """
        알림 스케줄링 (현재는 로그만, 추후 실제 스케줄러 연동)
        
        Args:
            reminder_data: 리마인더 데이터
            
        Returns:
            bool: 스케줄링 성공 여부
        """
        try:
            scheduled_time = reminder_data['scheduled_time']
            current_time = datetime.now()
            
            # 스케줄 시간까지의 지연 시간 계산
            delay_seconds = (scheduled_time - current_time).total_seconds()
            
            if delay_seconds > 0:
                logger.info(f"리마인더 스케줄됨: {reminder_data['habit_name']} at {scheduled_time}")
                
                # 실제 프로덕션에서는 Celery, APScheduler 등 사용
                # 현재는 간단한 asyncio 기반 지연 실행
                asyncio.create_task(self._delayed_notification(reminder_data, delay_seconds))
                
                return True
            else:
                logger.warning(f"과거 시간으로 리마인더 스케줄 시도: {scheduled_time}")
                return False
                
        except Exception as e:
            logger.error(f"리마인더 스케줄링 실패: {str(e)}")
            return False

    async def _delayed_notification(self, reminder_data: Dict[str, Any], delay_seconds: float):
        """지연된 알림 발송"""
        try:
            await asyncio.sleep(delay_seconds)
            await self._send_notification(reminder_data)
        except Exception as e:
            logger.error(f"지연된 알림 발송 실패: {str(e)}")

    async def _send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        실제 알림 발송 (현재는 콘솔 로그)
        
        추후 확장 가능:
        - 푸시 알림 (FCM, APNs)
        - 이메일 알림
        - SMS 알림
        - 웹 소켓 실시간 알림
        """
        try:
            # 콘솔 로그 출력
            logger.info("=" * 50)
            logger.info("🔔 HABIT REMINDER NOTIFICATION")
            logger.info(f"사용자 ID: {notification_data['user_id']}")
            logger.info(f"메시지: {notification_data['message']}")
            logger.info(f"타입: {notification_data['type']}")
            logger.info(f"시간: {notification_data.get('sent_at', datetime.now())}")
            if notification_data.get('habit_id'):
                logger.info(f"습관 ID: {notification_data['habit_id']}")
            logger.info("=" * 50)
            
            # 추후 실제 알림 발송 로직 추가
            # if settings.PUSH_NOTIFICATIONS_ENABLED:
            #     await self._send_push_notification(notification_data)
            # if settings.EMAIL_NOTIFICATIONS_ENABLED:
            #     await self._send_email_notification(notification_data)
            
            return True
            
        except Exception as e:
            logger.error(f"알림 발송 실패: {str(e)}")
            return False

    # =================================================================
    # 추후 확장 가능한 알림 방법들
    # =================================================================

    async def _send_push_notification(self, notification_data: Dict[str, Any]) -> bool:
        """푸시 알림 발송 (추후 구현)"""
        # FCM, APNs 등을 통한 푸시 알림
        pass

    async def _send_email_notification(self, notification_data: Dict[str, Any]) -> bool:
        """이메일 알림 발송 (추후 구현)"""
        # SMTP를 통한 이메일 발송
        pass

    async def _send_sms_notification(self, notification_data: Dict[str, Any]) -> bool:
        """SMS 알림 발송 (추후 구현)"""
        # SMS 서비스를 통한 문자 발송
        pass