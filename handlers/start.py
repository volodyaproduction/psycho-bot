"""
Обработчик команды /start.
Регистрирует нового пользователя и отправляет приветственное сообщение.
"""

from aiogram import Router, types
from aiogram.filters import Command
from utils.database import add_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Регистрирует пользователя и отправляет приветственное сообщение.
    """
    # Добавляем пользователя в базу данных
    await add_user(message.from_user.dict())
    
    # Формируем приветственное сообщение
    welcome_text = (
        "👋 Привет! Я бот для отслеживания психологического состояния.\n\n"
        "Каждый день я буду просить вас оценить ваше состояние по шкале от -3 до +3:\n"
        "🔴 -3: Очень плохо\n"
        "🟠 -2: Плохо\n"
        "🟡 -1: Немного плохо\n"
        "⚪️ 0: Нейтрально\n"
        "🟢 +1: Немного хорошо\n"
        "🔵 +2: Хорошо\n"
        "🟣 +3: Отлично\n\n"
        "Доступные команды:\n"
        "/measure - Внести новое измерение\n"
        "/plot - Построить график измерений\n"
        "/get_interpretation - Получить анализ состояния"
    )
    
    await message.answer(welcome_text) 