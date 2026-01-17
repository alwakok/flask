import sqlite3
import os


def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect('data/calories.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS calculations')
    
    cursor.execute('''
        CREATE TABLE calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            carbs_percent REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("База данных успешно инициализирована!")


def get_db_connection():
    conn = sqlite3.connect('data/calories.db')
    conn.row_factory = sqlite3.Row

    return conn
