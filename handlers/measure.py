"""
Обработчик команды /measure.
Позволяет пользователю внести новое измерение своего состояния.
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.database import add_measurement
from utils.config import MIN_MEASUREMENT, MAX_MEASUREMENT

router = Router()

class MeasurementState(StatesGroup):
    """Состояния для FSM при измерении состояния."""
    waiting_for_measurement = State()

@router.message(Command("measure"))
async def cmd_measure(message: types.Message, state: FSMContext):
    """
    Обработчик команды /measure.
    Запрашивает у пользователя оценку состояния.
    """
    await state.set_state(MeasurementState.waiting_for_measurement)
    await message.answer(
        "Оцените ваше текущее состояние по шкале от -3 до +3:\n"
        "🔴 -3: Очень плохо\n"
        "🟠 -2: Плохо\n"
        "🟡 -1: Немного плохо\n"
        "⚪️ 0: Нейтрально\n"
        "🟢 +1: Немного хорошо\n"
        "🔵 +2: Хорошо\n"
        "🟣 +3: Отлично"
    )

@router.message(MeasurementState.waiting_for_measurement)
async def process_measurement(message: types.Message, state: FSMContext):
    """
    Обработчик ввода оценки состояния.
    Проверяет корректность ввода и сохраняет результат.
    """
    try:
        measurement = int(message.text)
        if MIN_MEASUREMENT <= measurement <= MAX_MEASUREMENT:
            await add_measurement(message.from_user.id, measurement)
            await state.clear()
            await message.answer("✅ Спасибо! Ваша оценка сохранена.")
        else:
            await message.answer(f"❌ Пожалуйста, введите число от {MIN_MEASUREMENT} до {MAX_MEASUREMENT}")
    except ValueError:
        await message.answer("❌ Пожалуйста, введите целое число") 