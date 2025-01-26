"""
Конфигурационный файл проекта.
Содержит все необходимые настройки и переменные окружения.
"""

import os

# Токены и ключи API
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Настройки OpenAI
OPENAI_MODEL = "gpt-4-turbo-preview"  # Модель GPT для интерпретации результатов

# Настройки базы данных
DB_NAME = "psycho_bot.db"

# Константы для измерений
MIN_MEASUREMENT = -3
MAX_MEASUREMENT = 3

# Временные интервалы для напоминаний (в часах)
REMINDER_INTERVAL = 24 