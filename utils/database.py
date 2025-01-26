"""
Модуль для работы с базой данных.
Содержит функции для создания таблиц, добавления и получения данных.
"""

import aiosqlite
from datetime import datetime
import pytz
from .config import DB_NAME

# SQL запросы для создания таблиц
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    is_bot BOOLEAN,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    language_code TEXT
)
"""

CREATE_MEASUREMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp DATETIME,  -- Время хранится в UTC
    measurement INTEGER,
    state TEXT,
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""

def to_utc(dt: datetime) -> datetime:
    """
    Преобразует datetime в UTC.
    Если время не содержит информацию о часовом поясе, считает его локальным.
    """
    if dt.tzinfo is None:
        # Если время без часового пояса, считаем его локальным
        local_tz = pytz.timezone('UTC')
        dt = local_tz.localize(dt)
    return dt.astimezone(pytz.UTC)

async def init_db():
    """Инициализация базы данных и создание таблиц."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(CREATE_USERS_TABLE)
        await db.execute(CREATE_MEASUREMENTS_TABLE)
        await db.commit()

async def add_user(user_data: dict):
    """Добавление нового пользователя в базу данных."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (id, is_bot, first_name, last_name, username, language_code)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_data['id'],
                user_data.get('is_bot', False),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('username'),
                user_data.get('language_code')
            )
        )
        await db.commit()

async def add_measurement(user_id: int, measurement: int, state: str = None, error_message: str = None, timestamp: datetime = None):
    """
    Добавление нового измерения в базу данных.
    
    Args:
        user_id: ID пользователя
        measurement: Значение измерения
        state: Состояние (опционально)
        error_message: Сообщение об ошибке (опционально)
        timestamp: Время измерения (опционально, по умолчанию текущее время в UTC)
    """
    if timestamp is None:
        # Если время не указано, берем текущее время в UTC
        timestamp = datetime.now(pytz.UTC)
    else:
        # Если время указано, преобразуем его в UTC
        timestamp = to_utc(timestamp)
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO measurements (user_id, timestamp, measurement, state, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, timestamp.isoformat(), measurement, state, error_message)
        )
        await db.commit()

async def get_user_measurements(user_id: int, days: int = None):
    """
    Получение измерений пользователя за определенный период.
    Все временные метки в UTC.
    """
    query = """
        SELECT timestamp, measurement
        FROM measurements
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """
    if days:
        query = """
            SELECT timestamp, measurement
            FROM measurements
            WHERE user_id = ?
            AND timestamp >= datetime('now', ?, 'utc')
            ORDER BY timestamp DESC
        """
    
    async with aiosqlite.connect(DB_NAME) as db:
        if days:
            cursor = await db.execute(query, (user_id, f'-{days} days'))
        else:
            cursor = await db.execute(query, (user_id,))
        return await cursor.fetchall() 