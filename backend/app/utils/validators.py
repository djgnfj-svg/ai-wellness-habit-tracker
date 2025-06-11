"""
유틸리티 검증 함수들
"""
import re
from typing import Optional
from datetime import datetime


def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_nickname(nickname: str) -> bool:
    """닉네임 검증 (2-20자, 한글/영문/숫자)"""
    if not nickname or len(nickname) < 2 or len(nickname) > 20:
        return False
    
    # 한글, 영문, 숫자만 허용
    pattern = r'^[\w\u4e00-\u9fff\uac00-\ud7af]+$'
    return bool(re.match(pattern, nickname))


def validate_birth_year(birth_year: Optional[int]) -> bool:
    """출생연도 검증"""
    if birth_year is None:
        return True
    
    current_year = datetime.now().year
    return 1900 <= birth_year <= current_year


def validate_password_strength(password: str) -> bool:
    """비밀번호 강도 검증 (8자 이상, 영문+숫자+특수문자)"""
    if len(password) < 8:
        return False
    
    # 영문, 숫자, 특수문자 각각 하나 이상 포함
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    return has_letter and has_digit and has_special


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """문자열 살균 및 길이 제한"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 여러 공백을 하나로 통합
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 길이 제한
    return text[:max_length]


def validate_phone_number(phone: str) -> bool:
    """한국 전화번호 형식 검증"""
    # 010-1234-5678, 01012345678 형식 지원
    pattern = r'^(010)[\-\s]?\d{4}[\-\s]?\d{4}$'
    return bool(re.match(pattern, phone))


def validate_age_range(birth_year: int) -> str:
    """나이대 계산"""
    current_year = datetime.now().year
    age = current_year - birth_year
    
    if age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    elif age < 50:
        return "40대"
    elif age < 60:
        return "50대"
    else:
        return "60대 이상"