"""
도움 함수들
"""
import hashlib
import secrets
import string
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pytz


def generate_random_string(length: int = 32) -> str:
    """랜덤 문자열 생성"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_string(text: str) -> str:
    """문자열 해싱 (SHA-256)"""
    return hashlib.sha256(text.encode()).hexdigest()


def get_korean_time() -> datetime:
    """한국 시간 반환"""
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)


def format_korean_datetime(dt: datetime) -> str:
    """한국식 날짜 형식"""
    return dt.strftime('%Y년 %m월 %d일 %H:%M:%S')


def calculate_age(birth_year: int) -> int:
    """나이 계산"""
    current_year = datetime.now().year
    return current_year - birth_year


def mask_email(email: str) -> str:
    """이메일 마스킹 (user@example.com -> u***@example.com)"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 1:
        return email
    
    masked_local = local[0] + '*' * (len(local) - 1)
    return f"{masked_local}@{domain}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_time_slot(time_str: str) -> Optional[Dict[str, int]]:
    """시간대 문자열 파싱 ("09:00-10:00" -> {"start_hour": 9, "start_minute": 0, "end_hour": 10, "end_minute": 0})"""
    try:
        start_time, end_time = time_str.split('-')
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        
        return {
            "start_hour": start_hour,
            "start_minute": start_minute,
            "end_hour": end_hour,
            "end_minute": end_minute
        }
    except (ValueError, AttributeError):
        return None


def format_time_slot(time_data: Dict[str, int]) -> str:
    """시간대 데이터를 문자열로 변환"""
    start_time = f"{time_data['start_hour']:02d}:{time_data['start_minute']:02d}"
    end_time = f"{time_data['end_hour']:02d}:{time_data['end_minute']:02d}"
    return f"{start_time}-{end_time}"


def get_weekday_korean(weekday: int) -> str:
    """요일 숫자를 한글로 변환 (0=월요일)"""
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    return weekdays[weekday % 7]


def calculate_streak_days(log_dates: List[datetime]) -> int:
    """연속 일수 계산"""
    if not log_dates:
        return 0
    
    # 날짜만 추출 및 정렬
    dates = sorted(set(date.date() for date in log_dates), reverse=True)
    
    if not dates:
        return 0
    
    # 오늘부터 역순으로 연속 일수 계산
    today = datetime.now().date()
    streak = 0
    current_date = today
    
    for date in dates:
        if date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif date == current_date + timedelta(days=1):
            # 오늘 기록이 없어도 어제부터 연속이면 계속
            current_date = date
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """안전한 나눗셈 (영나눔 방지)"""
    return numerator / denominator if denominator != 0 else default


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """백분율 형식화"""
    return f"{value:.{decimal_places}f}%"