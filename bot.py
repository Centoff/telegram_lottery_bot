# bot.py

import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers import start, join, draw, stats, history, reset, admin, webapp_handler, check_subscription, add_channel_command, add_prize_command, user_stats_callback, draw_history_callback, my_rewards_callback, webapp_callback, reset_data_callback, force_draw_callback, bot_stats_callback, all_users_callback, button_handler
from inline_buttons import get_join_keyboard, get_channel_subscription_keyboard, get_main_menu, get_admin_menu
from subscription_check import is_subscribed
from database import init_db
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("draw", draw))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("webapp", webapp_handler))
    application.add_handler(CommandHandler("checksub", check_subscription))
    
    # Новые команды для админ-панели
    application.add_handler(CommandHandler("addchannel", add_channel_command))
    application.add_handler(CommandHandler("addprize", add_prize_command))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    # Обработчик текстовых сообщений для добавления каналов и призов
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    await application.run_polling()

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений для добавления каналов и призов"""
    user_id = update.effective_user.id
    
    # Если пользователь админ, проверяем на команды
    if user_id == ADMIN_CHAT_ID:
        message_text = update.message.text
        
        # Проверяем, является ли сообщение командой добавления канала
        if "|" in message_text and len(message_text.split("|")) >= 2:
            # Проверяем формат
            parts = message_text.split("|")
            if len(parts) >= 2:
                # Проверяем, что это команда для добавления
                if update.message.text.startswith("/addchannel") or update.message.text.startswith("/addprize"):
                    pass  # Обработка уже была в соответствующих командах
                else:
                    # Это может быть добавление канала или приза через сообщение
                    await update.message.reply_text("Используйте команды /addchannel или /addprize")

if __name__ == '__main__':
    asyncio.run(main())
