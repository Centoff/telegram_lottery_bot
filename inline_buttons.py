# inline_buttons.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TELEGRAM_CHANNELS, MAX_CHANNELS

def get_join_keyboard():
    keyboard = [
        [InlineKeyboardButton("Подтвердить участие", callback_data="confirm_join")],
        [InlineKeyboardButton("Отмена", callback_data="cancel_join")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_channel_subscription_keyboard(channels: list):
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(f"Подписаться на {channel}", url=f"https://t.me/{channel[1:] if channel.startswith('@') else channel}")])
    return InlineKeyboardMarkup(keyboard)

def get_webapp_keyboard():
    keyboard = [
        [InlineKeyboardButton("Открыть WebApp", web_app=True)]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎲 Участвовать в розыгрыше", callback_data="join_lottery")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="user_stats")],
        [InlineKeyboardButton("🏆 История розыгрышей", callback_data="draw_history")],
        [InlineKeyboardButton("🎁 Мои награды", callback_data="my_rewards")],
        [InlineKeyboardButton("🌐 WebApp", callback_data="webapp")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu():
    keyboard = [
        [InlineKeyboardButton("🔄 Сбросить данные", callback_data="reset_data")],
        [InlineKeyboardButton("🎲 Провести розыгрыш", callback_data="force_draw")],
        [InlineKeyboardButton("📊 Статистика бота", callback_data="bot_stats")],
        [InlineKeyboardButton("👥 Все пользователи", callback_data="all_users")],
        [InlineKeyboardButton("➕ Добавить канал", callback_data="admin_add_channel")],
        [InlineKeyboardButton("📋 Управление каналами", callback_data="admin_manage_channels")],
        [InlineKeyboardButton("➕ Добавить приз", callback_data="admin_add_prize")],
        [InlineKeyboardButton("🎁 Управление призами", callback_data="admin_manage_prizes")],
        [InlineKeyboardButton("⏰ Автоматические розыгрыши", callback_data="admin_auto_draws")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_channel_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить канал", callback_data="admin_add_channel")],
        [InlineKeyboardButton("📋 Список каналов", callback_data="admin_list_channels")],
        [InlineKeyboardButton("Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_prize_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить приз", callback_data="admin_add_prize")],
        [InlineKeyboardButton("📋 Список призов", callback_data="admin_list_prizes")],
        [InlineKeyboardButton("Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_auto_draw_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить автоматический розыгрыш", callback_data="admin_add_auto_draw")],
        [InlineKeyboardButton("📋 Список розыгрышей", callback_data="admin_list_auto_draws")],
        [InlineKeyboardButton("Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_channel_list_keyboard(channels):
    keyboard = []
    for channel in channels:
        id_, name, channel_id, is_active = channel
        status = "✅" if is_active else "❌"
        keyboard.append([InlineKeyboardButton(f"{status} {name} ({channel_id})", callback_data=f"channel_info_{id_}")])
    keyboard.append([InlineKeyboardButton("Назад", callback_data="admin_main")])
    return InlineKeyboardMarkup(keyboard)

def get_prize_list_keyboard(prizes):
    keyboard = []
    for prize in prizes:
        id_, name, value, is_active, usage_count = prize
        status = "✅" if is_active else "❌"
        keyboard.append([InlineKeyboardButton(f"{status} {name} - {value} (использовано: {usage_count})", callback_data=f"prize_info_{id_}")])
    keyboard.append([InlineKeyboardButton("Назад", callback_data="admin_main")])
    return InlineKeyboardMarkup(keyboard)

def get_auto_draw_list_keyboard(draws):
    keyboard = []
    for draw in draws:
        id_, datetime_, prize_id, is_active, executed = draw
        status = "✅" if is_active else "❌"
        exec_status = "🔄" if not executed else "✅"
        keyboard.append([InlineKeyboardButton(f"{status}{exec_status} {datetime_} (приз ID: {prize_id})", callback_data=f"auto_draw_info_{id_}")])
    keyboard.append([InlineKeyboardButton("Назад", callback_data="admin_main")])
    return InlineKeyboardMarkup(keyboard)
