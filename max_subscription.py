# max_subscription.py

import asyncio
import aiohttp
from typing import Dict, List, Optional

class MAXSubscriptionChecker:
    def __init__(self, max_api_token: str):
        self.max_api_token = max_api_token
        self.base_url = "https://api.max.com/v1"
        
    async def check_subscription(self, user_id: int, channel_ids: List[str]) -> Dict[str, bool]:
        """
        Проверяет подписку пользователя на несколько каналов MAX
        Возвращает словарь с результатами проверки
        """
        results = {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.max_api_token}',
                'Content-Type': 'application/json'
            }
            
            for channel_id in channel_ids:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_url}/channels/{channel_id}/members/{user_id}"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            results[channel_id] = data.get('is_subscribed', False)
                        else:
                            results[channel_id] = False
                            
        except Exception as e:
            print(f"Ошибка при проверке подписки на MAX: {e}")
            # В случае ошибки возвращаем все False
            for channel_id in channel_ids:
                results[channel_id] = False
                
        return results
    
    async def get_user_subscriptions(self, user_id: int) -> List[str]:
        """
        Получает список каналов, на которые подписан пользователь
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.max_api_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{user_id}/subscriptions"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('channels', [])
                    else:
                        return []
                        
        except Exception as e:
            print(f"Ошибка получения подписок пользователя: {e}")
            return []

# Глобальный экземпляр проверки
max_checker = None

def init_max_checker(max_api_token: str):
    """Инициализация проверки подписки на MAX"""
    global max_checker
    max_checker = MAXSubscriptionChecker(max_api_token)

async def is_subscribed_to_max_channels(user_id: int, channel_ids: List[str]) -> bool:
    """Проверяет подписку пользователя на все указанные каналы MAX"""
    if not max_checker:
        return False
        
    results = await max_checker.check_subscription(user_id, channel_ids)
    
    # Все каналы должны быть подписаны
    for subscribed in results.values():
        if not subscribed:
            return False
    
    return True

async def get_user_max_subscriptions(user_id: int) -> List[str]:
    """Получает список подписок пользователя на MAX"""
    if not max_checker:
        return []
        
    return await max_checker.get_user_subscriptions(user_id)
