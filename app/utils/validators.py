# app/utils/validators.py
from typing import Optional
import re

def validate_email(email: str) -> bool:
    """Проверка валидности email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_uuid(uuid_str: str) -> bool:
    """Проверка валидности UUID"""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False

def validate_connection_link(link: str) -> bool:
    """Проверка валидности ссылки подключения"""
    # Простая проверка на наличие протокола
    return link.startswith(("vless://", "vmess://", "trojan://"))
