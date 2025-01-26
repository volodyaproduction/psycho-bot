"""
Основной файл бота.
Инициализирует бота и запускает его.
"""

import asyncio
import logging
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from handlers import start, measure, plot, interpretation, load_data
from utils.database import init_db
from utils.config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Инициализация бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start.router)
dp.include_router(measure.router)
dp.include_router(plot.router)
dp.include_router(interpretation.router)
dp.include_router(load_data.router)

async def main():
    """
    Основная функция запуска бота.
    Инициализирует базу данных и запускает бота.
    """
    # Инициализация базы данных
    await init_db()
    
    # Удаляем все обновления, накопившиеся за время отключения
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 