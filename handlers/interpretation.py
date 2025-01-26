"""
Обработчик команды /get_interpretation.
Получает интерпретацию результатов от ChatGPT.
"""

from aiogram import Router, types
from aiogram.filters import Command
from utils.database import get_user_measurements
from openai import AsyncOpenAI
from utils.config import OPENAI_API_KEY, OPENAI_MODEL

router = Router()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_gpt_interpretation(measurements: list) -> str:
    """
    Получает интерпретацию результатов от ChatGPT.
    
    Args:
        measurements: Список измерений пользователя
    
    Returns:
        str: Текст интерпретации
    """
    if not measurements:
        return "Недостаточно данных для анализа."
    
    # Формируем промпт для GPT
    prompt = (
        "Проанализируй следующие измерения психологического состояния человека "
        "и дай рекомендации по улучшению состояния. "
        "Измерения представлены в формате (дата, значение), "
        "где значение от -3 (очень плохо) до +3 (отлично):\n\n"
    )
    
    for timestamp, measurement in measurements:
        prompt += f"{timestamp}: {measurement}\n"
    
    prompt += "\nПожалуйста, проанализируй:\n1. Общую динамику состояния\n2. Возможные паттерны\n3. Дай рекомендации"
    
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Ты - эмпатичный психолог-аналитик, который анализирует данные о психологическом состоянии человека."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Произошла ошибка при получении интерпретации: {str(e)}"

@router.message(Command("get_interpretation"))
async def cmd_interpretation(message: types.Message):
    """
    Обработчик команды /get_interpretation.
    Получает и отправляет интерпретацию результатов.
    """
    # Получаем измерения пользователя
    measurements = await get_user_measurements(message.from_user.id)
    
    if not measurements:
        await message.answer("❌ У вас пока нет измерений для анализа.")
        return
    
    # Отправляем сообщение о начале анализа
    processing_msg = await message.answer("🤔 Анализирую ваши данные...")
    
    # Получаем интерпретацию
    interpretation = await get_gpt_interpretation(measurements)
    
    # Отправляем результат
    await processing_msg.delete()
    await message.answer(
        "📊 Анализ ваших измерений:\n\n" + interpretation,
        parse_mode="Markdown"
    ) 