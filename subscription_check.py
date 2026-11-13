# subscription_check.py

import asyncio
from telegram import ChatMember
from max_subscription import is_subscribed_to_max_channels, init_max_checker

# Инициализация MAX проверки (замените на ваш токен)
init_max_checker('YOUR_MAX_API_TOKEN_HERE')

async def is_subscribed(bot, user_id: int, telegram_channels: list, max_channels: list = None) -> bool:
    """
    Проверяет подписку пользователя на Telegram и MAX каналы
    """
    
    # Проверяем Telegram-каналы
    for channel in telegram_channels:
        try:
            chat_member = await bot.get_chat_member(channel, user_id)
            if chat_member.status not in ['member', 'creator', 'administrator']:
                return False
        except Exception as e:
            print(f"Ошибка при проверке подписки на {channel}: {e}")
            return False
    
    # Проверяем MAX-каналы (если указаны)
    if max_channels:
        try:
            max_subscribed = await is_subscribed_to_max_channels(user_id, max_channels)
            if not max_subscribed:
                return False
        except Exception as e:
            print(f"Ошибка при проверке подписки на MAX каналы: {e}")
            return False
    
    return True

async def check_all_subscriptions(bot, user_id: int, telegram_channels: list, max_channels: list = None) -> dict:
    """Возвращает словарь с состоянием подписок"""
    result = {}
    
    # Проверяем Telegram-каналы
    for channel in telegram_channels:
        try:
            chat_member = await bot.get_chat_member(channel, user_id)
            result[channel] = chat_member.status in ['member', 'creator', 'administrator']
        except Exception as e:
            print(f"Ошибка проверки {channel}: {e}")
            result[channel] = False
    
    # Проверяем MAX-каналы (если указаны)
    if max_channels:
        try:
            max_results = await is_subscribed_to_max_channels(user_id, max_channels)
            for channel in max_channels:
                result[channel] = max_results
        except Exception as e:
            print(f"Ошибка проверки MAX каналов: {e}")
            for channel in max_channels:
                result[channel] = False
    
    return result

async def get_user_subscription_status(bot, user_id: int, telegram_channels: list, max_channels: list = None) -> str:
    """Возвращает текстовый статус подписки"""
    subscriptions = await check_all_subscriptions(bot, user_id, telegram_channels, max_channels)
    status = []
    
    for channel, subscribed in subscriptions.items():
        if "max.com" in channel or "max_" in channel:
            # Для MAX каналов
            status.append(f"{'✅' if subscribed else '❌'} MAX: {channel}")
        else:
            # Для Telegram каналов
            status.append(f"{'✅' if subscribed else '❌'} TG: {channel}")
    
    return "\n".join(status)
