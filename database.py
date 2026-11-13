# database.py

import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    
    # Таблица участников
    c.execute('''CREATE TABLE IF NOT EXISTS participants
                 (user_id INTEGER PRIMARY KEY, join_date TEXT, last_draw_date TEXT)''')
    
    # Таблица розыгрышей
    c.execute('''CREATE TABLE IF NOT EXISTS draws
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, winner_id INTEGER, draw_date TEXT, prize TEXT, channel TEXT, draw_type TEXT)''')
    
    # Таблица статистики пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                 (user_id INTEGER PRIMARY KEY, total_joins INTEGER, total_wins INTEGER, last_join_date TEXT)''')
    
    # Таблица наград
    c.execute('''CREATE TABLE IF NOT EXISTS rewards
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, reward_type TEXT, reward_value TEXT, date TEXT)''')
    
    # Таблица каналов для розыгрышей
    c.execute('''CREATE TABLE IF NOT EXISTS lottery_channels
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_name TEXT, channel_id TEXT, is_active BOOLEAN DEFAULT 1, created_date TEXT)''')
    
    # Таблица призов
    c.execute('''CREATE TABLE IF NOT EXISTS prizes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, prize_name TEXT, prize_value TEXT, is_active BOOLEAN DEFAULT 1, created_date TEXT, usage_count INTEGER DEFAULT 0)''')
    
    # Таблица автоматических розыгрышей
    c.execute('''CREATE TABLE IF NOT EXISTS auto_draws
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, draw_datetime TEXT, prize_id INTEGER, is_active BOOLEAN DEFAULT 1, executed BOOLEAN DEFAULT 0, created_date TEXT)''')
    
    conn.commit()
    conn.close()

def register_participant(user_id: int):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Проверяем существование пользователя
        c.execute("SELECT user_id FROM participants WHERE user_id=?", (user_id,))
        if not c.fetchone():
            c.execute("INSERT OR REPLACE INTO participants (user_id, join_date) VALUES (?, ?)", (user_id, now))
        else:
            c.execute("UPDATE participants SET join_date=? WHERE user_id=?", (now, user_id))
            
        # Обновляем статистику
        c.execute("INSERT OR REPLACE INTO user_stats (user_id, total_joins, total_wins, last_join_date) VALUES (?, 1, 0, ?)", (user_id, now))
        conn.commit()
    except Exception as e:
        print(f"Ошибка регистрации участника: {e}")
    finally:
        conn.close()

def has_participated_today(user_id: int) -> bool:
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT join_date FROM participants WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()

    if not result:
        return False

    last_join = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
    return datetime.now() - last_join < timedelta(days=1)

def get_participants():
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM participants")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def save_draw(winner_id: int, prize: str = "1000₽", channel: str = "main", draw_type: str = "manual"):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Сохраняем розыгрыш
    c.execute("INSERT INTO draws (winner_id, draw_date, prize, channel, draw_type) VALUES (?, ?, ?, ?, ?)", 
              (winner_id, now, prize, channel, draw_type))
    
    # Обновляем статистику победителя
    c.execute("UPDATE user_stats SET total_wins = total_wins + 1 WHERE user_id=?", (winner_id,))
    conn.commit()
    conn.close()

def get_draw_history(limit=5):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT winner_id, draw_date, prize, channel FROM draws ORDER BY draw_date DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_stats(user_id: int):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT total_joins, total_wins, last_join_date FROM user_stats WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {'joins': result[0], 'wins': result[1], 'last_join': result[2]}
    return {'joins': 0, 'wins': 0, 'last_join': None}

def get_user_joins(user_id: int):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT join_date FROM participants WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_last_draw_date(user_id: int):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE participants SET last_draw_date=? WHERE user_id=?", (now, user_id))
    conn.commit()
    conn.close()

def get_user_rewards(user_id: int):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT reward_type, reward_value, date FROM rewards WHERE user_id=? ORDER BY date DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_reward(user_id: int, reward_type: str, reward_value: str):
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO rewards (user_id, reward_type, reward_value, date) VALUES (?, ?, ?, ?)", 
              (user_id, reward_type, reward_value, now))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM participants")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def get_total_draws():
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM draws")
    count = c.fetchone()[0]
    conn.close()
    return count

# === Новые функции для админ-панели ===

def add_lottery_channel(channel_name: str, channel_id: str):
    """Добавить канал для розыгрышей"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO lottery_channels (channel_name, channel_id, created_date) VALUES (?, ?, ?)", 
              (channel_name, channel_id, now))
    conn.commit()
    conn.close()

def get_lottery_channels():
    """Получить все каналы для розыгрышей"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT id, channel_name, channel_id, is_active FROM lottery_channels ORDER BY created_date DESC")
    channels = c.fetchall()
    conn.close()
    return channels

def update_lottery_channel(channel_id: int, is_active: bool):
    """Обновить статус канала"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("UPDATE lottery_channels SET is_active=? WHERE id=?", (is_active, channel_id))
    conn.commit()
    conn.close()

def delete_lottery_channel(channel_id: int):
    """Удалить канал"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("DELETE FROM lottery_channels WHERE id=?", (channel_id,))
    conn.commit()
    conn.close()

def add_prize(prize_name: str, prize_value: str):
    """Добавить приз"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO prizes (prize_name, prize_value, created_date) VALUES (?, ?, ?)", 
              (prize_name, prize_value, now))
    conn.commit()
    conn.close()

def get_prizes():
    """Получить все призы"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT id, prize_name, prize_value, is_active, usage_count FROM prizes ORDER BY created_date DESC")
    prizes = c.fetchall()
    conn.close()
    return prizes

def update_prize(prize_id: int, is_active: bool):
    """Обновить статус приза"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("UPDATE prizes SET is_active=? WHERE id=?", (is_active, prize_id))
    conn.commit()
    conn.close()

def delete_prize(prize_id: int):
    """Удалить приз"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("DELETE FROM prizes WHERE id=?", (prize_id,))
    conn.commit()
    conn.close()

def get_active_prizes():
    """Получить активные призы"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT id, prize_name, prize_value FROM prizes WHERE is_active=1 ORDER BY created_date DESC")
    prizes = c.fetchall()
    conn.close()
    return prizes

def add_auto_draw(draw_datetime: str, prize_id: int):
    """Добавить автоматический розыгрыш"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO auto_draws (draw_datetime, prize_id, created_date) VALUES (?, ?, ?)", 
              (draw_datetime, prize_id, now))
    conn.commit()
    conn.close()

def get_auto_draws():
    """Получить все автоматические розыгрыши"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("SELECT id, draw_datetime, prize_id, is_active, executed FROM auto_draws ORDER BY draw_datetime DESC")
    draws = c.fetchall()
    conn.close()
    return draws

def update_auto_draw(draw_id: int, is_active: bool):
    """Обновить статус автоматического розыгрыша"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("UPDATE auto_draws SET is_active=? WHERE id=?", (is_active, draw_id))
    conn.commit()
    conn.close()

def mark_auto_draw_executed(draw_id: int):
    """Отметить автоматический розыгрыш как выполненный"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("UPDATE auto_draws SET executed=1 WHERE id=?", (draw_id,))
    conn.commit()
    conn.close()

def increment_prize_usage(prize_id: int):
    """Увеличить счетчик использования приза"""
    conn = sqlite3.connect('lottery.db')
    c = conn.cursor()
    c.execute("UPDATE prizes SET usage_count=usage_count+1 WHERE id=?", (prize_id,))
    conn.commit()
    conn.close()
