# webapp.py

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/lottery')
def lottery_api():
    # Пример API для WebApp
    data = {
        "message": "Добро пожаловать в розыгрыш!",
        "channels": ["@channel1", "@channel2"],
        "prize": "1000₽",
        "users_online": 1567,
        "active_draws": 3
    }
    return jsonify(data)

@app.route('/api/user/<int:user_id>')
def user_api(user_id):
    # Пример данных пользователя
    data = {
        "user_id": user_id,
        "joins": 25,
        "wins": 3,
        "level": "⭐ Эксперт",
        "rewards": [
            {"type": "Приз", "value": "1000₽", "date": "2024-01-15"},
            {"type": "Награда", "value": "Telegram Premium", "date": "2024-01-10"}
        ]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
