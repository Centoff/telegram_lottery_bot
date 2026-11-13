# handlers.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import register_participant, has_participated_today, get_participants, save_draw, get_draw_history, get_user_stats, get_user_rewards, add_reward, get_total_draws, get_all_users, add_lottery_channel, get_lottery_channels, update_lottery_channel, delete_lottery_channel, add_prize, get_prizes, update_prize, delete_prize, get_active_prizes, add_auto_draw, get_auto_draws, update_auto_draw, mark_auto_draw_executed, increment_prize_usage
from subscription_check import is_subscribed, check_all_subscriptions, get_user_subscription_status
from inline_buttons import get_join_keyboard, get_channel_subscription_keyboard, get_webapp_keyboard, get_main_menu, get_admin_menu, get_admin_channel_menu, get_admin_prize_menu, get_admin_auto_draw_menu, get_channel_list_keyboard, get_prize_list_keyboard, get_auto_draw_list_keyboard
from utils import generate_prize, format_datetime, get_user_level, get_prize_tier
from config import TELEGRAM_CHANNELS, MAX_CHANNELS, ADMIN_CHAT_ID, PRIZE_AMOUNT
import random
import asyncio

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = get_main_menu()
    
    await update.message.reply_text(
        f"🎉 Привет, {user.first_name}!\n\n"
        f"Добро пожаловать в Telegram Lottery!\n"
        f"Участвуйте в розыгрышах и выигрывайте призы!\n\n"
        f"Подписаться на каналы:\n" + "\n".join(TELEGRAM_CHANNELS) + "\n" + "\n".join(MAX_CHANNELS),
        reply_markup=keyboard
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = get_join_keyboard()
    
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        f"Подтвердите участие в розыгрыше и подпишитесь на каналы:\n"
        + "\n".join(TELEGRAM_CHANNELS) + "\n" + "\n".join(MAX_CHANNELS),
        reply_markup=keyboard
    )

async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not has_participated_today(user_id):
        await update.message.reply_text("Вы ещё не участвовали сегодня. Используйте команду /join.")
        return

    users = get_participants()
    if not users:
        await update.message.reply_text("Нет участников!")
        return

    winner_id = random.choice(users)
    winner = await context.bot.get_chat(winner_id)
    
    # Генерируем приз
    prize = generate_prize()
    
    save_draw(winner_id, prize, "main", "manual")

    try:
        await context.bot.send_message(
            chat_id=winner_id,
            text=f"🎉 Поздравляем! Вы выиграли в розыгрыше!\n"
                  f"🏆 Приз: {prize}\n\n"
                  f"Приз будет доставлен в течение 24 часов."
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения победителю {winner_id}: {e}")

    await update.message.reply_text(
        f"🏆 Поздравляем @{winner.username} с победой!\n"
        f"Приз: {prize}\n"
        f"Участников: {len(users)}"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_user_stats(user_id)
    
    level = get_user_level(stats['joins'])
    
    await update.message.reply_text(
        f"📊 Ваша статистика:\n"
        f"🏆 Участий: {stats['joins']}\n"
        f"🎉 Побед: {stats['wins']}\n"
        f"🏅 Уровень: {level}"
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_draw_history(10)
    if not rows:
        await update.message.reply_text("История пуста.")
        return

    text = "🏆 Последние розыгрыши:\n\n"
    for row in rows:
        winner = await context.bot.get_chat(row[0])
        prize_tier = get_prize_tier(row[2])
        text += f"{format_datetime(row[1])}\n"
        text += f"🏆 @{winner.username or row[0]} - {row[2]}\n"
        text += f"🏷️ {prize_tier}\n\n"
    
    await update.message.reply_text(text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Доступ ограничен.")
        return

    import sqlite3
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("DELETE FROM participants")
    c.execute("DELETE FROM draws")
    c.execute("DELETE FROM user_stats")
    c.execute("DELETE FROM rewards")
    c.execute("DELETE FROM lottery_channels")
    c.execute("DELETE FROM prizes")
    c.execute("DELETE FROM auto_draws")
    conn.commit()
    conn.close()

    await update.message.reply_text("🔄 Все данные сброшены!")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Доступ ограничен.")
        return

    keyboard = get_admin_menu()
    await update.message.reply_text(
        "🔧 Админ-панель:",
        reply_markup=keyboard
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем подписку на все каналы
    status = await get_user_subscription_status(
        context.bot, 
        user_id, 
        TELEGRAM_CHANNELS, 
        MAX_CHANNELS
    )
    
    await update.message.reply_text(
        f"📋 Статус подписки:\n{status}"
    )

# === Новые обработчики для админ-панели ===

async def admin_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Здесь можно добавить логику для добавления канала
    await query.edit_message_text("Добавление нового канала для розыгрышей:\n\n"
                                  "Отправьте сообщение в формате:\n"
                                  "Название канала | ID канала")

async def admin_manage_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    channels = get_lottery_channels()
    keyboard = get_channel_list_keyboard(channels)
    
    await query.edit_message_text("📋 Каналы для розыгрышей:", reply_markup=keyboard)

async def admin_add_prize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Здесь можно добавить логику для добавления приза
    await query.edit_message_text("Добавление нового приза:\n\n"
                                  "Отправьте сообщение в формате:\n"
                                  "Название приза | Значение приза")

async def admin_manage_prizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    prizes = get_prizes()
    keyboard = get_prize_list_keyboard(prizes)
    
    await query.edit_message_text("🎁 Призы для розыгрышей:", reply_markup=keyboard)

async def admin_auto_draws(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    draws = get_auto_draws()
    keyboard = get_auto_draw_list_keyboard(draws)
    
    await query.edit_message_text("⏰ Автоматические розыгрыши:", reply_markup=keyboard)

# === Обработчики для конкретных действий ===

async def user_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    stats = get_user_stats(user_id)
    
    level = get_user_level(stats['joins'])
    
    await query.edit_message_text(
        f"📊 Ваша статистика:\n"
        f"🏆 Участий: {stats['joins']}\n"
        f"🎉 Побед: {stats['wins']}\n"
        f"🏅 Уровень: {level}"
    )

async def draw_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    rows = get_draw_history(10)
    if not rows:
        await query.edit_message_text("История пуста.")
        return

    text = "🏆 Последние розыгрыши:\n\n"
    for row in rows:
        winner = await context.bot.get_chat(row[0])
        prize_tier = get_prize_tier(row[2])
        text += f"{format_datetime(row[1])}\n"
        text += f"🏆 @{winner.username or row[0]} - {row[2]}\n"
        text += f"🏷️ {prize_tier}\n\n"
    
    await query.edit_message_text(text)

async def my_rewards_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    rewards = get_user_rewards(user_id)
    
    if not rewards:
        await query.edit_message_text("🎁 У вас пока нет наград.")
        return

    text = "🎁 Ваши награды:\n\n"
    for reward in rewards:
        text += f"{format_datetime(reward[2])}\n"
        text += f"🏆 {reward[1]} - {reward[0]}\n\n"
    
    await query.edit_message_text(text)

async def webapp_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = get_webapp_keyboard()
    await query.edit_message_text(
        "🌐 Откройте WebApp:",
        reply_markup=keyboard
    )

async def reset_data_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    import sqlite3
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("DELETE FROM participants")
    c.execute("DELETE FROM draws")
    c.execute("DELETE FROM user_stats")
    c.execute("DELETE FROM rewards")
    c.execute("DELETE FROM lottery_channels")
    c.execute("DELETE FROM prizes")
    c.execute("DELETE FROM auto_draws")
    conn.commit()
    conn.close()

    await query.edit_message_text("🔄 Все данные сброшены!")

async def force_draw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    users = get_participants()
    if not users:
        await query.edit_message_text("❌ Нет участников для розыгрыша!")
        return

    winner_id = random.choice(users)
    winner = await context.bot.get_chat(winner_id)
    
    prize = generate_prize()
    save_draw(winner_id, prize, "admin_force", "manual")
    
    try:
        await context.bot.send_message(
            chat_id=winner_id,
            text=f"🎉 Администратор провел розыгрыш!\n"
                  f"🏆 Приз: {prize}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения победителю {winner_id}: {e}")

    await query.edit_message_text(
        f"🏆 Победитель: @{winner.username}\n"
        f"Приз: {prize}"
    )

async def bot_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    total_users = len(get_all_users())
    total_draws = get_total_draws()
    
    await query.edit_message_text(
        f"📊 Статистика бота:\n"
        f"👥 Пользователей: {total_users}\n"
        f"🎲 Розыгрышей: {total_draws}"
    )

async def all_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    users = get_all_users()
    text = f"👥 Всего пользователей: {len(users)}\n\n"
    
    # Показываем первых 10 пользователей
    for i, user_id in enumerate(users[:10]):
        try:
            user = await context.bot.get_chat(user_id)
            text += f"{i+1}. @{user.username or user_id}\n"
        except:
            text += f"{i+1}. {user_id}\n"
    
    if len(users) > 10:
        text += f"\n... и ещё {len(users)-10} пользователей"
    
    await query.edit_message_text(text)

# === Новые обработчики для админ-панели ===

async def admin_add_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика добавления канала
    pass

async def admin_list_channels_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика отображения списка каналов
    pass

async def admin_add_prize_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика добавления приза
    pass

async def admin_list_prizes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика отображения списка призов
    pass

async def admin_add_auto_draw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика добавления автоматического розыгрыша
    pass

async def admin_list_auto_draws_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика отображения списка автоматических розыгрышей
    pass

# === Обработчики для кнопок админ-панели ===

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_join":
        user_id = query.from_user.id
        # Проверяем подписку на оба типа каналов
        subscribed = await is_subscribed(
            context.bot, 
            user_id, 
            ['@channel1', '@channel2'], 
            ['max_channel_1', 'max_channel_2']
        )
        
        if subscribed:
            if not hasattr(context, 'participants'):
                context.participants = set()
            if user_id in context.participants:
                await query.edit_message_text("Вы уже участвовали сегодня!")
                return

            from database import register_participant
            register_participant(user_id)
            await query.edit_message_text("🎉 Вы успешно зарегистрировались на розыгрыш!")
        else:
            keyboard = get_channel_subscription_keyboard(['@channel1', '@channel2'])
            await query.edit_message_text(
                "Чтобы участвовать в розыгрыше, подпишитесь на каналы:\n"
                + "\n".join(['@channel1', '@channel2']) + "\n" + "\n".join(['max_channel_1', 'max_channel_2']),
                reply_markup=keyboard
            )

    elif query.data == "cancel_join":
        await query.edit_message_text("❌ Вы отменили участие.")
    
    elif query.data == "join_lottery":
        await join(query, context)
    
    elif query.data == "user_stats":
        await user_stats_callback(query, context)
    
    elif query.data == "draw_history":
        await draw_history_callback(query, context)
    
    elif query.data == "my_rewards":
        await my_rewards_callback(query, context)
    
    elif query.data == "webapp":
        await webapp_callback(query, context)
    
    elif query.data == "reset_data":
        await reset_data_callback(query, context)
    
    elif query.data == "force_draw":
        await force_draw_callback(query, context)
    
    elif query.data == "bot_stats":
        await bot_stats_callback(query, context)
    
    elif query.data == "all_users":
        await all_users_callback(query, context)
    
    elif query.data == "admin_main":
        keyboard = get_admin_menu()
        await query.edit_message_text("🔧 Админ-панель:", reply_markup=keyboard)
    
    elif query.data == "admin_add_channel":
        await admin_add_channel(query, context)
    
    elif query.data == "admin_manage_channels":
        await admin_manage_channels(query, context)
    
    elif query.data == "admin_add_prize":
        await admin_add_prize(query, context)
    
    elif query.data == "admin_manage_prizes":
        await admin_manage_prizes(query, context)
    
    elif query.data == "admin_auto_draws":
        await admin_auto_draws(query, context)

# === Добавим обработчик для команды добавления канала ===

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Доступ ограничен.")
        return
    
    # Парсим сообщение
    message = update.message.text
    if "|" in message:
        parts = message.split("|")
        if len(parts) >= 2:
            channel_name = parts[0].strip()
            channel_id = parts[1].strip()
            
            add_lottery_channel(channel_name, channel_id)
            await update.message.reply_text(f"✅ Канал '{channel_name}' добавлен!")
        else:
            await update.message.reply_text("❌ Неверный формат. Используйте: Название | ID")
    else:
        await update.message.reply_text("❌ Неверный формат. Используйте: Название | ID")

# === Добавим обработчик для команды добавления приза ===

async def add_prize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Доступ ограничен.")
        return
    
    # Парсим сообщение
    message = update.message.text
    if "|" in message:
        parts = message.split("|")
        if len(parts) >= 2:
            prize_name = parts[0].strip()
            prize_value = parts[1].strip()
            
            add_prize(prize_name, prize_value)
            await update.message.reply_text(f"✅ Приз '{prize_name}' добавлен!")
        else:
            await update.message.reply_text("❌ Неверный формат. Используйте: Название | Значение")
    else:
        await update.message.reply_text("❌ Неверный формат. Используйте: Название | Значение")
