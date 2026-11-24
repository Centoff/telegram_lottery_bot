# utils.py

import random
from datetime import datetime, timedelta
from config import PRIZE_AMOUNT

def generate_prize():
    """Генерирует случайный приз"""
    prizes = [
        "100₽", "500₽", "1000₽", "2000₽", "5000₽",
        "Telegram Premium 1 месяц", "Подарочная карта 1000₽",
        "Мобильный телефон", "Планшет", "Кошелек"
    ]
    return random.choice(prizes)

def format_datetime(dt_str):
    """Форматирует дату для отображения"""
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt_str

def get_user_level(joins: int) -> str:
    """Определяет уровень пользователя"""
    if joins >= 100:
        return "🏆 Мастер розыгрышей"
    elif joins >= 50:
        return "⭐ Эксперт"
    elif joins >= 20:
        return "🌟 Новичок"
    else:
        return "👤 Участник"

def get_prize_tier(prize: str) -> str:
    """Определяет уровень приза"""
    if "₽" in prize:
        amount = int(prize.replace("₽", ""))
        if amount >= 5000:
            return "🏆 Главный приз"
        elif amount >= 1000:
            return "💰 Средний приз"
        else:
            return "✨ Маленький приз"
    else:
        return "🎁 Специальный приз"

def parse_datetime(datetime_str: str) -> datetime:
    """Парсинг даты и времени"""
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return None

def is_past_datetime(datetime_str: str) -> bool:
    """Проверяет, является ли дата в прошлом"""
    dt = parse_datetime(datetime_str)
    if dt:
        return dt < datetime.now()
    return False
