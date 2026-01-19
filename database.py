import sqlite3
import os
import hashlib
import secrets


def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect('data/calories.db')
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_token TEXT
        )
    ''')

    # Создаем таблицу для истории расчетов с user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            goal TEXT NOT NULL,
            activity TEXT NOT NULL,
            bmr REAL NOT NULL,
            tdee REAL NOT NULL,
            target_calories REAL NOT NULL,
            protein_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            carbs_g REAL NOT NULL,
            protein_percent REAL NOT NULL,
            fat_percent REAL NOT NULL,
            carbs_percent REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("База данных успешно инициализирована!")


def get_db_connection():
    conn = sqlite3.connect('data/calories.db')
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_session_token():
    """Создание токена сессии"""
    return secrets.token_hex(32)